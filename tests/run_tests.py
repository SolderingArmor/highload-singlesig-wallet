#!/usr/bin/env python3

# ==============================================================================
# 
import freeton_utils
from   freeton_utils import *
import binascii
import unittest
import time
import sys
from   pathlib import Path
from   pprint import pprint
from   contract_HighloadSinglesig import HighloadSinglesig

SERVER_ADDRESS = "https://net.ton.dev"

# ==============================================================================
#
def getClient():
    return TonClient(config=ClientConfig(network=NetworkConfig(server_address=SERVER_ADDRESS)))

# ==============================================================================
# 
# Parse arguments and then clear them because UnitTest will @#$~!
for _, arg in enumerate(sys.argv[1:]):
    if arg == "--disable-giver":
        
        freeton_utils.USE_GIVER = False
        sys.argv.remove(arg)

    if arg == "--throw":
        
        freeton_utils.THROW = True
        sys.argv.remove(arg)

    if arg.startswith("http"):
        
        SERVER_ADDRESS = arg
        sys.argv.remove(arg)

    if arg.startswith("--msig-giver"):
        
        freeton_utils.MSIG_GIVER = arg[13:]
        sys.argv.remove(arg)

# ==============================================================================
# EXIT CODE FOR SINGLE-MESSAGE OPERATIONS
# we know we have only 1 internal message, that's why this wrapper has no filters
def _getAbiArray():
    return ["../bin/HighloadSinglesig.abi.json"]

def _getExitCode(msgIdArray):
    abiArray     = _getAbiArray()
    msgArray     = unwrapMessages(getClient(), msgIdArray, abiArray)
    if msgArray != "":
        realExitCode = msgArray[0]["TX_DETAILS"]["compute"]["exit_code"]
    else:
        realExitCode = -1
    return realExitCode   

# ==============================================================================
# 
class Test_01_DeployAndTransfer(unittest.TestCase):

    hsig1 = HighloadSinglesig(tonClient=getClient())
    hsig2 = HighloadSinglesig(tonClient=getClient())
    hsig3 = HighloadSinglesig(tonClient=getClient())

    def test_0(self):
        print("\n\n----------------------------------------------------------------------")
        print("Running:", self.__class__.__name__)

    # 1. Giver
    def test_1(self):
        giverGive(getClient(), self.hsig1.ADDRESS, TON * 10)
        giverGive(getClient(), self.hsig2.ADDRESS, TON * 10)
        giverGive(getClient(), self.hsig3.ADDRESS, TON * 10)

    # 2. Deploy multisig
    def test_2(self):
        result = self.hsig1.deploy()
        self.assertEqual(result[1]["errorCode"], 0)
        result = self.hsig2.deploy()
        self.assertEqual(result[1]["errorCode"], 0)
        result = self.hsig3.deploy()
        self.assertEqual(result[1]["errorCode"], 0)

    # 3. Get info
    def test_3(self):

        result = self.hsig1.sendTransaction(addressDest=self.hsig2.ADDRESS, value=TON, bounce=False, flags=1, payload="")
        self.assertEqual(result[1]["errorCode"], 0)

    # 5. Cleanup
    def test_5(self):
        result = self.hsig1.destroy(addressDest = freeton_utils.giverGetAddress())
        self.assertEqual(result[1]["errorCode"], 0)
        result = self.hsig2.destroy(addressDest = freeton_utils.giverGetAddress())
        self.assertEqual(result[1]["errorCode"], 0)
        result = self.hsig3.destroy(addressDest = freeton_utils.giverGetAddress())
        self.assertEqual(result[1]["errorCode"], 0)

# ==============================================================================
# 
unittest.main()
