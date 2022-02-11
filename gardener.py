import os
import sys
import logging
import traceback
from settings import *
from animalfarm import *
from web3 import Web3
from utils import decimal_round, eth2wei, wei2eth, pancakeswap_api_get_price, to_checksum
from decimal import Decimal
import time
import random

VERSION = "1.0"

POOL_DICT = {}
CLAIMED_COUNTER = 0
COMPOUND_COUNTER = 0

def main():
    global POOL_DICT
    os.system("clear")
    
    # Setup logger.
    log_format = '%(asctime)s: %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_format, stream=sys.stdout)
    logging.info('honest work by Ray v%s Started!' % VERSION)
    
    client = AnimalFarmClient(
        PRIVATE_KEY, txn_timeout=TXN_TIMEOUT, gas_price=GAS_PRICE_IN_WEI, rpc_host=RPC_HOST)

    # bottom_price = client.bottom_price()
    # logging.info(bottom_price)
    
    while True:
        # handle the garden actions.
        handle_garden(client)
        
        # take care of all the pools user is in! check settings.py
        handle_pools(client)

        logging.info('%s' % random.choice(FARMING_PHRASES))
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
            unclaimed_lp = decimal_round(garden.get_user_lp(seed_count), 4)
            drip_busd_lp = garden.get_drip_busd_lp_price()
            unclaimed_worth = drip_busd_lp["price"] * unclaimed_lp
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
        'unclaimed_worth': unclaimed_worth,
        'drip_busd': drip_busd_lp
    }

def get_token_price(token):
    price_dict = pancakeswap_api_get_price(token)
    token_price = Decimal(price_dict["data"]["price"])
    return token_price

def save_stats(last_action, claimed, planted):
    try:
        with open('stats.log', 'w') as fp:
            fp.write('%s,%s,%s\n' %(last_action, claimed, planted))
    except:
        logging.debug(traceback.format_exc())

def load_stats():
    try:
        with open('stats.log', 'r') as fp:
            temp_lines = fp.readlines()
        stats_data = temp_lines[0].strip().split(',')
    except:
        stats_data = ["compound", 0, 0]
        logging.debug(traceback.format_exc())
    return stats_data

def handle_garden(client):
    global CLAIMED_COUNTER, COMPOUND_COUNTER
    # loading previous session stats, so we know where we left off.
    current_action, claimed_counter, compound_counter = load_stats()
    # Get dogs info
    dogs_price = get_token_price(DOGS_TOKEN_ADDRESS)
    pigs_price = get_token_price(PIGS_TOKEN_ADDRESS)
    # Get garden info.
    garden_data = get_garden_data(client, max_tries=MAX_TRIES)
    if len(garden_data) == 0:
        time.sleep(10)
        return
    seed_count = garden_data.get('seeds', 0)
    plant_count = garden_data.get('plants', 0)
    seeds_per_plant = garden_data.get('seeds_per_plant', 0)
    new_plants = garden_data.get('new_plants', 0)
    if seed_count >= seeds_per_plant:
        new_plants = seed_count // seeds_per_plant
    else:
        new_plants = 0
    unclaimed_lp = garden_data.get('unclaimed_lp', 0)
    unclaimed_worth = garden_data.get('unclaimed_worth', 0)
    # Report garden stats.
    logging.info('----------------')
    logging.info('Seeds: %s. Plants: %s.' % (seed_count, plant_count))
    logging.info('New Plants: %s/%s.' % (new_plants, MINIMUM_NEW_PLANTS))
    logging.info('DOGS: $%s. PIGS: $%s.' % (decimal_round(dogs_price, 2), decimal_round(pigs_price, 2)))
    logging.info('Pending: %s. Value: $%s.' % (unclaimed_lp, decimal_round(unclaimed_worth, 2)))
    logging.info('Sold: %s. Planted: %s. Next Action: %s.' % (CLAIMED_COUNTER, COMPOUND_COUNTER, current_action))
    response = ""
    # Save stats before current action changes!
    save_stats(current_action, claimed_counter, compound_counter)
    # Do actions in the garden.
    if new_plants > MINIMUM_NEW_PLANTS:
        if current_action == "compound":
            current_action = "sell"
            logging.info('Planting seeds (compounding)...')
            response = client.plant_seeds(max_tries=MAX_TRIES)
            if response and "status" in response and response["status"] == 1:
                COMPOUND_COUNTER += 1
        elif current_action == "sell":
            current_action = "compound"
            logging.info('Selling seeds...')
            response = client.sell_seeds(max_tries=MAX_TRIES)
            if response and "status" in response and response["status"] == 1:
                CLAIMED_COUNTER += 1
        logging.debug('response: %s' % response)
    # Save stats 1 more time to make sure we are up to date!
    save_stats(current_action, claimed_counter, compound_counter)

def handle_pools(client):
    global POOL_DICT
    if os.path.exists("pools.log") is True:
        POOL_DICT = load_json("pools.log")
        
    if len(POOL_DICT) == 0:
        logging.info("Downloading pool information...")
        dog_pools = client.get_all_pools(pigs_or_dogs="dogs")
        pig_pools = client.get_all_pools(pigs_or_dogs="pigs")
        POOL_DICT.update(pig_pools)
        POOL_DICT.update(dog_pools)
        save_json("pools.log", POOL_DICT)
    if len(POOL_DICT) > 0:
        logging.info('----------------')
        for pool_id in DOGS_POOLS:
            dict_key = "%s:dogs" % pool_id
            current_pool_dict = POOL_DICT[dict_key]
            # Get reward info from pools
            reward_data = client.get_pool_user_info(pool_id, pigs_or_dogs="dogs")
            amount = decimal_round(Decimal(reward_data["amount"]), 4)
            logging.info('Pool: %s. Deposited: %s.' % (
                current_pool_dict["symbol"], amount))
        for pool_id in PIGS_POOLS:
            dict_key = "%s:pigs" % pool_id
            current_pool_dict = POOL_DICT[dict_key]
            # Get reward info from pools
            reward_data = client.get_pool_user_info(pool_id, pigs_or_dogs="pigs")
            amount = decimal_round(Decimal(reward_data["amount"]), 4)
            logging.info('Pool: %s. Deposited: %s.' % (
                current_pool_dict["symbol"], amount))
    
def save_json(filename, dict_obj):
    try:
        with open(filename, 'w') as fp:
            fp.write(json.dumps(dict_obj))
    except:
        logging.debug(traceback.format_exc())
        
def load_json(filename):
    items = {}
    try:
        with open(filename, 'r') as fp:
            items = json.loads(fp.read())
    except:
        logging.debug(traceback.format_exc())
    return items

if __name__ == "__main__":
    main()
    