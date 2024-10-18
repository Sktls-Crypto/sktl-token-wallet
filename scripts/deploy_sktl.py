from brownie import SKTL, SktlAirdrop, network, config
from scripts.helpful_scripts import get_account, get_contract
import shutil
import os
import yaml
import json
from web3 import Web3
import pandas as pd
import logbook
import sys
from math import floor
from brownie.network.gas.strategies import LinearScalingStrategy
from brownie.network import gas_price

logger = logbook.Logger("deploy_sktl")
logbook.StreamHandler(sys.stdout).push_application()

# KEPT_BALANCE = Web3.toWei(100, "ether")


def print_account(index: str):
    print(get_account(int(index)))


def print_current_contract():
    print(SKTL[-1].address)


def deploy_sktls(update_front_end=False):
    account = get_account()
    sktl_token = SKTL.deploy({"from": account}, publish_source=True)
    if update_front_end:
        # copy_front_end()
        pass

    logger.info(f"{sktl_token=}")
    logger.info(f"{sktl_token.totalSupply()=}")


def simple_transfer(addr, amt):
    # just testing
    account = get_account()
    SKTL[-1].transfer(addr, amt, {"from": account})


def get_total_supply(addr):
    account = get_account()
    logger.info(f"total supply = {SKTL[-1].totalSupply({'from': account}) / 10 ** 18}")
    logger.info(f"owner account = {SKTL[-1].balanceOf(addr) / 10 ** 18}")


def deploy_airdrop():
    account = get_account()
    sktlairdrop = SktlAirdrop.deploy(SKTL[-1], {"from": account}, publish_source=True)
    logger.info(f"Deploy success to {sktlairdrop.address}")


def deploy_approve():
    # need to approve the airdrop contract can spend for the owner account
    SKTL[-1].approve(
        SktlAirdrop[-1], SKTL[-1].balanceOf(get_account(0)), {"from": get_account(0)}
    )


def batch(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]


def airdrop():
    # read a list of address and airdrop

    address_file = "airdrop_address_20220506.json"
    with open(address_file, "r") as afile:
        addr = json.loads(afile.read())

    validated_addrs = list(
        set(
            [a for a in addr if (isinstance(a, str) and len(a) == 42 and a[:2] == "0x")]
        )
    )

    amt = floor((100 * 10 ** 6 * 10 ** 18) / len(validated_addrs))
    # amt = 100000 * (10 ** 18)
    logger.info(f"Going to drop {len(validated_addrs)} addresses for {amt} sktls")
    # gas_strategy = LinearScalingStrategy("10 gwei", "100000 gwei", 1.1)
    # gas_price(gas_strategy)
    # network.gas_limit(2 * 10 ** 18)

    for addrs in batch(validated_addrs, 100):
        logger.info(f"dropping {len(addrs)=}, first addr={addrs[0]}")
        SktlAirdrop[-1].airDrop(addrs, amt, {"from": get_account(0)})


def rewardBalance(acc):
    bal = SKTL[-1].rewardBalance(acc)
    print(f"{acc} has {bal / 10**18} SKTLs")


def rewardTokenBalance(acc):
    bal = SKTL[-1].rewardTokenBalance(acc)
    print(f"{acc} has {bal / 10**18} rewardToken(s)")


def add_reward(amt):
    amt = int(amt)
    raw_amt = amt * (10 ** 18)
    account = get_account(0)
    print(f"Adding new SKTL in the amt:{amt}, raw_amt={raw_amt}")
    SKTL[-1].increaseReward(raw_amt, {"from": account})
    # print(account, SKTL[-1].balanceOf(account))


def withdraw(acc_idx):
    acc = get_account(int(acc_idx))
    SKTL[-1].withdraw({"from": acc})
    print(f"Withdrew for {acc}")


def copy_front_end():
    print("Updating front end...")
    # The Build
    copy_folders_to_front_end("./build/contracts", "./front_end/src/chain-info")

    # The Contracts
    copy_folders_to_front_end("./contracts", "./front_end/src/contracts")

    # The ERC20
    copy_folders_to_front_end(
        "./build/contracts/dependencies/OpenZeppelin/openzeppelin-contracts@4.6.0",
        "./front_end/src/chain-info",
        False,
    )
    # The Map
    copy_files_to_front_end(
        "./build/deployments/map.json", "./front_end/src/chain-info/map.json",
    )

    # The Config, converted from YAML to JSON
    with open("brownie-config.yaml", "r") as brownie_config:
        config_dict = yaml.load(brownie_config, Loader=yaml.FullLoader)
        with open(
            "./front_end/src/brownie-config-json.json", "w"
        ) as brownie_config_json:
            json.dump(config_dict, brownie_config_json)
    print("Front end updated!")


def copy_folders_to_front_end(src, dest, cleanup=True):
    if cleanup and os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree(src, dest, dirs_exist_ok=not cleanup)


def copy_files_to_front_end(src, dest):
    if os.path.exists(dest):
        os.remove(dest)
    shutil.copyfile(src, dest)


# def air_drop():
#     df = pd.read_csv('/Users/danielng/projects/sktls-defi/temp/sktl_init_drop_address.csv')
#     for addr in df.address:
#         Sktl20[-1].transfer(addr, 1000 * (10 ** 18), {"from": get_account(0)})
#


def main():
    deploy_sktls(update_front_end=False)
