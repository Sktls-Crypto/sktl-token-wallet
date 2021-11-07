// Contract SKTL

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract SKTL is ERC20, Ownable {

    uint256 public constant maxSupply = 300000000000000000000000000; // 300MM
    uint256 public constant scaling = 1000000000000000000; // 10^18
    uint256 public constant totalRewardToken = 1000000000000000000000000000; // 10B fixed

    uint256 private _scaledRewardPerToken;
    mapping(address => uint256) private _scaledRewardCreditedTo;
    mapping(address => uint256) private _rewardTokenBalance;
    uint256 private _scaledRemainder = 0;
    bool private _enableHook = true;


    constructor(uint256 initialSupply) ERC20("Skytale", "SKTL") {
        require(owner() == _msgSender(), "owner is not the same as _msgSender()");

        // owner() will own the unclaimed tokens
        _mint(owner(), initialSupply);
        _rewardTokenBalance[owner()] = totalRewardToken;
    }

    function rewardBalance(address account) public view virtual returns (uint256) {
        uint256 scaledOwed = _scaledRewardPerToken - _scaledRewardCreditedTo[account];
        return (_rewardTokenBalance[account] * scaledOwed) / scaling;
    }

    function _update(address account) internal {
        uint256 owed = rewardBalance(account);
        if (owed > 0) {
            // this is _transfer() without hook, may need to handler revert
            _enableHook = false;
            _transfer(owner(), account, owed);
            _enableHook = true;
        }
        _scaledRewardCreditedTo[account] = _scaledRewardPerToken;
    }

    function transferOwnership(address newOwner) public virtual override onlyOwner {
        _update(newOwner);
        require(balanceOf(newOwner) == 0, "newOwner is required to hold no tokens");

        _update(owner()); // make sure transfer full balance of owner()
        _transfer(owner(), newOwner, balanceOf(owner()));

        super.transferOwnership(newOwner);
    }

    function _beforeTokenTransfer(address from, address to, uint256 value)
    internal virtual override
    {
        super._beforeTokenTransfer(from, to, value);
        if (!_enableHook) return;

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
    ) internal virtual override
    {
        super._afterTokenTransfer(from, to, value);
        if (!_enableHook) return;

        if (from == address(0))
            // miniting
            return;

            uint256 scaledTransferPct = (value * scaling) / (balanceOf(from) + value) ;
            uint256 rewardTokenTransfered = (scaledTransferPct * _rewardTokenBalance[from]) / scaling;
            _rewardTokenBalance[from] -= rewardTokenTransfered;
            _rewardTokenBalance[to] += rewardTokenTransfered;
    }

    function _mint(address account, uint256 amount) internal virtual override {
        require(ERC20.totalSupply() + amount <= maxSupply, "maxSupply exceeded");
        super._mint(account, amount);
    }

    function increaseReward(uint256 amount) public onlyOwner{
        _mint(owner(), amount);

        // scale the deposit and add the previous remainder
        uint256 scaledAvailable = (amount * scaling) + _scaledRemainder;
        _scaledRewardPerToken += scaledAvailable / totalRewardToken;
        _scaledRemainder = scaledAvailable % totalRewardToken;
        _scaledRewardCreditedTo[owner()] = _scaledRewardPerToken;
    }

    function withdraw() public {
        require(rewardBalance(_msgSender()) > 0, "No rewards left to withdraw");
        _update(_msgSender());
    }

    function scaledRewardPerToken() public view virtual returns (uint256) {
        return _scaledRewardPerToken;
    }

    function rewardTokenBalance(address addr) public view virtual returns(uint256) {
        return _rewardTokenBalance[addr];
    }
}
