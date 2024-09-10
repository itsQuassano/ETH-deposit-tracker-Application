# ETH Deposit Tracker Application

## Overview

The ETH Deposit Tracker Application is a Python-based tool that monitors deposits to the Ethereum Beacon Deposit Contract and sends notifications via Telegram. It utilizes Docker for containerization and Prometheus for monitoring metrics.

## Prerequisites

- **Docker**: Ensure Docker is installed on your machine. [Download Docker](https://www.docker.com/get-started)
- **Docker Compose** (optional): Useful for managing multi-container Docker applications

## Setup Instructions

### 1. Clone the Repository

Clone the repository containing the ETH Deposit Tracker Application folder:

```bash
git clone <repository-url>
cd ETH\ Deposit\ Tracker\ Application/python-image
```

### 2. Environment Variables

Create a `.env` file in the `python-image` directory with the following content:

```
ALCHEMY_RPC_URL=<Your Alchemy RPC URL>
TELEGRAM_API_TOKEN=<Your Telegram Bot API Token>
TELEGRAM_CHAT_ID=<Your Telegram Chat ID>
```

Replace the placeholders with your actual values.

### 3. Build the Docker Image

```bash
docker build -t 1ethapp .
```

### 4. Run the Docker Container

```bash
docker run --name 1ethapp --env-file .env -d 1ethapp
```

If you encounter a conflict with the container name, remove the existing container:

```bash
docker stop 1ethapp
docker rm 1ethapp
```

Then run the container again.

## Application Structure

- `app.py`: Main application file containing the deposit tracking logic
- `Dockerfile`: Instructions for building the Docker image
- `requirements.txt`: List of Python dependencies

## Key Features

- Monitors Ethereum Beacon Deposit Contract for new deposits
- Sends notifications via Telegram for each new deposit
- Uses Prometheus for monitoring and metrics collection
- Implements exponential backoff for handling network issues

## Logging

The application logs its activities to both a file (`deposit_tracker.log`) and the console. You can view the logs using:

```bash
docker logs 1ethapp
```

## Customization

You can modify the following aspects of the application:

- Adjust the polling interval in the `monitor_deposits` function
- Customize the Telegram notification message format in the `notify_new_deposits` function
- Add additional metrics to the Prometheus registry as needed



## Application Structure

- `app.py`: Main application file containing the deposit tracking logic
- `Dockerfile`: Instructions for building the Docker image
- `requirements.txt`: List of Python dependencies

## Code Explanation: app.py

The `app.py` file contains the core functionality of the ETH Deposit Tracker. Here's a breakdown of its main components:

### Imports and Setup

```python
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
```

This section imports necessary libraries for Ethereum interaction, HTTP requests, logging, and Prometheus metrics.

### Environment Variables

```python
load_dotenv()
TELEGRAM_API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
```

Loads environment variables from the `.env` file, including Telegram API credentials.

### Prometheus Setup

```python
registry = CollectorRegistry()
g_deposits = Gauge('new_deposits_total', 'Total number of new deposits', registry=registry)
```

Sets up Prometheus metrics to monitor the total number of new deposits.

### Logging Configuration

```python
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("deposit_tracker.log"),
        logging.StreamHandler()
    ]
)
```

Configures logging to output both to a file and the console.

### Ethereum Connection

```python
RPC_URL = os.getenv("ALCHEMY_RPC_URL")
w3 = Web3(Web3.HTTPProvider(RPC_URL))
```

Establishes a connection to the Ethereum network using the provided RPC URL.

### Key Functions

1. `exponential_backoff`: Implements retry logic with exponential backoff for handling network issues.

2. `fetch_deposit_events`: Retrieves deposit events from the Ethereum blockchain.

3. `monitor_deposits`: The main loop that continuously checks for new deposits.

4. `save_deposits`: Placeholder function for saving deposit details (to be implemented as needed).

5. `notify_new_deposits`: Processes new deposits and sends notifications.

6. `send_telegram_notification`: Sends notifications to a Telegram chat.

### Main Execution

```python
def main():
    if not w3.is_connected():
        logging.error("Failed to connect to Ethereum network")
        return

    start_block = w3.eth.get_block_number()
    logging.info(f"Connected to Ethereum network. Latest block: {start_block}")
    logging.info(f"Starting deposit tracking from block {start_block}")
    send_telegram_notification("ETH Deposit Tracker Starting: - ")
    monitor_deposits(start_block)

if __name__ == "__main__":
    main()
```

The `main` function initializes the connection to Ethereum, logs the starting block, sends an initial Telegram notification, and starts the deposit monitoring process.

## Customization

You can modify the following aspects of the application:

- Adjust the polling interval in the `monitor_deposits` function
- Customize the Telegram notification message format in the `notify_new_deposits` function
- Add additional metrics to the Prometheus registry as needed

## Troubleshooting

If you encounter issues:

1. Ensure all environment variables are correctly set in the `.env` file
2. Check the application logs for error messages
3. Verify your Ethereum RPC URL is valid and accessible
4. Confirm your Telegram bot token and chat ID are correct

