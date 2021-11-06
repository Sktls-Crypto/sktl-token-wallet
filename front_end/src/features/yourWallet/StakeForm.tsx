import React, { useEffect, useState } from "react"
import { SliderInput } from "../../components"
import { useEthers, useTokenBalance, useNotifications } from "@usedapp/core"
import { formatUnits } from "@ethersproject/units"
import {
  Button,
  CircularProgress,
  Snackbar,
  makeStyles,
} from "@material-ui/core"
import { Token } from "../Main"
import { useStakeTokens } from "../../hooks"
import { utils } from "ethers"
import Alert from "@material-ui/lab/Alert"
import "../../App.css"

// This is the typescript way of saying this compent needs this type
export interface StakeFormProps {
  token: Token
}

const useStyles = makeStyles((theme) => ({
  container: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: theme.spacing(2),
    width: "100%",
  },
  slider: {
    width: "100%",
    maxWidth: "400px",
  },
}))

// token is getting passed in as a prop
// in the ping brackets is an object/variable 
// That object is of the shape StakeFormProps
export const StakeForm = ({ token }: StakeFormProps) => {
  const { address: tokenAddress, name } = token

  const { account } = useEthers()
  const tokenBalance = useTokenBalance(tokenAddress, account)
  const { notifications } = useNotifications()

  const classes = useStyles()

  const { send: withdrawSend, state: withdrawState } =
    useStakeTokens(tokenAddress)

  /*
  const formattedTokenBalance: number = tokenBalance
    ? parseFloat(formatUnits(tokenBalance, 18))
    : 0
   */

  const handleWithdrawSubmit = () => {
    //const amountAsWei = utils.parseEther(amount.toString())
    return withdrawSend();
  }

  /*
  const [amount, setAmount] =
    useState<number | string | Array<number | string>>(0)
   */

  //const [showErc20ApprovalSuccess, setShowErc20ApprovalSuccess] = useState(false)
  //const [showStakeTokensSuccess, setShowStakeTokensSuccess] = useState(false)
  const [showWithdrawSuccess, setWithdrawSuccess] = useState(false)

  const handleCloseSnack = () => {
    // showErc20ApprovalSuccess && setShowErc20ApprovalSuccess(false)
    // showStakeTokensSuccess && setShowStakeTokensSuccess(false)
    showWithdrawSuccess && setWithdrawSuccess(false);
  }

  useEffect(() => {
    if (
      notifications.filter(
        (notification) =>
          notification.type === "transactionSucceed" &&
          notification.transactionName === "withdraw rewards"
      ).length > 0
    ) {
      setWithdrawSuccess(true)
    }
  }, [notifications, showWithdrawSuccess])

  // const isMining = stakeTokensState.status === "Mining"

  // const hasZeroBalance = formattedTokenBalance === 0
  // const hasZeroAmountSelected = parseFloat(amount.toString()) === 0

  return (
    <>
      <div className={classes.container}>
          {/*
        <SliderInput
          label={`Stake ${name}`}
          maxValue={formattedTokenBalance}
          id={`slider-input-${name}`}
          className={classes.slider}
          value={amount}
          onChange={setAmount}
          disabled={isMining || hasZeroBalance}
        />
            */}
        <Button
          color="primary"
          variant="contained"
          size="large"
          onClick={handleWithdrawSubmit}
            disabled={false /*isMining || hasZeroAmountSelected */}
        >
          {"Claim Rewards"}
        </Button>
      </div>
      <Snackbar
        open={showWithdrawSuccess}
        autoHideDuration={5000}
        onClose={handleCloseSnack}
      >
        <Alert onClose={handleCloseSnack} severity="success">
            Withdraw Success!
        </Alert>
      </Snackbar>
        {/*
      <Snackbar
        open={showStakeTokensSuccess}
        autoHideDuration={5000}
        onClose={handleCloseSnack}
      >
        <Alert onClose={handleCloseSnack} severity="success">
          Tokens staked successfully!
        </Alert>
      </Snackbar>
          */}
    </>
  )
}
