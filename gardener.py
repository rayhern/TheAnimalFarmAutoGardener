import os
import sys
import logging
import traceback
from settings import *
from animalfarm import Garden, FARMING_PHRASES
from web3 import Web3
from utils import decimal_round, eth2wei, wei2eth, pancakeswap_api_get_price
from decimal import Decimal
import time
import random

VERSION = "1.0"

def main():
    os.system("clear")
    
    # Setup logger.
    log_format = '%(asctime)s: %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_format, stream=sys.stdout)
    logging.info('honest work by Ray v%s Started!' % VERSION)
    
    garden = Garden(
        PRIVATE_KEY, txn_timeout=TXN_TIMEOUT, gas_price=GAS_PRICE_IN_WEI, rpc_host=RPC_HOST)
    
    # compound or sell
    # the method is to alternate between the two when minimum plants is reached.
    current_action = "compound"
    
    # TODO add session compounded counter.
    # TODO add session sold counter.
    # TODO calculate lp into usd worth.
    
    while True:
        
        # Get dogs info
        dogs_price = get_token_price('0xDBdC73B95cC0D5e7E99dC95523045Fc8d075Fb9e')
        pigs_price = get_token_price('0x3A4C15F96B3b058ab3Fb5FAf1440Cc19E7AE07ce')
        
        # Get garden info.
        garden_data = get_garden_data(garden, max_tries=MAX_TRIES)
        if len(garden_data) == 0:
            time.sleep(10)
            continue
        seed_count = garden_data.get('seeds', 0)
        plant_count = garden_data.get('plants', 0)
        seeds_per_plant = garden_data.get('seeds_per_plant', 0)
        new_plants = garden_data.get('new_plants', 0)
        if seed_count >= seeds_per_plant:
            new_plants = seed_count // seeds_per_plant
        else:
            new_plants = 0
        unclaimed_lp = garden_data.get('unclaimed_lp', 0)
        claimed_lp = garden_data.get('claimed_lp', 0)
        # Report garden stats.
        logging.info('----------------')
        logging.info('Seeds: %s. Plants: %s.' % (seed_count, plant_count))
        logging.info('New Plants: %s/%s.' % (new_plants, MINIMUM_NEW_PLANTS))
        logging.info('DOGS: $%s. PIGS: $%s.' % (decimal_round(dogs_price, 2), decimal_round(pigs_price, 2)))
        logging.info('Unclaimed: %s. Claimed: %s.' % (unclaimed_lp, claimed_lp))
        response = ""
        # Do actions in the garden.
        if new_plants > MINIMUM_NEW_PLANTS:
            if current_action == "compound":
                current_action = "sell"
                logging.info('Planting seeds (compounding)...')
                response = garden.plant_seeds(max_tries=MAX_TRIES)
            elif current_action == "sell":
                current_action = "compound"
                logging.info('Selling seeds...')
                response = garden.sell_seeds_for_lp(max_tries=MAX_TRIES)
            logging.debug('response: %s' % response)
        logging.info('Status: %s.' % random.choice(FARMING_PHRASES))
        time.sleep(MINUTES_BETWEEN_UPDATES * 60)
        
def get_garden_data(garden, max_tries=1):
    for _ in range(max_tries):
        try:
            seed_count = garden.get_user_seeds(garden.address)
            plant_count = garden.get_my_plants()
            seeds_per_plant = garden.get_seeds_per_plant()
            if seed_count >= seeds_per_plant:
                new_plants = seed_count // seeds_per_plant
            else:
                new_plants = 0
            unclaimed_lp = decimal_round(Decimal(wei2eth(garden.calculate_seed_sell(seed_count))), 4)
            claimed_lp = decimal_round(Decimal(wei2eth(garden.get_claimed_balance())), 4)
            break
        except:
            logging.debug(traceback.format_exc())
            return {}
    return {
        'seeds': seed_count,
        'plants': plant_count,
        'seeds_per_plant': seeds_per_plant,
        'new_plants': new_plants,
        'unclaimed_lp': unclaimed_lp,
        'claimed_lp': claimed_lp
    }

def get_token_price(token):
    price_dict = pancakeswap_api_get_price(token)
    token_price = Decimal(price_dict["data"]["price"])
    return token_price

if __name__ == "__main__":
    main()
    