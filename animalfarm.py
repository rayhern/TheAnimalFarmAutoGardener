from web3 import Web3
from utils import *
import traceback
import time
from decimal import Decimal
import logging
import json
import asyncio
import threading

"""
    https://theanimal.farm - Auto Gardener
    
    Garden class to control the garden.
    
# Pig pools
2022-02-09 20:58:06,584: 0 - PIGS - 0x3A4C15F96B3b058ab3Fb5FAf1440Cc19E7AE07ce
2022-02-09 20:58:07,189: 1 - WBNB<>BUSD - 0x58F876857a02D6762E0101bb5C46A8c1ED44Dc16
2022-02-09 20:58:07,775: 2 - USDT<>BUSD - 0x7EFaEf62fDdCCa950418312c6C91Aef321375A00
2022-02-09 20:58:08,373: 3 - USDC<>BUSD - 0x2354ef4DF11afacb85a5C7f98B624072ECcddbB1
2022-02-09 20:58:09,146: 4 - TUSD<>BUSD - 0x2E28b9B74D6d99D4697e913b82B41ef1CAC51c6C
2022-02-09 20:58:09,715: 5 - DAI<>BUSD - 0x66FDB2eCCfB58cF098eaa419e5EfDe841368e489
2022-02-09 20:58:10,309: 6 - ETH<>BTCB - 0xD171B26E4484402de70e3Ea256bE5A2630d7e88D
2022-02-09 20:58:10,901: 7 - ETH<>WBNB - 0x74E4716E431f45807DCF19f284c7aA99F18a4fbc
2022-02-09 20:58:11,653: 8 - BTCB<>WBNB - 0x61EB789d75A95CAa3fF50ed7E47b96c132fEc082
2022-02-09 20:58:12,237: 9 - ETH<>USDC - 0xEa26B78255Df2bBC31C1eBf60010D78670185bD0
2022-02-09 20:58:12,854: 10 - BTCB<>BUSD - 0xF45cd219aEF8618A92BAa7aD848364a158a24F33
2022-02-09 20:58:13,484: 11 - USDT<>WBNB - 0x16b9a82891338f9bA80E2D6970FddA79D1eb0daE
2022-02-09 20:58:14,135: 12 - Cake<>BUSD - 0x804678fa97d91B974ec2af3c843270886528a9E6
2022-02-09 20:58:14,719: 13 - Cake<>USDT - 0xA39Af17CE4a8eb807E076805Da1e2B8EA7D0755b
2022-02-09 20:58:15,322: 14 - Cake<>WBNB - 0x0eD7e52944161450477ee417DE9Cd3a859b14fD0
2022-02-09 20:58:15,913: 15 - WBNB<>BELT - 0xF3Bc6FC080ffCC30d93dF48BFA2aA14b869554bb
2022-02-09 20:58:16,498: 16 - DOT<>WBNB - 0xDd5bAd8f8b360d76d12FdA230F8BAF42fe0022CF
2022-02-09 20:58:17,076: 17 - WBNB<>LINK - 0x824eb9faDFb377394430d2744fa7C42916DE3eCe
2022-02-09 20:58:17,267: 18 - WBNB - 0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c
2022-02-09 20:58:17,462: 19 - BUSD - 0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56
2022-02-09 20:58:17,658: 20 - ETH - 0x2170Ed0880ac9A755fd29B2688956BD959F933F8
2022-02-09 20:58:17,853: 21 - Cake - 0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82
2022-02-09 20:58:18,051: 22 - BTCB - 0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c

# Dog pools
2022-02-09 20:58:18,771: 0 - DOGS<>BUSD - 0x70f01321CB37A37D4b095bBda7E4BF46E1C9F1F9
2022-02-09 20:58:19,391: 1 - WBNB<>DOGS - 0x761C695d5EF6e8eFBCF5FaE00035a589eD164774
2022-02-09 20:58:20,021: 2 - DRIP<>BUSD - 0xa0feB3c81A36E885B6608DF7f0ff69dB97491b58
2022-02-09 20:58:20,216: 3 - DOGS - 0xDBdC73B95cC0D5e7E99dC95523045Fc8d075Fb9e


    
"""

