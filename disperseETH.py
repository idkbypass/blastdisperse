import os
from dotenv import load_dotenv
from web3 import Web3
import json
from colorama import Fore, init
import time
import random
import requests
import ctypes

ctypes.windll.kernel32.SetConsoleTitleW("Farming Bot for BlastDisperse by @valeesec")

init()

def get_user_info(user_address):
    user_info_url = f"https://api.blastdisperse.app/users?address={user_address}"
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-US,en;q=0.9',
        'Dnt': '1',
        'Origin': 'https://www.blastdisperse.app',
        'Referer': 'https://www.blastdisperse.app/',
        'Sec-Ch-Ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    }

    try:
        user_info_response = requests.get(user_info_url, headers=headers)
        user_info_response.raise_for_status()

        user_info_data = user_info_response.json()
        filtered_info = {
            "address": user_info_data.get("address", ""),
            "rank": user_info_data.get("rank", ""),
            "total_points": user_info_data.get("total_points", ""),
            "eth_transactions": user_info_data.get("eth_transactions", "")
        }
        
        print(Fore.BLUE, filtered_info)
    except requests.RequestException as e:
        print(Fore.RED, f"Error retrieving user information: {e}")

load_dotenv()

print(Fore.BLUE, "Starting the tool.. github @idkbypass | twitter @valeesec")

private_key = os.getenv("PRIVATE_KEY")

web3 = Web3(Web3.HTTPProvider("https://sepolia.blast.io"))

user_address = web3.eth.account.from_key(private_key).address

get_user_info(user_address)

time.sleep(1.4)

print(Fore.WHITE, f"Starting balance for {user_address}: {web3.from_wei(web3.eth.get_balance(user_address), 'ether')} ETH")

contract_address = "0x8dd3CBB840676dA4bc4d39250f9e46D9302f7a16"

abi_file_path = "blast-contract.json"
with open(abi_file_path, "r") as abi_file:
    contract_abi = json.load(abi_file)

contract = web3.eth.contract(address=contract_address, abi=contract_abi)

GAS_PRICE_BUMP = 550000000  

iteration_counter = 0

def resume_script():
    get_user_info(user_address)
    print(Fore.YELLOW, "Resuming the script.")

while True:
    num_addresses = random.randint(2, 3)
    addresses = [user_address] * num_addresses
    
    total_amount = random.randint(100000000000000000000,120000000000000000000 )
    amount_per_address = total_amount // num_addresses
    
    amounts = [amount_per_address] * num_addresses
    
    max_base_fee = 5.999043439
    priority_fee = 0.002308228
    gas_limit = 27796366
    
    base_gas_price = int(max_base_fee * 1e9)  
    max_priority_gas_price = int(priority_fee * 1e9)

    current_block = web3.eth.get_block("latest")
    gas_limit = max(gas_limit, min(current_block["gasLimit"], current_block["gasUsed"] + 150000))

    payable_amount = sum(amounts)

    transaction = contract.functions.disperseETH(addresses, amounts).build_transaction({
        'gas': gas_limit,
        'nonce': web3.eth.get_transaction_count(user_address),
        'value': payable_amount,
        'maxFeePerGas': base_gas_price + GAS_PRICE_BUMP,
        'maxPriorityFeePerGas': min(max_priority_gas_price, base_gas_price) + GAS_PRICE_BUMP,
    })

    signed_transaction = web3.eth.account.sign_transaction(transaction, private_key)

    try:
        transaction_hash = web3.eth.send_raw_transaction(signed_transaction.rawTransaction)
        print(Fore.WHITE + f"[{Fore.BLUE}INFO{Fore.WHITE}] Transaction: https://testnet.blastscan.io/tx/{transaction_hash.hex()}")
        print(Fore.BLUE, "----------------------------------------------------BLASTDISPERSE----------------------------------------------------")
        time.sleep(23)
        get_user_info(user_address)
    except ValueError as ve:
        if 'replacement transaction underpriced' in str(ve):
            print(Fore.YELLOW, "Retrying the transaction with an increased gas price.")
            continue
        else:
            print(Fore.RED, f"Error sending transaction: {ve}")

    iteration_counter += 1

    if 15 <= iteration_counter <= 20:
        print(Fore.YELLOW, "Pausing script to avoid throttling.")
        time.sleep(random.uniform(12, 22))
        resume_script()

    random_sleep_duration = random.uniform(10, 14)
    time.sleep(random_sleep_duration)
