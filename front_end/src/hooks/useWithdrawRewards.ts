import { useContractFunction, useEthers } from "@usedapp/core"
import Sktl20 from "../chain-info/Sktl20.json"
import { utils, constants } from "ethers"
import { Contract } from "@ethersproject/contracts"
import networkMapping from "../chain-info/map.json"

/**
 * Expose { send, state } object to facilitate unstaking the user's tokens from the Sktl20 contract
 */
export const useWithdrawRewards = () => {
  const { chainId } = useEthers()

  const { abi } = Sktl20
  const sktlContractAddr = chainId ? networkMapping[String(chainId)]["Sktl20"][0] : constants.AddressZero
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
