// Contract SKTL

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.10;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract SktlAirdrop is Ownable {
    IERC20 private _token;
    mapping(address => uint256) private _droppedAmounts;

    constructor(IERC20 token) {
        require(
            owner() == _msgSender(),
            "owner is not the same as _msgSender()"
        );

        _token = token;
    }

    function airDrop(address[] memory receivers, uint256 amount)
        public
        virtual
        onlyOwner
    {
        require(
            _token.balanceOf(owner()) >= (receivers.length * amount),
            "Owner doesn't have enough balance to airdrop"
        );

        for (uint256 i = 0; i < receivers.length; i++) {
            if (_droppedAmounts[receivers[i]] == 0) {
                _token.transferFrom(owner(), receivers[i], amount);
                _droppedAmounts[receivers[i]] = amount;
            }
        }
    }
}
