#!/usr/bin/env python3

# ==============================================================================
# 
import freeton_utils
from   freeton_utils import *
from   contract_HighloadSinglesig import HighloadSinglesig
from   pprint import pprint

# ==============================================================================
#
def getClient():
    endpoints = ["http://localhost"]
    config    = NetworkConfig(endpoints=endpoints)
    return TonClient(config=ClientConfig(network=config), is_core_async=True)

print(getAbi("../bin/HighloadSinglesig.abi.json").value)

# ==============================================================================
# 
# Create Wallet
hsig1 = HighloadSinglesig(tonClient=getClient())
hsig2 = HighloadSinglesig(tonClient=getClient())

# Giver for TON OS SE
giverGive(tonClient=getClient(), contractAddress=hsig1.ADDRESS, amountTons=TON*5)
giverGive(tonClient=getClient(), contractAddress=hsig2.ADDRESS, amountTons=TON*5)

hsig1.deploy()
hsig2.deploy()

result = hsig1.sendTransaction(addressDest=hsig2.ADDRESS, value=TON, bounce=False, flags=1, payload="")
print("Result:", result[1]["errorCode"])
