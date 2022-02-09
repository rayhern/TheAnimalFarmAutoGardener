from web3 import Web3
from utils import wei2eth, eth2wei, to_checksum, read_json_file, nonce
import traceback
import time
from decimal import Decimal
import logging

"""
    https://theanimal.farm - Auto Gardener
    
    Garden class to control the garden.
"""

ANIMAL_FARM_GARDEN_ABI_FILE = "./abis/Garden.json"
ANIMAL_FARM_GARDEN_ADDRESS = "0x685BFDd3C2937744c13d7De0821c83191E3027FF"

FARMING_PHRASES = [
    'Running the tractor...', 'It ain\'t much but it\'s honest work...', 
    'Spreading the seeds...', 'Feeding the pigs...', 'Walking the dogs...',
    'Milking the cows...']
    

class Garden:
    def __init__(self, private_key, txn_timeout=120, gas_price=30, rpc_host="https://bsc-dataseed.binance.org:443"):
        self.private_key = private_key
        self.txn_timeout = txn_timeout
        self.gas_price = gas_price
        self.rpc_host = rpc_host
        # Initialize web3, and load the smart contract objects.
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_host))
        self.account = self.w3.eth.account.privateKeyToAccount(self.private_key)
        self.address = self.account.address
        self.w3.eth.default_account = self.address
        # Load uniswap router contract
        self.garden_contract = self.w3.eth.contract(
            to_checksum(ANIMAL_FARM_GARDEN_ADDRESS), 
            abi=read_json_file(ANIMAL_FARM_GARDEN_ABI_FILE))
        self.seeds_per_plant = None
    
    def get_seeds_per_plant(self):
        if not self.seeds_per_plant:
            try:
                self.seeds_per_plant = self.garden_contract.functions.SEEDS_TO_GROW_1PLANT().call()
            except:
                self.seeds_per_plant = None
                logging.debug(traceback.format_exc())
        return self.seeds_per_plant
    
    def get_user_seeds(self, address):
        return self.garden_contract.functions.getUserSeeds(address).call()
    
    def get_my_seeds(self):
        return self.garden_contract.functions.getMySeeds().call()
    
    def get_my_plants(self):
        return self.garden_contract.functions.getMyPlants().call()
    
    def get_balance(self):
        return self.garden_contract.functions.getBalance().call()
    
    def sell_seeds_for_lp(self, max_tries=1):
        txn_receipt = None
        for _ in range(max_tries):
            try:
                txn = self.garden_contract.functions.sellSeeds().buildTransaction({
                    {"gasPrice": eth2wei(self.gas_price, "gwei"), 
                     "nonce": nonce()}
                })
                signed_txn = self.w3.eth.account.sign_transaction(txn, self.private_key)
                txn = self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)
                txn_receipt = self.w3.eth.waitForTransactionReceipt(txn)
                if txn_receipt and "status" in txn_receipt and txn_receipt["status"] == 1: 
                    logging.info('Sold seeds successfully!')
                    break
                else:
                    logging.info('Could not sell seeds.')
                    logging.debug(txn_receipt)
                    time.sleep(10)
            except:
                logging.debug(traceback.format_exc())
                time.sleep(10)
        return txn_receipt
    
    def plant_seeds(self, max_tries=1):
        txn_receipt = None
        for _ in range(max_tries):
            try:
                txn = self.garden_contract.functions.plantSeeds(self.address).buildTransaction({
                    {"gasPrice": eth2wei(self.gas_price, "gwei"), 
                     "nonce": nonce()}
                })
                signed_txn = self.w3.eth.account.sign_transaction(txn, self.private_key)
                txn = self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)
                txn_receipt = self.w3.eth.waitForTransactionReceipt(txn)
                if txn_receipt and "status" in txn_receipt and txn_receipt["status"] == 1: 
                    logging.info('Planted seeds successfully!')
                    break
                else:
                    logging.info('Could not sell seeds.')
                    logging.debug(txn_receipt)
                    time.sleep(10)
            except:
                logging.debug(traceback.format_exc())
                time.sleep(10)
        return txn_receipt
    
    def calculate_seed_sell(self, seeds):
        return self.garden_contract.functions.calculateSeedSell(seeds).call()
    
