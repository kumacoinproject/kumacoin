![](https://raw.githubusercontent.com/kumacoinproject/kumacoin/master/src/qt/res/images/splash.png)
# Kumacoinについて
Kumacoinは日本で作られたP2P型の暗号通貨です。（2014年4月29日公開）<br>
暗号通貨とは、Bitcoin(ビットコイン)などと同様にP2Pネットワークで取引され、管理者が存在しない電子通貨の一種です。<br>
KumacoinはQuarkと呼ばれるCPUが強いアルゴリズムを採用しているのが特徴で、<br>
PoW+PoSを採用し、マシンパワーを使ってのコイン採掘に加え、ウォレットを起動してコインを持ってるだけでもネットワーク貢献として所持金が増えていきます。

***

### Specifications
```
アルゴリスム：Quark
プレマイン：無し 
PoS報酬： 
　1 - 1,051,200 blockまで 20%
　以降、1,051,200 block毎に 15% -> 10% -> 5% まで減少（最終的に5%で固定）　

PoW報酬： 
　1 - 100,000 blockまで 1 - 5,000KUMA のランダムブロック発見報酬 
　100,000 block以降     1 - 2,000KUMA のランダムブロック発見報酬 
　以降 1,051,200 block毎に報酬の上限を半減させていく 

PoSマイニングの最低要件：5 coin age以上 
コインの成熟期間：40日 
ブロック発見間隔：90秒間隔 
難易度変更間隔：1blockごと

Port: 7586
Testnet: 17586 
RPC Port: 7585
Testnet RPC: 17585
```

***

### Download
ウォレット<br>
[Kumacoin-Qt Wallet for Windows](https://drive.google.com/folderview?id=0B16eh4lTx_uAQm1BSTU3RzBITHc&usp=sharing) （2016/2/27 Wallet更新）<br><br>
マイニングソフト<br>
[Mining Software for CPU cpuminer](http://sourceforge.net/projects/philosopherstone/files/QRK/)<br>
[Mining Software for GPU (AMD) sph-sgminer](https://bitcointalk.org/index.php?topic=475795.0)<br>
[Mining Software for GPU (nVidia) ccminer](https://github.com/cbuchner1/ccminer/releases)<br>
***

### kumacoin.conf設定例
C:\Users\[UserName]\AppData\Roaming\Kumacoinのフォルダー内にkumacoin.confを作成し、<br>
下記の内容を記述してください。
```
rpcallowip=127.0.0.1
rpcuser=username（任意）
rpcpassword=password（任意）
maxconnections=100
server=1
```

***

### Pool
LA pool: <br>
* http://kuma.xau.jp/<br>
* http://pool2.xau.jp/<br>

kuma MD pool：<br>
* http://kuma.mona-dns.info/<br>

***

### EXCHANGES（取引所）
* <S>AllCoin.com</S><br>
* [もなとれ](https://monatr.jp/trade/kuma_mona)<br>
* [MonacoEX](https://trade.monaco-ex.org/)

***

### 更新履歴
```
・2016/02/27 kumacoin-qt-20160227-18.zip Wallet更新
　　チェックポイント追加, "Checkpoint is too old..."の警告表示を削除
・2015/05/03 kumacoin-qt-20150503-19.zip Wallet更新
　　チェックポイント追加
・2014/09/17 kumacoin-qt-20140917-21.zip Wallet更新
　　初期ノードにプールのIPを追加
・2014/09/13 kumacoin-qt-20140913-20.zip Wallet更新
　　staking optionが有効にならないの不具合を修正
・2014/08/17 kumacoin-qt-20140817-21.zip Wallet更新
　　PoSとPoWのDiffが連動して、異常にDiffが高くなる問題を修正
　　9万ブロックで切り替え
・2014/05/29 kumacoin-qt-20140529-23.zip Wallet更新
　　Stakingアイコン追加, getstakinginfoコマンドに対応
・2014/05/20 kumacoin-qt-20140520-00.zip Wallet更新
　　「QRコードの表示」時にbitcoinと表示されてしまう問題を修正
・2014/05/06 kumacoin-qt-20140506-21.zip Wallet更新
　　block生成問題修正, DigiShieldへの変更, ブロック生成間隔変更（128秒→90秒）
・2014/04/29 公開
```

***

### Contact
kumacoinproject@gmail.com