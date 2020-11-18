[![Build Status](https://travis-ci.com/Kenneth-Macharia/BlockChain-App.svg?branch=master)](https://travis-ci.com/Kenneth-Macharia/BlockChain-App)
[![Coverage Status](https://coveralls.io/repos/github/Kenneth-Macharia/BlockChain-App/badge.svg?branch=master&service=github)](https://coveralls.io/github/Kenneth-Macharia/BlockChain-App?branch=master)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/2aeb21c8472244498f1c634303d3d105)](https://www.codacy.com/manual/Kenneth-Macharia/BlockChain-App?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Kenneth-Macharia/BlockChain-App&amp;utm_campaign=Badge_Grade)

# Blockchain Application

- A web app that implements land records as a blockchain.
- Blockchains offer improved security against records tampering making them ideal to safeguard ownership records of high-value assets.
- They also give a history of transactions that have occured on a particular asset rather than just the asset's current ownership state.

## The Components

- The application is made up of the following containerized services:

        1. A node.js (express) service which renders the UI and can
        be used to link the app to other external applications via
        APIs.

        2. A flask-restful backend service which secures the blockchain and
        co-ordinates data flow between the Node service and the backend and across the blockchain peer network.

        3. A Redis cache and queue service between the node and flask services. The cache keep a simplified copy of the blockchain records thus offering fast record look-ups without having to hit the backend DB. The cache is updated whenever a new block/ transaction is added to the blockchain. The queue holds new transactions captured by the node service before being persisted to the backend DB, ensuring asynchronous data capture. Transactions are popped from the queue using a separate thread running in the flask service.

        4. A MongoDB database service: the backend main storage, which holds the entire blockchain for the hub.

- The services 1 & 2 will be packaged into Docker images and deployed to an image registry using Travis CI, after automated tests have pass.
- They can then be pulled into a cluster environment alongside official images for the two data stores 3 & 4 and orchestrated to achieve the apps functionality.

## App Implementation Scenario

- Multiple hubs (each containing a 3-node cluster) can be spun up to create a blockchain peer network.
- Each hub will run the application on it's cluster and store it's own blockchain of the records.
- Record queries as well as additions can be perfomed at each of the hubs.
- Each hub will automatically sync with the other peer hubs via an API in the falsk service, before forging a new block/ transaction, to gurantee the blockchain's validity across the peer network.
