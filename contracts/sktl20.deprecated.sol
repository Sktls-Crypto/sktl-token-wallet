// contracts/GLDToken.sol
// SPDX-License-Identifier: MIT

// DEPRECATED.  Just a record for older version

pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

// import "./contracts/token/ERC20/ERC20.sol";

contract Sktl20 is ERC20 {
    uint256 public constant scaling = 1000000000000000000; // 10^18
    uint256 public constant totalRewardToken = 1000000000000000000000000000; // about 10B, and should be fixed

    address internal _owner; // owner who can mint
    address internal _vault; // vault address to store the rewards & donations
    uint256 public scaledRewardPerToken;
    mapping(address => uint256) public scaledRewardCreditedTo;
    mapping(address => uint256) public rewardTokenBalance;
    uint256 public scaledRemainder = 0;
    bool private _enable_hook = true;

    constructor(uint256 initialSupply) ERC20("Skytale", "sktb") {
        _owner = _msgSender();
        _vault = _msgSender();
        _mint(_vault, initialSupply);
        rewardTokenBalance[_msgSender()] = totalRewardToken;
    }

    function reward_balance(address account)
        public
        view
        virtual
        returns (uint256)
    {
        uint256 scaledOwed = scaledRewardPerToken -
            scaledRewardCreditedTo[account];
        return (rewardTokenBalance[account] * scaledOwed) / scaling;
    }

    function _update(address account) internal {
        uint256 owed = reward_balance(account);
        if (owed > 0) {
            // this is _transfer() without hook, may need to handler revert
            _enable_hook = false;
            _transfer(_vault, account, owed);
            _enable_hook = true;
        }
        scaledRewardCreditedTo[account] = scaledRewardPerToken;
    }

    function set_owner(address new_owner) public virtual returns (bool) {
        require(
            _msgSender() == _owner,
            "Only current owner can assign a new owner"
        );

        // todo to check the validity of new_owner
        _owner = new_owner;
        return true;
    }

    function set_vault(address new_vault) public virtual returns (bool) {
        require(
            _msgSender() == _owner,
            "Only current owner can assign a new owner"
        );
        // todo to check the validity of new_vault

        _transfer(_vault, new_vault, balanceOf(_vault));
        _vault = new_vault;

        return true;
    }

    function _beforeTokenTransfer(
        address from,
        address to,
        uint256 value
    ) internal virtual override {
        super._beforeTokenTransfer(from, to, value);
        if (!_enable_hook) return;

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
    ) internal virtual override {
        super._afterTokenTransfer(from, to, value);
        if (!_enable_hook) return;

        if (from == address(0))
            // miniting
            return;

        uint256 scaledTransferPct = (value * scaling) /
            (balanceOf(from) + value);
        uint256 rewardTokenTransfered = (scaledTransferPct *
            rewardTokenBalance[from]) / scaling;
        rewardTokenBalance[from] -= rewardTokenTransfered;
        rewardTokenBalance[to] += rewardTokenTransfered;
    }

    function rewards(uint256 amount) public {
        require(_msgSender() == _owner, "Only owner can create new rewards");
        // scale the deposit and add the previous remainder
        uint256 scaledAvailable = (amount * scaling) + scaledRemainder;
        scaledRewardPerToken += scaledAvailable / totalRewardToken;
        scaledRemainder = scaledAvailable % totalRewardToken;
        _mint(_vault, amount);
        scaledRewardCreditedTo[_vault] = scaledRewardPerToken;
    }

    function withdraw() public {
        require(
            reward_balance(_msgSender()) > 0,
            "No rewards left to withdraw"
        );
        _update(_msgSender());
    }
}
