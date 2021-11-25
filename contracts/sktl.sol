// Contract SKTL

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.10;

import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Pausable.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Capped.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/draft-ERC20Permit.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Votes.sol";

contract SKTL is
    ERC20,
    Ownable,
    ERC20Permit,
    ERC20Votes,
    ERC20Pausable,
    ERC20Capped
{
    uint256 public constant scaling = 10 ** 36; // make sure totalRewardToken * scaling is still less than 2^256

    // 3B fixed, to calculate the weight to payout rewards, set the accomodate the future max tokens
    uint256 public constant totalRewardToken = 3000 * 10**6 * 10**18;

    uint256 private _scaledRewardPerRewardToken;
    mapping(address => uint256) private _scaledRewardCreditedTo;
    mapping(address => uint256) private _rewardTokenBalance;
    uint256 private _scaledRemainder = 0;
    bool private _transferHookEnabled = true;

    constructor()
        ERC20("Skytale", "SKTL")
        ERC20Capped(300000000000000000000000000) // 300MM max
        ERC20Permit("Skytale")
    {
        require(
            owner() == _msgSender(),
            "owner is not the same as _msgSender()"
        );

        // owner() will own the unclaimed tokens
        _mint(owner(), 200000000000000000000000000); // initial 200MM supply
        _rewardTokenBalance[owner()] = totalRewardToken;
    }

    function rewardBalance(address account)
        public
        view
        virtual
        returns (uint256)
    {
        uint256 scaledOwed = _scaledRewardPerRewardToken -
            _scaledRewardCreditedTo[account];
        return (_rewardTokenBalance[account] * scaledOwed) / scaling;
    }

    function _update(address account) internal {
        uint256 owed = rewardBalance(account);
        if (owed > 0) {
            _transferHookEnabled = false;
            _transfer(owner(), account, owed);
            _transferHookEnabled = true;
        }
        _scaledRewardCreditedTo[account] = _scaledRewardPerRewardToken;
    }

    function transferOwnership(address newOwner)
        public
        virtual
        override
        onlyOwner
    {
        _update(newOwner);
        require(
            balanceOf(newOwner) == 0,
            "newOwner is required to hold no tokens"
        );

        _update(owner()); // make sure transfer full balance of owner()

        _transferHookEnabled = false;
        _transfer(owner(), newOwner, balanceOf(owner()));
        _transferHookEnabled = true;

        _rewardTokenBalance[newOwner] = _rewardTokenBalance[owner()];
        _rewardTokenBalance[owner()] = 0;
        _scaledRewardCreditedTo[newOwner] = _scaledRewardPerRewardToken;

        super.transferOwnership(newOwner);
    }

    function _beforeTokenTransfer(
        address from,
        address to,
        uint256 value
    ) internal virtual override(ERC20, ERC20Pausable) {
        super._beforeTokenTransfer(from, to, value); // this will call ERC20._beforeTokenTransfer
        if (!_transferHookEnabled) return;

        if (from == address(0))
            // minting
            return;

        _update(from);
        _update(to);
    }

    function _afterTokenTransfer(
        address from,
        address to,
        uint256 value
    ) internal virtual override(ERC20, ERC20Votes) {
        super._afterTokenTransfer(from, to, value);
        if (!_transferHookEnabled) return;

        if (from == address(0))
            // minting
            return;

        uint256 rewardTokenTransfered = (value * totalRewardToken) / totalSupply();

        _rewardTokenBalance[from] -= rewardTokenTransfered;
        _rewardTokenBalance[to] += rewardTokenTransfered;
    }

    function increaseReward(uint256 amount) public onlyOwner {
        _mint(owner(), amount);

        // scale the deposit and add the previous remainder
        uint256 scaledAvailable = (amount * scaling) + _scaledRemainder;
        _scaledRewardPerRewardToken += scaledAvailable / totalRewardToken;
        _scaledRemainder = scaledAvailable % totalRewardToken;
        _scaledRewardCreditedTo[owner()] = _scaledRewardPerRewardToken;
    }

    function withdraw() public {
        require(rewardBalance(_msgSender()) > 0, "No rewards left to withdraw");
        _update(_msgSender());
    }

    function rewardTokenBalance(address addr)
        public
        view
        virtual
        returns (uint256)
    {
        return _rewardTokenBalance[addr];
    }

    function _mint(address account, uint256 amount)
        internal
        virtual
        override(ERC20, ERC20Capped, ERC20Votes)
    {
        super._mint(account, amount);
    }

    function _burn(address account, uint256 amount)
        internal
        override(ERC20, ERC20Votes)
    {
        super._burn(account, amount);
    }

    function pause() public onlyOwner {
        super._pause();
    }

    function unpause() public onlyOwner {
        super._unpause();
    }
}
