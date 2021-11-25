import unittest
import brownie
from brownie import SKTL
import random
from scripts.helpful_scripts import get_account
from collections import defaultdict

DECIMALS = 10**18
SCALING = 10**36


class TestSKTLSimpleDvd(unittest.TestCase):

    def assertIntAlmostEqual(
            self,
            value1,
            value2,
            msg: str = None,
            places: int = 12,  # decimal places in %
    ):
        if msg is not None:
            msg += f", {value1=} {value2=}"
        self.assertLessEqual(value1 / value2, 1 + (10**-places), msg)
        self.assertGreaterEqual(value1 / value2, 1 - (10**-places), msg)

    def setUp(self):
        self.init_token = 200 * 10**6  # 200 MM
        self.init_donation_pool = self.init_token // 2
        self.init_acc_tokens = [
            0,
            1000,  # 1
            2000,  # 2
            3000,  # 2
            7000,  # 4
            13000  # 5
        ]

        self.token = SKTL.deploy({"from": get_account(0)})
        for i in range(1, len(self.init_acc_tokens)):
            self.token.transfer(get_account(i),
                                self.init_acc_tokens[i] * DECIMALS)

        self.dontation_pool_acc = 9
        self.token.transfer(get_account(self.dontation_pool_acc),
                            self.init_donation_pool *
                            DECIMALS)  # this is the donation pool

    def test_random_transfer_and_reward(self):
        random.seed('a')
        init_acc_tokens = self.init_acc_tokens + [0, 0, 0, 100 * 10**6]
        init_acc_tokens[0] = 100 * 10**6 - sum(self.init_acc_tokens)
        transfered_record = defaultdict(int)  # {account => amt}
        reward_record = defaultdict(int)  # {account => amt}

        for loop in range(100):
            # TEST transfer
            fromacc = random.randint(1, 9)
            toacc = random.randint(1, 9)

            while toacc == fromacc:
                toacc = random.randint(0, 9)

            if self.token.balanceOf(get_account(fromacc)) == 0:
                continue

            transfer_pct = random.random()
            transfer_amt = int(self.token.balanceOf(get_account(fromacc)) * transfer_pct)
            transfered_record[fromacc] -= transfer_amt
            transfered_record[toacc] += transfer_amt
            print()
            print(f"Test Transfer {loop=}")
            for i in range(10):
                print(f"{i}: {self.token.balanceOf(get_account(i))}, tran={transfered_record[i]}")
            print(f"{fromacc=} {toacc=} {transfer_amt=}")

            self.token.transfer(get_account(toacc), transfer_amt,
                                {"from": get_account(fromacc)})

            for i in (fromacc, toacc):
                self.assertIntAlmostEqual(
                    self.token.balanceOf(get_account(i)),
                    init_acc_tokens[i] * DECIMALS + transfered_record[i] + reward_record[i],
                    f"{loop=}: acount[{i}] balance not match after transfer")

            # TEST Reward
            reward_amt = int(1000000 * random.random() * DECIMALS)

            print()
            print(f"Test reward {loop=} {reward_amt=}")

            for i in range(10):
                tot_balance = self.token.balanceOf(get_account(i)) + self.token.rewardBalance(get_account(i))
                reward_record[i] += int(reward_amt * tot_balance / self.token.totalSupply())
            self.token.increaseReward(reward_amt, {"from": get_account(0)})

            for i in range(10):
                print(f"{i}: rewardBalance={self.token.rewardBalance(get_account(i))} reward_rec={reward_record[i]}")

            # skip 1, because it's the owner
            for i in range(1, 10):
                tot_balance = self.token.balanceOf(get_account(i)) + self.token.rewardBalance(get_account(i))
                if tot_balance == 0:
                    continue
                self.assertIntAlmostEqual(
                    self.token.balanceOf(get_account(i)) + self.token.rewardBalance(get_account(i)),
                    init_acc_tokens[i] * DECIMALS + transfered_record[i] + reward_record[i],
                    f"{loop=}: acount[{i}] balance not match after reward")
