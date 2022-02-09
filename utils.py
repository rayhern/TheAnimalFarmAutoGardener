from web3 import Web3
from decimal import Decimal
import logging
import traceback

def wei2eth(wei, unit="ether"):
    return Web3.fromWei(wei, unit)

def eth2wei(eth, unit="ether"):
    return Web3.toWei(eth, unit)

def nonce(address):
    return Web3.eth.getTransactionCount(address)

def to_checksum(address):
    return Web3.toChecksumAddress(address)

def read_json_file(filepath):
    try:
        with open(filepath) as fp:
            results = fp.read()
    except:
        logging.info('Error reading json file.')
        results = None
    return results

def decimal_round(decimal_number, decimal_places):
    return decimal_number.quantize(Decimal(10) ** -decimal_places)

def is_percent_down(previous_amount, current_amount, percent_down):
    if previous_amount - current_amount > Decimal(previous_amount) * (Decimal(percent_down) / Decimal(100)):
        return True
    else:
        return False
    
def is_percent_up(previous_amount, current_amount, percent_up):
    if current_amount - previous_amount > Decimal(previous_amount) * (Decimal(percent_up) / Decimal(100)):
        return True
    else:
        return False