ANIMAL_FARM_GARDEN_ABI_FILE = "./abis/Garden.json"
ANIMAL_FARM_GARDEN_PAIR_ABI_FILE = "./abis/Pair.json"
ANIMAL_FARM_MASTER_CHEF_PIGS_ABI_FILE = "./abis/MasterChefPigs.json"
ANIMAL_FARM_MASTER_CHEF_DOGS_ABI_FILE = "./abis/MasterChefDogs.json"
ERC20_ABI_FILE = "./abis/ERC20.json"

ANIMAL_FARM_GARDEN_ADDRESS = "0x685BFDd3C2937744c13d7De0821c83191E3027FF"
ANIMAL_FARM_GARDEN_PAIR_ADDRESS = "0xa0feB3c81A36E885B6608DF7f0ff69dB97491b58"
ANIMAL_FARM_DRIP_PAIR_ADDRESS = "0xa0feB3c81A36E885B6608DF7f0ff69dB97491b58"

# 0xe5d9c56B271bc7820Eee01BCC99E593e3e7bAD44
ANIMAL_FARM_DOGS_ADDRESS = "0xe5d9c56B271bc7820Eee01BCC99E593e3e7bAD44"
ANIMAL_FARM_PIGS_ADDRESS = "0x932C5E1709a6895Bc455E799B03F43D3a8FfbD9A"

DOGS_TOKEN_ADDRESS = "0xDBdC73B95cC0D5e7E99dC95523045Fc8d075Fb9e"
PIGS_TOKEN_ADDRESS = "0x3A4C15F96B3b058ab3Fb5FAf1440Cc19E7AE07ce"

FARMING_PHRASES = [
    'Running the tractor...', 'It ain\'t much but it\'s honest work...', 
    'Spreading the seeds...', 'Feeding the pigs...', 'Walking the dogs...',
    'Milking the cows...']
    

