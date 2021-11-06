import React, { useState, useEffect } from "react"
import {
  Button,
  CircularProgress,
  Snackbar,
  makeStyles,
} from "@material-ui/core"
import { Token } from "../Main"
import { useWithdrawRewards, useStakingBalance } from "../../hooks"
import Alert from "@material-ui/lab/Alert"
import { useNotifications } from "@usedapp/core"
import { formatUnits } from "@ethersproject/units"
import { BalanceMsg } from "../../components"

export interface claimFormProps {
  token: Token
}

const useStyles = makeStyles((theme) => ({
  contentContainer: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "flex-start",
    gap: theme.spacing(2),
  },
}))

export const ClaimRewards = ({ token }: claimFormProps) => {
  const { image, address: tokenAddress, name } = token

  const { notifications } = useNotifications()

  const balance = useStakingBalance(tokenAddress)

  const formattedBalance: number = balance
    ? parseFloat(formatUnits(balance, 18))
    : 0

  const { send: withdrawRewardsSend, state: withdrawRewardsState } =
    useWithdrawRewards()

  const withdrawRewardsSubmit = () => {
      console.log(`withdrawRewardsSubmit: ${tokenAddress}`);
    return withdrawRewardsSend()
  }

  const [showWithdrawSuccess, setShowWithdrawSuccess] = useState(false)

  const handleCloseSnack = () => {
    showWithdrawSuccess && setShowWithdrawSuccess(false)
  }

  useEffect(() => {
    if (
      notifications.filter(
        (notification) =>
          notification.type === "transactionSucceed" &&
          notification.transactionName === "withdraw tokens"
      ).length > 0
    ) {
      !showWithdrawSuccess && setShowWithdrawSuccess(true)
    }
  }, [notifications, showWithdrawSuccess])

  const classes = useStyles()

  return (
    <>
      <div className={classes.contentContainer}>
        <BalanceMsg
          label={`Your reward ${name} balance`}
          amount={formattedBalance}
          tokenImgSrc={image}
        />
        <Button
          color="primary"
          variant="contained"
          size="large"
          onClick={withdrawRewardsSubmit}
          disabled={false}
        >
          { `CLAIM REWARDS`}
        </Button>
      </div>
      <Snackbar
        open={showWithdrawSuccess}
        autoHideDuration={5000}
        onClose={handleCloseSnack}
      >
        <Alert onClose={handleCloseSnack} severity="success">
          Tokens claimed successfully!
        </Alert>
      </Snackbar>
    </>
  )
}
