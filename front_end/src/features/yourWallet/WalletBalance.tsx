import React from "react";
import { Token } from "../Main";
import { useEthers, useTokenBalance } from "@usedapp/core";
import { formatUnits } from "@ethersproject/units";
import { BalanceMsg } from "../../components";

export interface WalletBalanceProps {
  token: Token;
}

export const WalletBalance = ({ token }: WalletBalanceProps) => {
  const { image, address, name } = token;

  console.log(`WalletBalance address=${address} name=${name}`);

  const { account } = useEthers();
  const tokenBalance = useTokenBalance(address, account);
  const formattedTokenBalance: number = tokenBalance
    ? parseFloat(formatUnits(tokenBalance, 18))
    : 0;

  return (
      <div>
            <BalanceMsg
              label={`Your ${name} balance`}
              amount={formattedTokenBalance}
              tokenImgSrc={image}
            />

          {/*
          <p>
            <BalanceMsg
              label={`Your ${name} reward balance`}
              amount={formattedRewardTokenBalance}
              tokenImgSrc={image}
            />
          </p>
            */}
      </div>

  );
};
