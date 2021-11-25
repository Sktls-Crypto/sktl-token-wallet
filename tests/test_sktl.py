import unittest

import brownie
from brownie import SKTL

from scripts.helpful_scripts import get_account

DECIMALS = 10**18
SCALING = 10**36


def round_int_by_decimal_places(value: int, places: int):
    return round(value / pow(10, places))


class TestSKTLSimpleDvd(unittest.TestCase):

    def assertIntAlmostEqual(self,
                             value1,
                             value2,
                             places: int = 1,
                             msg: str = None):
        self.assertEqual(
            round_int_by_decimal_places(value1, places),
            round_int_by_decimal_places(value2, places),
            msg
        )

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

    def test_init_wallets(self):
        self.assertEqual(
            self.token.balanceOf(get_account(0)),
            (self.init_token - self.init_donation_pool -
             sum(self.init_acc_tokens)) * DECIMALS,
            "original account balance failed after init transfer",
        )

        for i in range(1, len(self.init_acc_tokens)):
            self.assertEqual(
                self.token.balanceOf(get_account(i)),
                self.init_acc_tokens[i] * DECIMALS,
                f"original account[{i}] balance failed after init transfer",
            )

        self.assertEqual(
            self.token.balanceOf(get_account(self.dontation_pool_acc)),
            self.init_donation_pool * DECIMALS,
            "original donation pool balance failed after init transfer",
        )

    def test_init_reward_tokens(self):
        # check the rewardToken
        total_reward_token = self.token.totalRewardToken()
        half_token = int(total_reward_token / 2)

        self.assertEqual(
            int(
                self.token.rewardTokenBalance(
                    get_account(self.dontation_pool_acc)) / DECIMALS),
            int(half_token / DECIMALS),
            "Donation pool doesn't have half rewardToken",
        )

        for i in range(1, len(self.init_acc_tokens)):
            self.assertEqual(
                int(self.token.rewardTokenBalance(get_account(i))),
                int(((self.init_acc_tokens[i] * total_reward_token) //
                     self.init_token)),
                msg=f"account[{i}] rewardbalance doesn't match",
            )

    def test_simple_rewards(self):
        rewards = 10000
        self.token.increaseReward(rewards * DECIMALS)

        self.assertEqual(
            self.token.scaledRewardPerToken(),
            rewards * DECIMALS * SCALING // self.token.totalRewardToken(),
        )

        # owner should not have any rewardBalance
        self.assertEqual(
            self.token.rewardBalance(get_account(0)),
            0,
        )

        # owner has all the rewards so far
        self.assertEqual(
            self.token.balanceOf(get_account(0)),
            (self.init_token - self.init_donation_pool - sum(self.init_acc_tokens) + rewards) * DECIMALS,
        )

        for i in range(1, len(self.init_acc_tokens)):
            self.assertIntAlmostEqual(
                self.token.rewardBalance(get_account(i)),
                int((rewards * self.init_acc_tokens[i] * DECIMALS) // self.init_token),
                1,
                f"account[{i}] reward balance doesn't match",
            )

    def test_second_rewards(self):
        rewards = [4000, 8000]
        for i in range(len(rewards)):
            self.token.increaseReward(rewards[i] * DECIMALS)

        self.assertEqual(
            self.token.scaledRewardPerToken(),
            sum(rewards) * DECIMALS * SCALING / self.token.totalRewardToken(),
        )

        self.assertEqual(
            self.token.rewardBalance(get_account(0)),
            0,
        )

        # owner has all the rewards so far
        self.assertEqual(
            self.token.balanceOf(get_account(0)),
            (self.init_token - self.init_donation_pool - sum(self.init_acc_tokens) + sum(rewards)) * DECIMALS,
        )

        for i in range(1, len(self.init_acc_tokens)):
            self.assertIntAlmostEqual(
                self.token.rewardBalance(get_account(i)),
                int((sum(rewards) * self.init_acc_tokens[i] * DECIMALS) // self.init_token),
                1,
                f"account[{i}] reward balance doesn't match after multiple rewards",
            )

    def test_second_transfer(self):
        # test reward, then transfer, then reward
        self.token.increaseReward(1000 * DECIMALS)
        self.token.transfer(get_account(3), 500 * DECIMALS,
                            {"from": get_account(2)})

        # make sure the rewardTokenBalance is calculated correctly
        self.assertIntAlmostEqual(
            self.token.rewardTokenBalance(get_account(2)),
            750 / 1250 * self.token.rewardTokenBalance(get_account(1)))
        self.assertIntAlmostEqual(
            self.token.rewardTokenBalance(get_account(3)),
            500 / 1250 * self.token.rewardTokenBalance(get_account(1)))
        self.token.increaseReward(1000 * DECIMALS)
        self.assertEqual(
            self.token.rewardBalance(get_account(1)),
            500 * DECIMALS,
        )
        # 1250 - 500
        self.assertIntAlmostEqual(
            self.token.balanceOf(get_account(2)),
            750 * DECIMALS,
        )
        # 15% * 1000
        self.assertIntAlmostEqual(
            self.token.rewardBalance(get_account(2)),
            150 * DECIMALS,
        )
        self.assertIntAlmostEqual(
            self.token.rewardBalance(get_account(3)),
            100 * DECIMALS,
        )
        self.assertIntAlmostEqual(
            self.token.balanceOf(get_account(3)),
            500 * DECIMALS,
        )

    def test_should_fail(self):
        # make sure only owner can reward
        with brownie.reverts():
            self.token.increaseReward(1000 * DECIMALS, {"from": get_account(2)})

        # transfer more than it owns
        with brownie.reverts():
            self.token.transfer(get_account(1), 2000 * DECIMALS,
                                {"from": get_account(2)})

    def test_set_owner(self):
        with brownie.reverts():
            self.token.transferOwnership(get_account(2),
                                         {"from": get_account(1)})

        self.token.transferOwnership(get_account(4), {"from": get_account(0)})

        with brownie.reverts():
            self.token.increaseReward(1000 * DECIMALS, {"from": get_account(0)})

        self.token.increaseReward(1000 * DECIMALS, {"from": get_account(4)})

        self.assertEqual(
            self.token.rewardBalance(get_account(1)),
            250 * DECIMALS,
        )
        self.token.withdraw({"from": get_account(1)})
        self.assertEqual(
            self.token.balanceOf(get_account(1)),
            1250 * DECIMALS,
        )

    def test_transfer_from_using_allowance(self):
        with brownie.reverts():
            self.token.transferFrom(get_account(1), get_account(3),
                                    1000 * DECIMALS)

        self.token.approve(get_account(3), 500 * DECIMALS,
                           {"from": get_account(1)})

        with brownie.reverts():
            self.token.transferFrom(get_account(1), get_account(3),
                                    501 * DECIMALS, {"from": get_account(3)})

        self.token.transferFrom(get_account(1), get_account(4), 500 * DECIMALS,
                                {"from": get_account(3)})

        self.assertEqual(
            self.token.balanceOf(get_account(1)),
            500 * DECIMALS,
        )
        self.assertEqual(
            self.token.balanceOf(get_account(4)),
            500 * DECIMALS,
        )

        self.assertEqual(
            self.token.rewardBalance(get_account(1)),
            self.token.rewardBalance(get_account(4)),
        )

        # make sure the simple reward works

        self.token.increaseReward(1000 * DECIMALS)

        self.assertEqual(
            self.token.scaledRewardPerToken(),
            1000 * DECIMALS * DECIMALS / self.token.totalRewardToken(),
        )

        self.assertEqual(
            self.token.rewardBalance(get_account(0)),
            0,
        )

        # owner has all the rewards so far
        self.assertEqual(
            self.token.balanceOf(get_account(0)),
            3000 * DECIMALS,
        )

        self.assertEqual(
            self.token.rewardBalance(get_account(1)),
            125 * DECIMALS,
        )
        self.assertEqual(
            self.token.rewardBalance(get_account(4)),
            125 * DECIMALS,
        )

        self.assertIntAlmostEqual(self.token.rewardBalance(get_account(2)),
                                  250 * DECIMALS)

    def test_set_vault(self):
        with brownie.reverts():
            self.token.transferOwnership(get_account(2),
                                         {"from": get_account(1)})

        self.token.transferOwnership(get_account(4), {"from": get_account(0)})

        self.assertEqual(
            self.token.rewardBalance(get_account(4)),
            0 * DECIMALS,
        )

        self.assertEqual(
            self.token.balanceOf(get_account(4)),
            2000 * DECIMALS,
        )

        self.token.increaseReward(1000 * DECIMALS, {"from": get_account(4)})

        self.assertEqual(
            self.token.rewardBalance(get_account(1)),
            250 * DECIMALS,
        )
        self.token.withdraw({"from": get_account(1)})

        self.assertEqual(
            self.token.balanceOf(get_account(1)),
            1250 * DECIMALS,
        )

        self.assertEqual(
            self.token.balanceOf(get_account(4)),
            2750 * DECIMALS,
        )

    def test_transfer_max(self):
        self.token.increaseReward(4000 * DECIMALS)
        self.assertEqual(
            self.token.balanceOf(get_account(1)),
            1000 * DECIMALS,
        )
        self.assertEqual(
            self.token.rewardBalance(get_account(1)),
            1000 * DECIMALS,
        )
        self.token.transfer(
            get_account(3), 2000 * DECIMALS,
            {"from": get_account(1)})  # transfer balance + reward

        self.assertEqual(
            self.token.balanceOf(get_account(1)),
            0,
        )
        self.assertEqual(
            self.token.rewardBalance(get_account(1)),
            0,
        )
        self.assertEqual(
            self.token.balanceOf(get_account(3)),
            2000 * DECIMALS,
        )
        self.assertEqual(
            self.token.rewardBalance(get_account(3)),
            0,
        )

    def test_transfer_from_max(self):
        self.token.increaseReward(4000 * DECIMALS)
        self.assertEqual(
            self.token.balanceOf(get_account(1)),
            1000 * DECIMALS,
        )
        self.assertEqual(
            self.token.rewardBalance(get_account(1)),
            1000 * DECIMALS,
        )

        self.token.approve(get_account(4), 2000 * DECIMALS,
                           {"from": get_account(1)})

        # transfer balance + reward
        self.token.transferFrom(get_account(1), get_account(3), 2000 * DECIMALS,
                                {"from": get_account(4)})

        self.assertEqual(
            self.token.balanceOf(get_account(1)),
            0,
        )
        self.assertEqual(
            self.token.rewardBalance(get_account(1)),
            0,
        )
        self.assertEqual(
            self.token.balanceOf(get_account(3)),
            2000 * DECIMALS,
        )
        self.assertEqual(
            self.token.rewardBalance(get_account(3)),
            0,
        )

    def test_max_supply(self):
        three_mm = 300 * 10**6
        self.token.increaseReward((three_mm - 4000) * DECIMALS)

        with brownie.reverts():
            self.token.increaseReward(1)

    def test_pause(self):
        # non-owner can't pause
        with brownie.reverts():
            self.token.pause({"from": get_account(1)})

        # not in pause state, can't unpause
        with brownie.reverts():
            self.token.unpause({"from": get_account(0)})

        self.token.pause({"from": get_account(0)})

        # paused, can't transfer
        with brownie.reverts():
            self.token.transfer(get_account(5), 1000 * DECIMALS,
                                {"from": get_account(0)})

        # can't pause twice
        with brownie.reverts():
            self.token.pause({"from": get_account(0)})

        # non-owner can't unpause
        with brownie.reverts():
            self.token.unpause({"from": get_account(1)})

        self.token.unpause({"from": get_account(0)})
        self.test_second_transfer()  # transfer test normal
