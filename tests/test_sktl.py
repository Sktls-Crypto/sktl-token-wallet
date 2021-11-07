import unittest

import brownie
from brownie import SKTL

from scripts.helpful_scripts import get_account

DECIMALS = 10**18


def round_int_by_decimal_places(value: int, places: int):
    return round(value / pow(10, places))


class TestSKTLSimpleDvd(unittest.TestCase):

    def assertIntAlmostEqual(self, value1, value2, places: int = 2):
        self.assertEqual(
            round_int_by_decimal_places(value1, places),
            round_int_by_decimal_places(value2, places),
        )

    def setUp(self):
        print(get_account(0))
        self.token = SKTL.deploy(4000 * DECIMALS, {"from": get_account(0)})
        self.token.transfer(get_account(1), 1000 * DECIMALS)
        self.token.transfer(get_account(2), 1000 * DECIMALS)

    def test_init_wallets(self):
        self.assertEqual(
            self.token.balanceOf(get_account(0)),
            2000 * DECIMALS,
            "original account balance failed after init transfer",
        )
        self.assertEqual(
            self.token.balanceOf(get_account(1)),
            1000 * DECIMALS,
            "original account1 balance failed after init transfer",
        )
        self.assertEqual(
            self.token.balanceOf(get_account(2)),
            1000 * DECIMALS,
            "original account2 balance failed after init transfer",
        )

    def test_init_reward_tokens(self):
        # check the rewardToken
        total_reward_token = self.token.totalRewardToken()
        half_token = int(total_reward_token / 2)
        quarter_token = int(total_reward_token / 4)

        self.assertEqual(
            int(self.token.rewardTokenBalance(get_account(0)) / DECIMALS),
            int(half_token / DECIMALS),
            "Failed in init rewardToken",
        )

        self.assertEqual(
            int(self.token.rewardTokenBalance(get_account(1)) / DECIMALS),
            int(quarter_token / DECIMALS),
            "Failed in init rewardToken",
        )

        self.assertEqual(
            int(self.token.rewardTokenBalance(get_account(2)) / DECIMALS),
            int(quarter_token / DECIMALS),
            "Failed in init rewardToken",
        )

    def test_simple_rewards(self):
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
            250 * DECIMALS,
        )

        self.assertIntAlmostEqual(self.token.rewardBalance(get_account(2)),
                                  250 * DECIMALS)

    def test_second_rewards(self):
        self.token.increaseReward(4000 * DECIMALS)
        self.token.increaseReward(8000 * DECIMALS)

        self.assertEqual(
            self.token.scaledRewardPerToken(),
            12000 * DECIMALS * DECIMALS / self.token.totalRewardToken(),
        )

        self.assertEqual(
            self.token.rewardBalance(get_account(0)),
            0,
        )

        # owner has all the rewards so far
        self.assertEqual(
            self.token.balanceOf(get_account(0)),
            14000 * DECIMALS,
        )

        self.assertEqual(
            self.token.rewardBalance(get_account(1)),
            3000 * DECIMALS,
        )
        self.assertIntAlmostEqual(
            self.token.rewardBalance(get_account(2)),
            3000 * DECIMALS,
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
            self.token.transfer(get_account(5), 1000*DECIMALS, {"from": get_account(0)})

        # can't pause twice
        with brownie.reverts():
            self.token.pause({"from": get_account(0)})

        # non-owner can't unpause
        with brownie.reverts():
            self.token.unpause({"from": get_account(1)})

        self.token.unpause({"from": get_account(0)})
        self.test_second_transfer()  # transfer test normal
