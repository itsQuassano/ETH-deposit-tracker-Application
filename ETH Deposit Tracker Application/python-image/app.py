import os
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
from datetime import datetime
import requests
from typing import List
from dataclasses import dataclass
from web3 import Web3
from dotenv import load_dotenv
import logging
import time
from requests.exceptions import RequestException, HTTPError

# Telegram API credentials
# TODO: Move these to environment variables for better security
TELEGRAM_API_TOKEN = '7229473187:AAEONbOqAKyglszVXwVhlzfCYDzPFYBTjBs'
TELEGRAM_CHAT_ID = '2125311347'

# Prometheus Setup and Connection
registry = CollectorRegistry()
g_deposits = Gauge('new_deposits_total', 'Total number of new deposits', registry=registry)

# Load environment variables
load_dotenv()

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("deposit_tracker.log"),
        logging.StreamHandler()
    ]
)

# Ethereum RPC setup
RPC_URL = os.getenv("ALCHEMY_RPC_URL")
if not RPC_URL:
    raise ValueError("ALCHEMY_RPC_URL environment variable is not set")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# Beacon Deposit Contract address
BEACON_DEPOSIT_CONTRACT = "0x00000000219ab540356cBB839Cbe05303d7705Fa"

# Define Deposit data class
@dataclass
class Deposit:
    block_number: int
    block_timestamp: int
    fee: float
    hash: str
    pubkey: str

# Utility function for exponential backoff
def exponential_backoff(func, retries=5, base_delay=1):
    delay = base_delay
    for attempt in range(retries):
        try:
            return func()
        except Exception as e:
            logging.warning(f"Request failed: {str(e)}. Retrying in {delay} seconds...")
            time.sleep(delay)
            delay *= 2  # Exponentially increase the delay
    logging.error("Max retries reached. Giving up.")
    raise RuntimeError("Max retries reached")

# Function to fetch deposit events from the blockchain
def fetch_deposit_events(current_block, end_block):
    filter_params = {"address": BEACON_DEPOSIT_CONTRACT}
    logging.info(f"Fetching logs from block {current_block} to {end_block} with filter: {filter_params}")

    try:
        logs = exponential_backoff(lambda: w3.eth.get_logs(filter_params))
        return logs
    except Exception as e:
        logging.error(f"Error fetching deposit events: {e}")
        logging.error(f"Filter params: {filter_params}")
        raise

# Main function to monitor deposits
def monitor_deposits(start_block: int):
    """
    Monitor the Beacon Deposit Contract for new ETH deposits.
    """
    current_block = start_block

    while True:
        try:
            latest_block = w3.eth.get_block_number()
            end_block = min(current_block + 1000, latest_block)  # Process up to 1000 blocks at a time

            if current_block > latest_block:
                logging.info("Waiting for new blocks...")
                time.sleep(30)  # Wait for 30 seconds before checking again
                continue

            new_deposits = fetch_deposit_events(current_block, end_block)
            if new_deposits:
                logging.info(f"Found {len(new_deposits)} new deposits.")
                save_deposits(new_deposits)
                notify_new_deposits(new_deposits)

            current_block = end_block + 1
        except Exception as e:
            logging.error(f"Error monitoring deposits: {e}", exc_info=True)
            time.sleep(60)  # Wait for 60 seconds if there's an error
        else:
            time.sleep(5)  # Short delay between successful iterations

# Function to save deposits (placeholder)


# Function to decode deposit amount from byte string
def decode_amount(data):
    """
    Decode the deposit amount from a byte string.
    """
    return int.from_bytes(data, byteorder='big')

# Function to notify about new deposits
def notify_new_deposits(new_deposits):
    for deposit in new_deposits:
        decoded_data = decode_amount(deposit['data'])
        deposit_info = (
            f"Block Number: {deposit.blockNumber}\n"
            f"Transaction Hash: {deposit.transactionHash}\n"
            f"Deposit Amount: {decoded_data}\n"
        )
        print(deposit_info)
        logging.info(deposit_info)
        send_telegram_notification(deposit_info)

# Function to send Telegram notifications
def send_telegram_notification(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_API_TOKEN}/sendMessage"
    payload = {
        'chat_id': 2125311347,
        'text': message,
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Raise an error for bad responses
        logging.info(f"Notification sent: {message}")
    except HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
    except RequestException as err:
        logging.error(f"Error sending Telegram notification: {err}")

# Main execution function
def main():
    if not w3.is_connected():
        logging.error("Failed to connect to Ethereum network")
        return

    start_block = w3.eth.get_block_number()
    logging.info(f"Connected to Ethereum network. Latest block: {start_block}")
    logging.info(f"Starting deposit tracking from block {start_block}")
    send_telegram_notification("ETH Deposit Tracker Starting: - ")
    monitor_deposits(start_block)

# Entry point of the script
if __name__ == "__main__":
    main()
