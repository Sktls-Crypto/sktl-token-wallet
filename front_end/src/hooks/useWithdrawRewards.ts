import { useContractFunction, useEthers } from "@usedapp/core"
import SKTL from "../chain-info/SKTL.json"
import { utils, constants } from "ethers"
import { Contract } from "@ethersproject/contracts"
import networkMapping from "../chain-info/map.json"

/**
 * Expose { send, state } object to facilitate unstaking the user's tokens from the SKTL contract
 */
export const useWithdrawRewards = () => {
  const { chainId } = useEthers()

  const { abi } = SKTL
  const sktlContractAddr = chainId ? networkMapping[String(chainId)]["SKTL"][0] : constants.AddressZero
  console.log(`useWithdrawRewards: sktlContractAddr=${sktlContractAddr}`);

  const sktlInterface = new utils.Interface(abi)

  const tokenFarmContract = new Contract(
    sktlContractAddr,
    sktlInterface
  )

  return useContractFunction(tokenFarmContract, "withdraw", {
    transactionName: "withdraw tokens",
  })
}
