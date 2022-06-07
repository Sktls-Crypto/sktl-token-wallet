import React from "react"
import { Header } from "./features/Header"
import { Main } from "./features/Main"
import { Container } from "@material-ui/core"
import {
  ChainId,
  DAppProvider,
  // useEtherBalance,
  // useEthers,
  Config,
} from '@usedapp/core'

export const App = () => {
    const config = {
  readOnlyChainId: ChainId.BSC,
  readOnlyUrls: {
    [ChainId.BSC]: 'https://bsc-dataseed1.binance.org',
  },
}

  return (
    <DAppProvider config={config}>
      <Header />
      <Container maxWidth="md">
        <Main />
      </Container>
    </DAppProvider>
  )
}
export default App
