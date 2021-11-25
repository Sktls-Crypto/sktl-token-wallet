import unittest

import brownie
from brownie import SKTL

from scripts.helpful_scripts import get_account

DECIMALS = 10**18
SCALING = 10**36


class TestSKTLSimpleDvd(unittest.TestCase):

    def assertIntAlmostEqual(
            self,
            value1,
            value2,
            msg: str = None,
            places: int = 10,  # decimal places in %
    ):
        self.assertLessEqual(value1 / value2, 1 + (10**-places))
        self.assertGreaterEqual(value1 / value2, 1 - (10**-places))

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
            (self.init_token - self.init_donation_pool -
             sum(self.init_acc_tokens) + rewards) * DECIMALS,
        )

        for i in range(1, len(self.init_acc_tokens)):
            self.assertIntAlmostEqual(
                self.token.rewardBalance(get_account(i)),
                int((rewards * self.init_acc_tokens[i] * DECIMALS) //
                    self.init_token),
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
            (self.init_token - self.init_donation_pool -
             sum(self.init_acc_tokens) + sum(rewards)) * DECIMALS,
        )

        for i in range(1, len(self.init_acc_tokens)):
            self.assertIntAlmostEqual(
                self.token.rewardBalance(get_account(i)),
                int((sum(rewards) * self.init_acc_tokens[i] * DECIMALS) /
                    self.init_token),
                f"account[{i}] reward balance doesn't match after multiple rewards",
            )

    def test_transfer_after_rewards(self):
        # test reward, then transfer, then reward
        rewards = 1000
        transfer = 301.0000001

        self.token.increaseReward(rewards * DECIMALS)

        self.token.transfer(get_account(3), transfer * DECIMALS,
                            {"from": get_account(2)})

        # make sure the rewardBalance is Zero
        self.assertEqual(self.token.rewardBalance(get_account(2)), 0)
        self.assertEqual(self.token.rewardBalance(get_account(3)), 0)

        balance2 = (self.init_acc_tokens[2] *
                    (1 + rewards / self.init_token)) - transfer
        balance3 = (self.init_acc_tokens[3] *
                    (1 + rewards / self.init_token)) + transfer

        self.assertIntAlmostEqual(
            self.token.balanceOf(get_account(2)),
            balance2 * DECIMALS,
        )
        self.assertIntAlmostEqual(
            self.token.balanceOf(get_account(3)),
            balance3 * DECIMALS,
        )

    def test_should_fail(self):
        # make sure only owner can reward
        with brownie.reverts():
            self.token.increaseReward(1000 * DECIMALS, {"from": get_account(2)})

        # transfer more than it owns
        with brownie.reverts():
            self.token.transfer(get_account(1),
                                self.init_acc_tokens[2] * 2 * DECIMALS,
                                {"from": get_account(2)})

    def test_set_owner(self):
        rewards = [1000, 2000]
        self.token.increaseReward(rewards[0] * DECIMALS,
                                  {"from": get_account(0)})

        with brownie.reverts():
            self.token.transferOwnership(get_account(2),
                                         {"from": get_account(1)})

        # make sure new owner can't hold tokens
        with brownie.reverts():
            self.token.transferOwnership(get_account(4),
                                         {"from": get_account(0)})

        self.token.transferOwnership(get_account(8), {"from": get_account(0)})

        # make old owner can't reward
        with brownie.reverts():
            self.token.increaseReward(rewards[0] * DECIMALS,
                                      {"from": get_account(0)})

        # new owner can reward
        self.token.increaseReward(rewards[1] * DECIMALS,
                                  {"from": get_account(8)})

        scaled_reward_token = sum(
            rewards) * DECIMALS * self.init_acc_tokens[1] / self.init_token

        self.assertEqual(
            self.token.rewardBalance(get_account(1)),
            scaled_reward_token,
        )

        self.token.withdraw({"from": get_account(1)})

        self.assertEqual(
            self.token.balanceOf(get_account(1)),
            self.init_acc_tokens[1] * DECIMALS + scaled_reward_token,
        )

    def test_transfer_from_using_allowance(self):
        transfer = 300

        # not allowed yet
        with brownie.reverts():
            self.token.transferFrom(get_account(1), get_account(3),
                                    1000 * DECIMALS, {"from": get_account(0)})

        self.token.approve(get_account(3), transfer * DECIMALS,
                           {"from": get_account(1)})

        # not allow over transferFrom
        with brownie.reverts():
            self.token.transferFrom(get_account(1), get_account(3),
                                    (transfer + 1) * DECIMALS,
                                    {"from": get_account(3)})

        self.token.transferFrom(get_account(1), get_account(4),
                                transfer * DECIMALS, {"from": get_account(3)})

        balance1 = (self.init_acc_tokens[1] - transfer)
        self.assertEqual(
            self.token.balanceOf(get_account(1)),
            balance1 * DECIMALS,
        )

        balance4 = (self.init_acc_tokens[4] + transfer)
        self.assertEqual(
            self.token.balanceOf(get_account(4)),
            balance4 * DECIMALS,
        )

        self.assertEqual(self.token.rewardBalance(get_account(1)), 0)
        self.assertEqual(self.token.rewardBalance(get_account(4)), 0)

        # make sure the simple reward works
        reward = 1000
        self.token.increaseReward(reward * DECIMALS)

        self.assertEqual(
            self.token.rewardBalance(get_account(0)),
            0,
        )

        self.assertIntAlmostEqual(
            self.token.rewardBalance(get_account(1)),
            reward * DECIMALS * balance1 / self.init_token,
        )
        self.assertIntAlmostEqual(
            self.token.rewardBalance(get_account(4)),
            reward * DECIMALS * balance4 / self.init_token,
        )
        self.assertIntAlmostEqual(
            self.token.rewardBalance(get_account(3)),
            reward * DECIMALS * self.init_acc_tokens[3] / self.init_token,
        )

    def test_transfer_balance_plus_reward(self):
        rewards = 3000
        self.token.increaseReward(rewards * DECIMALS)

        self.assertEqual(
            self.token.balanceOf(get_account(1)),
            self.init_acc_tokens[1] * DECIMALS,
        )
        scaled_reward_balance1 = rewards * DECIMALS * self.init_acc_tokens[
            1] / self.init_token
        self.assertEqual(
            self.token.rewardBalance(get_account(1)),
            scaled_reward_balance1,
        )
        total_transfer = self.init_acc_tokens[
            1] * DECIMALS + scaled_reward_balance1
        self.token.transfer(
            get_account(3), total_transfer,
            {"from": get_account(1)})  # transfer balance + reward

        self.assertEqual(
            self.token.balanceOf(get_account(1)),
            0,
        )
        self.assertEqual(
            self.token.rewardBalance(get_account(1)),
            0,
        )

        scaled_reward_balance3 = rewards * DECIMALS * self.init_acc_tokens[
            3] / self.init_token
        self.assertEqual(
            self.token.balanceOf(get_account(3)),
            self.init_acc_tokens[3] * DECIMALS + total_transfer +
            scaled_reward_balance3,
        )
        self.assertEqual(
            self.token.rewardBalance(get_account(3)),
            0,
        )

    def test_transferfrom_balance_plus_reward(self):
        rewards = 3000
        self.token.increaseReward(rewards * DECIMALS)
        self.assertEqual(
            self.token.balanceOf(get_account(1)),
            self.init_acc_tokens[1] * DECIMALS,
        )
        scaled_reward_balance1 = rewards * DECIMALS * self.init_acc_tokens[
            1] / self.init_token
        self.assertEqual(
            self.token.rewardBalance(get_account(1)),
            scaled_reward_balance1,
        )

        total_transfer = self.init_acc_tokens[
            1] * DECIMALS + scaled_reward_balance1
        self.token.approve(get_account(4), total_transfer,
                           {"from": get_account(1)})

        # transfer balance + reward
        self.token.transferFrom(get_account(1), get_account(3), total_transfer,
                                {"from": get_account(4)})

        self.assertEqual(
            self.token.balanceOf(get_account(1)),
            0,
        )
        self.assertEqual(
            self.token.rewardBalance(get_account(1)),
            0,
        )

        scaled_reward_balance3 = rewards * DECIMALS * self.init_acc_tokens[
            3] / self.init_token
        self.assertEqual(
            self.token.balanceOf(get_account(3)),
            self.init_acc_tokens[3] * DECIMALS + total_transfer +
            scaled_reward_balance3,
        )
        self.assertEqual(
            self.token.rewardBalance(get_account(3)),
            0,
        )

    def test_max_supply(self):
        three_mm = 300 * 10**6
        self.token.increaseReward((three_mm - self.init_token) * DECIMALS)

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
        self.test_transfer_after_rewards()  # transfer test normal
