import unittest
import brownie
from brownie import SKTL
import random
from scripts.helpful_scripts import get_account
from collections import defaultdict

DECIMALS = 10 ** 18
SCALING = 10 ** 36


class TestSKTLLongTests(unittest.TestCase):
    def assertIntAlmostEqual(
        self,
        value1,
        value2,
        msg: str = None,
        places: int = 12,  # decimal places in %
    ):
        if msg is not None:
            msg += f", {value1=} {value2=}"
        self.assertLessEqual(value1 / value2, 1 + (10 ** -places), msg)
        self.assertGreaterEqual(value1 / value2, 1 - (10 ** -places), msg)

    def setUp(self):
        self.init_token = 200 * 10 ** 6  # 200 MM
        self.init_donation_pool = self.init_token // 2
        self.init_acc_tokens = [
            0,
            1000,  # 1
            2000,  # 2
            3000,  # 2
            7000,  # 4
            13000,  # 5
            0,  # 6
            0,  # 7
            0,  # 8
            self.init_donation_pool,  # 9
        ]

        self.token = SKTL.deploy({"from": get_account(0)})

        for i in range(1, len(self.init_acc_tokens)):
            if (self.init_acc_tokens[i] > 0):
                self.token.transfer(get_account(i), self.init_acc_tokens[i] * DECIMALS)

    def print_current_status(self, transfered_record, reward_record):
        for i in range(10):
            print(
                f"{i}: bal:{self.token.balanceOf(get_account(i))}, tran={transfered_record[i]}, rew_bal:{self.token.rewardBalance(get_account(i))}, rew_rec:{reward_record[i]}"
            )

    def test_random_transfer_and_reward(self):
        random.seed('a')
        self.init_acc_tokens[0] = 100 * 10 ** 6 - sum(self.init_acc_tokens[1:])
        transfered_record = defaultdict(int)  # {account => amt}
        reward_record = defaultdict(int)  # {account => amt}

        for loop in range(20):
            # TEST transfer
            fromacc = random.randint(1, 9)
            toacc = random.randint(1, 9)

            while toacc == fromacc:
                toacc = random.randint(1, 9)

            if self.token.balanceOf(get_account(fromacc)) == 0:
                continue

            transfer_pct = random.random()
            transfer_amt = int(
                self.token.balanceOf(get_account(fromacc)) * transfer_pct
            )
            transfered_record[fromacc] -= transfer_amt
            transfered_record[toacc] += transfer_amt
            print()
            print(f"***Test Transfer {loop=} {fromacc=} {toacc=} {transfer_amt=}***")

            self.token.transfer(
                get_account(toacc), transfer_amt, {"from": get_account(fromacc)}
            )

            for i in (fromacc, toacc):
                self.assertIntAlmostEqual(
                    self.token.balanceOf(get_account(i)),
                    self.init_acc_tokens[i] * DECIMALS
                    + transfered_record[i]
                    + reward_record[i],
                    f"{loop=}: acount[{i}] balance not match after transfer",
                )
            print('==After Transfer==')
            self.print_current_status(transfered_record, reward_record)

            # TEST Reward
            reward_amt = int(1000000 * random.random() * DECIMALS)

            print()
            print(f"***Test reward {loop=} {reward_amt=} {self.token.totalSupply()=}***")

            for i in range(10):
                tot_balance = self.token.balanceOf(
                    get_account(i)
                ) + self.token.rewardBalance(get_account(i))
                reward_record[i] += int(
                    reward_amt * tot_balance / self.token.totalSupply()
                )
            self.token.increaseReward(reward_amt, {"from": get_account(0)})
            print('==After Reward==')
            self.print_current_status(transfered_record, reward_record)

            # skip 1, because it's the owner
            for i in range(1, 10):
                tot_balance = self.token.balanceOf(
                    get_account(i)
                ) + self.token.rewardBalance(get_account(i))
                if tot_balance == 0:
                    continue
                self.assertIntAlmostEqual(
                    self.token.balanceOf(get_account(i))
                    + self.token.rewardBalance(get_account(i)),
                    self.init_acc_tokens[i] * DECIMALS
                    + transfered_record[i]
                    + reward_record[i],
                    f"{loop=}: acount[{i}] balance not match after reward",
                )
