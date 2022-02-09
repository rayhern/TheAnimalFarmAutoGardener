import os
import sys
import logging
import traceback
from settings import *
from animalfarm import Garden, FARMING_PHRASES
from web3 import Web3
from utils import decimal_round, eth2wei, wei2eth
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
    
    while True:
        # Get garden info.
        garden_data = get_garden_data(garden, max_tries=MAX_TRIES)
        seed_count = garden_data.get('seeds', 0)
        plant_count = garden_data.get('plants', 0)
        seeds_per_plant = garden_data.get('seeds_per_plant', 0)
        new_plants = garden_data.get('new_plants', 0)
        if seed_count >= seeds_per_plant:
            new_plants = seed_count // seeds_per_plant
        else:
            new_plants = 0
        lp_amount = garden_data.get('lp_amount', 0)
        # Report garden stats.
        logging.info('Seeds: %s. Plants: %s.' % (seed_count, plant_count))
        logging.info('New Plants: %s/%s. LP: %s.' % (new_plants, MINIMUM_NEW_PLANTS, lp_amount))
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
        logging.info(random.choice(FARMING_PHRASES))
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
            lp_amount = decimal_round(wei2eth(garden.calculate_seed_sell(seed_count), "ether"), 4)
            break
        except:
            logging.debug(traceback.format_exc())
            return {}
    return {
        'seeds': seed_count,
        'plants': plant_count,
        'seeds_per_plant': seeds_per_plant,
        'new_plants': new_plants,
        'lp_amount': lp_amount
    }

if __name__ == "__main__":
    main()
    