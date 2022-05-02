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
  readOnlyChainId: ChainId.BSCTestnet,
  readOnlyUrls: {
    [ChainId.BSCTestnet]: 'https://data-seed-prebsc-1-s1.binance.org:8545/',
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
