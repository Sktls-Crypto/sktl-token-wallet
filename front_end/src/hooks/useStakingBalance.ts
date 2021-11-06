import { useContractCall, useEthers } from "@usedapp/core"
import Sktl20 from "../chain-info/Sktl20.json"
import { utils, BigNumber, constants } from "ethers"
import networkMapping from "../chain-info/map.json"

/**
 * Get the staking balance of a certain token by the user in our TokenFarm contract
 * @param address - The contract address of the token
 */
export const useStakingBalance = (address: string): BigNumber | undefined => {
  const { account, chainId } = useEthers()

  const { abi } = Sktl20
  const sktl20ContractAddress = chainId ? networkMapping[String(chainId)]["Sktl20"][0] : constants.AddressZero

  const sktl20Interface = new utils.Interface(abi)

  const [stakingBalance] =
    useContractCall({
      abi: sktl20Interface,
      address: sktl20ContractAddress,
      method: "reward_balance",
      args: [account],
    }) ?? []

  return stakingBalance
}
