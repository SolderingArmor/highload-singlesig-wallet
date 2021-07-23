#!/usr/bin/env python3

# ==============================================================================
#
import freeton_utils
from   freeton_utils import *

class HighloadSinglesig(object):
    def __init__(self, tonClient: TonClient, signer: Signer = None):
        self.SIGNER      = generateSigner() if signer is None else signer
        self.TONCLIENT   = tonClient
        self.ABI         = "../bin/HighloadSinglesig.abi.json"
        self.TVC         = "../bin/HighloadSinglesig.tvc"
        self.CONSTRUCTOR = {}
        self.INITDATA    = {}
        self.PUBKEY      = self.SIGNER.keys.public
        self.ADDRESS     = getAddress(abiPath=self.ABI, tvcPath=self.TVC, signer=self.SIGNER, initialPubkey=self.PUBKEY, initialData=self.INITDATA)

    def deploy(self):
        result = deployContract(tonClient=self.TONCLIENT, abiPath=self.ABI, tvcPath=self.TVC, constructorInput=self.CONSTRUCTOR, initialData=self.INITDATA, signer=self.SIGNER, initialPubkey=self.PUBKEY)
        return result
    
    def _call(self, functionName, functionParams, signer):
        result = callFunction(tonClient=self.TONCLIENT, abiPath=self.ABI, contractAddress=self.ADDRESS, functionName=functionName, functionParams=functionParams, signer=signer)
        return result

    def _run(self, functionName, functionParams):
        result = runFunction(tonClient=self.TONCLIENT, abiPath=self.ABI, contractAddress=self.ADDRESS, functionName=functionName, functionParams=functionParams)
        return result

    # ========================================
    #
    def sendTransaction(self, addressDest:str, value:int, bounce:bool, flags:int, payload:str):
        result = self._call(functionName="sendTransaction", functionParams={"dest":addressDest, "value":value, "bounce":bounce, "flags":flags, "payload":payload}, signer=self.SIGNER)
        return result

    def destroy(self, addressDest):
        result = self._call(functionName="sendTransaction", functionParams={"dest":addressDest, "value":0, "bounce":False, "flags":128+32, "payload":""}, signer=self.SIGNER)
        return result

    # ========================================
    #
    def getMessages(self):
        result = self._run(functionName="getMessages", functionParams={})
        return result
    

# ==============================================================================
# 
