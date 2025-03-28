#!/usr/bin/env python3

import asyncio
import logging
import os
import sys
from typing import Dict

from beekeepy.service.asynchronous import create_beekeeper_service
from wax import WaxChainOptions, create_hive_chain
from wax.proto.operations import claim_reward_balance

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# Define environment variables and defaults
PASSWORD = os.getenv("WALLET_PASSWORD", "password")
WALLET_NAME = os.getenv("WALLET_NAME", "my_wallet")
HIVED_ADDRESS = os.getenv("HIVED_ADDRESS", "https://api.hive.blog")
PRIVATE_KEY = os.getenv("ACTIVE_WIF", "")
PUBLIC_KEY = os.getenv("PUBLIC_KEY", "")
ACCOUNT_NAME = os.getenv("ACCOUNT_NAME", "")

# Initialize WAX chain connection
wax = create_hive_chain(WaxChainOptions(endpoint_url=HIVED_ADDRESS))


def get_wif() -> str:
    """Retrieve and validate the WIF from environment variables."""
    wif = os.getenv("ACTIVE_WIF")
    if not wif:
        logger.error("Environment variable ACTIVE_WIF must be set.")
        sys.exit(1)
    return wif


async def get_account_info(account_name: str) -> Dict:
    """Get account information including reward balances."""
    try:
        # Get account information using WAX API
        account_info = await wax.api.get_accounts([account_name])
        if not account_info or not account_info.accounts:
            logger.error(f"Account {account_name} not found.")
            return {}

        account = account_info.accounts[0]

        # Extract reward balances
        reward_hive = account.reward_hive_balance
        reward_hbd = account.reward_hbd_balance
        reward_vests = account.reward_vesting_balance

        logger.info(f"Today's rewards: {reward_hive} {reward_hbd} {reward_vests}")

        return {
            "account": account,
            "reward_hive": reward_hive,
            "reward_hbd": reward_hbd,
            "reward_vests": reward_vests,
        }
    except Exception as e:
        logger.error(f"Error retrieving account information: {e}")
        return {}


async def claim_rewards(account_name: str) -> None:
    """Claim rewards for the given account."""
    try:
        # Get account information and reward balances
        account_info = await get_account_info(account_name)
        if not account_info:
            return

        reward_hive = account_info["reward_hive"]
        reward_hbd = account_info["reward_hbd"]
        reward_vests = account_info["reward_vests"]

        # Check if there are rewards to claim
        if (
            reward_hive.amount == "0"
            and reward_hbd.amount == "0"
            and reward_vests.amount == "0"
        ):
            logger.info("No rewards to claim.")
            return

        # Create a transaction to claim rewards
        tx = await wax.create_transaction()
        tx.push_operation(
            claim_reward_balance(
                account=account_name,
                reward_hive=reward_hive,
                reward_hbd=reward_hbd,
                reward_vesting_shares=reward_vests,
            )
        )

        # Sign and broadcast the transaction
        async with create_beekeeper_service(
            wallet_name=WALLET_NAME, password=PASSWORD
        ) as beekeepy:
            # Import the private key if not already in the wallet
            if PUBLIC_KEY not in await beekeepy.wallet.public_keys:
                await beekeepy.wallet.import_key(private_key=PRIVATE_KEY)

            # Sign the transaction
            await tx.sign(wallet=beekeepy.wallet, public_key=PUBLIC_KEY)

            # Broadcast the transaction
            await wax.broadcast(tx)

        logger.info("Rewards claimed successfully.")

        # Get updated account information
        await get_account_info(account_name)
    except Exception as e:
        logger.error(f"Error claiming rewards: {e}")


async def get_balance(account_name: str) -> Dict:
    """Get and return the balance of the given account."""
    try:
        # Get account information
        account_info = await wax.api.get_accounts([account_name])
        if not account_info or not account_info.accounts:
            logger.error(f"Account {account_name} not found.")
            return {}

        account = account_info.accounts[0]

        # Extract balances
        hive_balance = account.balance
        hbd_balance = account.hbd_balance
        vesting_shares = account.vesting_shares

        balances = {"hive": hive_balance, "hbd": hbd_balance, "vests": vesting_shares}

        logger.info(f"Current balances: {balances}")
        return balances
    except Exception as e:
        logger.error(f"Error retrieving balance: {e}")
        return {}


async def main():
    """Main function to execute Hive reward claiming process."""
    # Get the private key from environment variables
    private_key = get_wif()
    if not private_key:
        return

    # Set the private key for the script
    global PRIVATE_KEY
    PRIVATE_KEY = private_key

    # Get account name from environment or use default
    account_name = os.getenv("ACCOUNT_NAME")
    if not account_name:
        logger.error("Environment variable ACCOUNT_NAME must be set.")
        sys.exit(1)

    # Get current balance
    await get_balance(account_name)

    # Claim rewards
    await claim_rewards(account_name)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
