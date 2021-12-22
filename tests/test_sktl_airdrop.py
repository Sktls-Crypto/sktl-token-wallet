import unittest
import brownie
from brownie import SKTL, SktlAirdrop
from scripts.helpful_scripts import get_account

DECIMALS = 10 ** 18
SCALING = 10 ** 36


class TestSktlAirdrop(unittest.TestCase):
    def setUp(self):
        self.token = SKTL.deploy({"from": get_account()})
        self.airdrop = SktlAirdrop.deploy(self.token, {"from": get_account()})

    def test_airdrop(self):
        ACC_BEGIN = 1
        ACC_END = 10

        self.assertEqual(self.token.balanceOf(get_account(0)), 200 * 10 ** 6 * DECIMALS)

        for i in range(ACC_BEGIN, ACC_END):
            self.assertEqual(
                self.token.balanceOf(get_account(i)),
                0,
                f"account[{i}] balance not zero",
            )

        self.token.approve(
            self.airdrop, self.token.balanceOf(get_account(0)), {"from": get_account()}
        )

        dropamt = 1234 * DECIMALS
        self.airdrop.airDrop(
            [get_account(i) for i in range(ACC_BEGIN, ACC_END)],
            dropamt,
            {"from": get_account(0)},
        )

        for i in range(ACC_BEGIN, ACC_END):
            self.assertEqual(
                self.token.balanceOf(get_account(i)),
                dropamt,
                f"account[{i}] balance failed airdrop",
            )
