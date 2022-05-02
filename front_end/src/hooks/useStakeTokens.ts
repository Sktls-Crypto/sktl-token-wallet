import { useEffect, useState } from "react"
import { useContractFunction, useEthers } from "@usedapp/core"
import SKTL from "../chain-info/SKTL.json"
import Erc20 from "../chain-info/ERC20.json"
import { utils, constants } from "ethers"
import { Contract } from "@ethersproject/contracts"
import networkMapping from "../chain-info/map.json"

/**
 * This hook is a bit messy but exposes a 'send' which makes two transactions.
 * The first transaction is to approve the ERC-20 token transfer on the token's contract.
 * Upon successful approval, a second transaction is initiated to execute the transfer by the SKTL contract.
 * The 'state' returned by this hook is the state of the first transaction until that has status "Succeeded".
 * After that it is the state of the second transaction.
 * @param tokenAddress - The token address of the token we wish to stake
 */
export const useStakeTokens = (tokenAddress: string) => {
  const { chainId } = useEthers()
  const { abi } = SKTL
  const tokenFarmContractAddress = chainId ? networkMapping[String(chainId)]["SKTL"][0] : constants.AddressZero

  const tokenFarmInterface = new utils.Interface(abi)

  const tokenFarmContract = new Contract(
    tokenFarmContractAddress,
    tokenFarmInterface
  )

  const { send: withdrawSend, state: withdrawState } =
    useContractFunction(tokenFarmContract, "withdraw", {
      transactionName: "withdraw rewards",
    })

  const send = () => {
        return withdrawSend();
  }

   const [state, setState] = useState(withdrawState)
  useEffect(() => {
      if (withdrawState.status === "Success") {
          setState(withdrawState)
      } else {
          setState(withdrawState)
      }

  }, [withdrawState]);

  return { send, state };
}