class AnimalFarmClient:
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
        self.garden_lp_contract = self.w3.eth.contract(
            to_checksum(ANIMAL_FARM_GARDEN_PAIR_ADDRESS), 
            abi=read_json_file(ANIMAL_FARM_GARDEN_PAIR_ABI_FILE))
        self.pair_abi = read_json_file(ANIMAL_FARM_GARDEN_PAIR_ABI_FILE)
        self.pigs_abi = read_json_file(ANIMAL_FARM_MASTER_CHEF_PIGS_ABI_FILE)
        self.dogs_abi = read_json_file(ANIMAL_FARM_MASTER_CHEF_DOGS_ABI_FILE)
        self.erc20_abi = read_json_file(ERC20_ABI_FILE)
        self.seeds_per_plant = None
        # info about DRIP<>BUSD lp pool.
        self.drip_busd = {
            "price": 0,
            "busd_price": 0,
            "busd_reserve": 0,
            "drip_price": 0,
            "drip_reserve": 0,
            "supply": 0,
            "lp_ratio": Decimal(0.0)
        }

        # self.async_thread = threading.Thread(target=self.event_thread)
        # self.async_thread.start()
        
    def event_thread(self):
        contract = self.get_pool_contract(pigs_or_dogs="pigs")
        logging.info('entered thread.')
        while True:
            try:
                for event in contract.events.SetFarmEndBlock.createFilter(fromBlock='latest').get_new_entries():
                    logging.info(event)
                time.sleep(5)
            except:
                logging.info(traceback.format_exc())
                time.sleep(2)
            time.sleep(5)
            
    def handle_event(self, event):
        """2022-02-07 17:14:56,554: AttributeDict({'args': AttributeDict({'tokenId': 118733, 'auctionId': 709987, 'totalPrice': 48000000000000000000, 'winner': '0x5E1af805f2c10dCE86bb610BADd6445F92921163'}), 'event': 'AuctionSuccessful', 'logIndex': 24, 'transactionIndex': 2, 'transactionHash': HexBytes('0x6c5f995d12b2a56df30616e453351b8a1b4597f83b73668a5eda078cfb6768cb'), 'address': '0x13a65B9F8039E2c032Bc022171Dc05B30c3f2892', 'blockHash': HexBytes('0x0cf76ca5ccbbfb5e2731422c15e9c23105e817cee7e9fa501da52789e0e800d4'), 'blockNumber': 22702673})"""
        logging.info(event)
        
    def approve(self, contract_address, type_="token", pigs_or_dogs="pigs", max_tries=1):
        txn_receipt = None
        public_key = self.address
        contract_address = Web3.toChecksumAddress(contract_address)
        if type_ == "pair":
            contract = self.w3.eth.contract(contract_address, abi=self.pair_abi)
        elif type_ == "token":
            contract = self.w3.eth.contract(contract_address, abi=self.erc20_abi)
        if pigs_or_dogs == "pigs":
            to_approve = ANIMAL_FARM_PIGS_ADDRESS
        else:
            to_approve = ANIMAL_FARM_DOGS_ADDRESS
        approved = False
        try:
            approved = contract.functions.allowance(public_key, to_approve).call()
            if int(approved) <= 500:
                # we have not approved this token yet. approve!
                for _ in range(max_tries):
                    try:
                        txn = contract.functions.approve(
                            to_approve,
                            115792089237316195423570985008687907853269984665640564039457584007913129639935
                        ).buildTransaction(
                            {
                                'from': public_key, 
                                'gasPrice': self.w3.toWei(self.gas_price, 'gwei'),
                                'nonce': self.get_nonce()
                            }
                        )
                        signed_txn = self.w3.eth.account.sign_transaction(txn, self.private_key)
                        txn = self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)
                        txn_receipt = self.w3.eth.waitForTransactionReceipt(txn)
                        if txn_receipt and "status" in txn_receipt and txn_receipt["status"] == 1: 
                            logging.info('Approved successfully!')
                            approved = True
                            break
                    except:
                        logging.debug(traceback.format_exc())
            else:
                logging.debug('Contract %s already approved.' % contract_address)
                approved = True
        except:
            logging.debug(traceback.format_exc())
        if approved is False:
            logging.debug('Could not approve contract: %s' % contract_address)
        return approved
    
    def nonce(self):
        return self.w3.eth.getTransactionCount(self.address)

    def fix_decimal(self, amount, token_address=None, decimals=None):
        if decimals is not None:
            return decimal_fix_places(amount, decimals)
        elif token_address is not None:
            return Decimal(amount / (10 ** self.get_decimals(token_address)))
        else:
            raise Exception("token address, or decimal count must be supplied to _fix_decimal().")
    
    def get_decimals(self, token_address):
        contract_address = Web3.toChecksumAddress(token_address)
        contract = self.w3.eth.contract(contract_address, abi=self.erc20_abi)
        return contract.functions.decimals().call()
    
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
    
    def get_contract_balance(self):
        return self.garden_contract.functions.getBalance().call()
    
    def get_market_seeds(self):
        try:
            result = self.garden_contract.functions.marketSeeds().call()
        except:
            result = None
            logging.debug(traceback.format_exc())
        return result
    
    def plant_seeds(self, max_tries=1):
        txn_receipt = None
        for _ in range(max_tries):
            try:
                txn = self.garden_contract.functions.plantSeeds(self.address).buildTransaction({
                    "gasPrice": eth2wei(self.gas_price, "gwei"), "nonce": self.nonce()})
                signed_txn = self.w3.eth.account.sign_transaction(txn, self.private_key)
                txn = self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)
                txn_receipt = self.w3.eth.waitForTransactionReceipt(txn)
                if txn_receipt and "status" in txn_receipt and txn_receipt["status"] == 1: 
                    logging.info('Planted seeds successfully!')
                    break
                else:
                    logging.info('Could not plant seeds.')
                    logging.debug(txn_receipt)
                    time.sleep(10)
            except:
                logging.debug(traceback.format_exc())
                time.sleep(10)
        return txn_receipt
    
    def sell_seeds(self, max_tries=1):
        txn_receipt = None
        for _ in range(max_tries):
            try:
                txn = self.garden_contract.functions.sellSeeds().buildTransaction({
                    "gasPrice": eth2wei(self.gas_price, "gwei"), "nonce": self.nonce()})
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
    
    def get_claimed_balance(self):
        contract = self.get_pair_contract(ANIMAL_FARM_GARDEN_PAIR_ADDRESS)
        return contract.functions.balanceOf(self.address).call()
    
    def deposit_drip_lp_farm(self, max_tries=1):
        lp_balance = self.get_claimed_balance()
        self.approve(ANIMAL_FARM_GARDEN_PAIR_ADDRESS, type_="pair", pigs_or_dogs="dogs")
        result = self.deposit(2, lp_balance, pigs_or_dogs="dogs", max_tries=max_tries)
        return result
    
    def calculate_seed_sell(self, seed_count):
        try:
            # get lp earned per day.
            # result = wei2eth(self.garden_contract.functions.calculateSeedSell(plant_count * 86400).call())
            # result = result * 0.95
            result = wei2eth(self.garden_contract.functions.calculateSeedSell(seed_count).call())
        except:
            result = None
        return result
    
    def get_user_lp(self, seed_count):
        result = self.calculate_seed_sell(seed_count) * Decimal(0.95)
        return result
    
    def get_drip_busd_lp_price(self):
        """
        Calculate how much current lp is worth.
        """
        try:
            self.drip_busd["supply"] = wei2eth(self.garden_lp_contract.functions.totalSupply().call())
            reserves = self.garden_lp_contract.functions.getReserves().call()
            token0 = self.garden_lp_contract.functions.token0().call()
            token1 = self.garden_lp_contract.functions.token1().call()
            self.drip_busd["drip_reserve"] = self.fix_decimal(reserves[0], token_address=token0)
            self.drip_busd["busd_reserve"] = self.fix_decimal(reserves[1], token_address=token1)
            # Get actual price in USD from the pancakeswap api.
            token0_price_data = pancakeswap_api_get_price(token0)
            token1_price_data = pancakeswap_api_get_price(token1)
            self.drip_busd["drip_price"] = Decimal(token0_price_data["data"]["price"])
            self.drip_busd["busd_price"] = Decimal(token1_price_data["data"]["price"])
            self.drip_busd["lp_ratio"] = Decimal(1 / self.drip_busd["supply"])
            self.drip_busd["price"] = (self.drip_busd["drip_reserve"] * self.drip_busd["lp_ratio"] * self.drip_busd["drip_price"]) + \
                (self.drip_busd["busd_reserve"] * self.drip_busd["lp_ratio"] * self.drip_busd["busd_price"])
        except:
            logging.info(traceback.format_exc())
            return self.drip_busd
        return self.drip_busd
    
    def get_token_contract(self, token_address):
        return self.w3.eth.contract(to_checksum(token_address), abi=self.erc20_abi)
    
    def get_pool_contract(self, pigs_or_dogs="pigs"):
        if pigs_or_dogs == "pigs":
            return self.w3.eth.contract(
                to_checksum(ANIMAL_FARM_PIGS_ADDRESS), abi=self.pigs_abi)
        elif pigs_or_dogs == "dogs":
            return self.w3.eth.contract(
                to_checksum(ANIMAL_FARM_DOGS_ADDRESS), abi=self.pigs_abi)
        else:
            return None
        
    def get_pair_contract(self, pair_address):
        return self.w3.eth.contract(
            to_checksum(pair_address), abi=self.pair_abi)
        
    def get_all_pools(self, pigs_or_dogs="pigs"):
        contract = self.get_pool_contract(pigs_or_dogs=pigs_or_dogs)
        item_dict = {}
        for i in range(contract.functions.poolLength().call()):
            pool_data = contract.functions.poolInfo(i).call()
            currency = pool_data[0]
            token_contract = self.get_token_contract(currency)
            symbol = token_contract.functions.symbol().call()
            if "LP" in symbol:
                token_contract = self.get_pair_contract(currency)
                token0 = token_contract.functions.token0().call()
                token1 = token_contract.functions.token1().call()
                token0_symbol = self.get_token_contract(token0).functions.symbol().call()
                token1_symbol = self.get_token_contract(token1).functions.symbol().call()
                symbol = "%s<>%s" % (token0_symbol, token1_symbol)
            logging.info('%s - %s - %s' % (i, symbol, currency))
            item_dict.update({"%s:%s" % (i, pigs_or_dogs): {"symbol": symbol, "currency": currency}})
        return item_dict
    
    def can_harvest(self, pool_id, pigs_or_dogs="pigs"):
        contract = self.get_pool_contract(pigs_or_dogs=pigs_or_dogs)
        try:
            resp = contract.functions.canHarvest(pool_id, to_checksum(self.address)).call()
        except:
            logging.debug(traceback.format_exc())
            resp = None
        return resp
    
    def bottom_price(self, pigs_or_dogs="pigs"):
        try:
            # start_block = contract.functions.emissionStartBlock().call()
            # end_block = contract.functions.emissionEndBlock().call()
            # total_blocks = end_block - start_block
            # token_per_block = contract.functions.tokenPerBlock().call()
            # logging.info('start block: %s' % start_block)
            # logging.info('end block: %s' % end_block)
            # logging.info('total blocks: %s' % total_blocks)
            # logging.info('token per block: %s' % token_per_block)
            contract = self.get_token_contract("0xDBdC73B95cC0D5e7E99dC95523045Fc8d075Fb9e")
            pool_info = contract.functions.balanceOf(self.address).call()
            return pool_info
        except:
            logging.info(traceback.format_exc())
            
    def deposit(self, pool_id, amount, pigs_or_dogs="pigs", max_tries=1):
        contract = self.get_pool_contract(pigs_or_dogs=pigs_or_dogs)
        txn_receipt = None
        for _ in range(max_tries):
            try:
                txn = contract.functions.deposit(pool_id, amount).buildTransaction({
                    "gasPrice": eth2wei(self.gas_price, "gwei"), "nonce": self.nonce()})
                signed_txn = self.w3.eth.account.sign_transaction(txn, self.private_key)
                txn = self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)
                txn_receipt = self.w3.eth.waitForTransactionReceipt(txn)
                if txn_receipt and "status" in txn_receipt and txn_receipt["status"] == 1: 
                    logging.info('Deposited into pool successfully!')
                    return txn_receipt
                else:
                    logging.info('Could not deposit into pool.')
                    logging.debug(txn_receipt)
                    time.sleep(10)
            except:
                logging.info(traceback.format_exc())
        return txn_receipt
    
    def get_pool_user_info(self, pool_id, pigs_or_dogs="pigs"):
        # Get reward info from pools
        contract = self.get_pool_contract(pigs_or_dogs=pigs_or_dogs)
        try:
            pool_data = contract.functions.userInfo(pool_id, to_checksum(self.address)).call()
            amount, reward, reward_locked, next_harvest = pool_data
            amount = wei2eth(amount)
            reward = wei2eth(reward)
            reward_locked = wei2eth(reward_locked)
        except:
            logging.debug(traceback.format_exc())
            amount = reward = reward_locked = next_harvest = None
        return {"amount": amount, "reward": reward, "reward_locked": reward_locked, "next_harvest": next_harvest}