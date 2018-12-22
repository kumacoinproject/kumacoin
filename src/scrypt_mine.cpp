#include <stdlib.h>
#include <stdint.h>
// #include <xmmintrin.h>

#include "scrypt_mine.h"
#include "pbkdf2.h"

#include "util.h"
#include "net.h"

extern bool fShutdown;
extern bool fGenerateBitcoins;

extern CBlockIndex* pindexBest;
extern uint32_t nTransactionsUpdated;

