# Blockchain Application

[![Build Status](https://travis-ci.com/Kenneth-Macharia/BlockChain-App.svg?branch=master)](https://travis-ci.com/Kenneth-Macharia/BlockChain-App)
[![Coverage Status](https://coveralls.io/repos/github/Kenneth-Macharia/BlockChain-App/badge.svg?branch=master)](https://coveralls.io/github/Kenneth-Macharia/BlockChain-App?branch=master)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/2aeb21c8472244498f1c634303d3d105)](https://www.codacy.com/manual/Kenneth-Macharia/BlockChain-App?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Kenneth-Macharia/BlockChain-App&amp;utm_campaign=Badge_Grade)

- A web app that implements land records as a blockchain.
- Blockchains offer improved security against records tampering making them ideal to safeguard ownership records of high-value assets.
- They also give a history of transactions that have occured on a particular asset rather than just the asset's current ownership state.

## The Components

- The application is made up of the following containerized services:

        1. A node.js (express) service which renders the UI and can
        be used to link the app to other external applications via
        APIs.

        2. A flask-restful backend service which secures the blockchain and
        co-ordinates data flow between the Node service and the backend and
        across the blockchain peer network.

        3. A Redis cache and queue service between the node and flask
         services. The cache keep a simplified copy of the blockchain records
        thus offering fast record look-ups without having to hit the backend
        DB. The cache is updated whenever a new block/ transaction is added
        to the blockchain. The queue holds new transactions captured by the
        node service before being persisted to the backend DB, ensuring
        asynchronous data capture. Transactions are popped from the queue
        using a separate thread running in the flask service.

        4. A MongoDB database service: the backend main storage, which holds
        the entire blockchain for the hub.

- The services 1 & 2 will be packaged into Docker images and deployed to an image registry using Travis CI, after automated tests have pass.
- They can then be pulled into a cluster environment alongside official images for the two data stores 3 & 4 and orchestrated to achieve the apps functionality.

## App Implementation Scenario

- Multiple hubs (each containing a 3-node cluster) can be spun up to create a blockchain peer network.
- Each hub will run the application on it's cluster and store it's own blockchain of the records.
- Record queries as well as additions can be perfomed at each of the hubs.
- Each hub will automatically sync with the other peer hubs via an API in the flask service, before forging a new block/ transaction, to gurantee the blockchain's validity across the peer network.

## The App Demo

- The application is currently deployed to _Azure_ as two independent blockchain hubs/peers.
- Hub 1 is on a VPN with _address space 10.0.0.0/16_ while Hub 2 is on a separate VPN with _address space 10.1.0.0/16_ and are not connected in any way.
- VMs on one hub cannot communicate directly with VMs on the other hub across Azure's network. The only way for inter-hub communication is via breaking out to the internet, thus mimicking a distributed blockchain network.

### Hub 1

- Hub 1 runs on a _Docker swarm cluster_ consisting of _3 linux VMs_.
- The _frontend service_ is accessible on `40.91.231.184`, from where records can be added and searched for as well as viewing of application logs.
- For demo purposes, _the backend service exposes a public endpoint_ allowing the viewing of the blockchain at the hub. This endpoint is accessible at `40.91.231.184:8080/backend/v1/blockchain`.

### Hub 2

- Hub 2 runs on a _Docker swarm cluster_ consisting of _3 linux VMs_ as well.
- The _frontend service_ is accessible on `52.188.123.100`, from where records can be added and searched for as well as viewing of application logs.
- For demo purposes, _the backend service exposes a public endpoint_ allowing the viewing of the blockchain at the hub. This endpoint is accessible at `52.188.123.100:8080/backend/v1/blockchain`.

## Using the App

- Upon loading the frontend, there is a short intro video showcasing how to use the application.
- Create a record on hub1 and check the blockchain on both hub using the backend service blockchain endpoint.
- Create a record on hub two and confirm that it's blockchain first gets updated with hub 1's blockchain before the new reocrd is added, demonstrating the sync functionlity that ensure the two blockchains remain valid and identical.
