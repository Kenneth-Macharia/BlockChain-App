# Blockchain Application

[![Build Status](https://travis-ci.com/Kenneth-Macharia/BlockChain-App.svg?branch=master)](https://travis-ci.com/Kenneth-Macharia/BlockChain-App)
[![Coverage Status](https://coveralls.io/repos/github/Kenneth-Macharia/BlockChain-App/badge.svg?branch=master)](https://coveralls.io/github/Kenneth-Macharia/BlockChain-App?branch=master)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/2aeb21c8472244498f1c634303d3d105)](https://www.codacy.com/manual/Kenneth-Macharia/BlockChain-App?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Kenneth-Macharia/BlockChain-App&amp;utm_campaign=Badge_Grade)

- A web app that implements a blockchain for storing land /asset records.
- Blockchains offer improved security against records tampering making them ideal to safeguard ownership records of high-value assets.
- They also give a history of transactions that have occured on a particular asset rather than just the asset's current ownership state.

## The Components

- The application is made up of the following containerized services:

        1. A node.js (express) service which renders the UI and can
           be used to link the app to other external applications via
           APIs.

        2. A flask-restful backend service which secures the blockchain and
           co-ordinates data flow between the node service and the main DB, as
           well as across the blockchain peer network.

        3. A Redis cache and queue service between the node and flask
           services. The cache keep a simplified copy of the blockchain records
           thus offering fast record look-ups without having to hit the main
           DB. The cache is updated whenever a new block/ transaction is added
           to the blockchain. The queue holds new transactions captured by the
           node service before being persisted to the main DB, thereby ensuring
           asynchronous data capture. Transactions are popped from the queue
           by a separate thread running in the flask backend service.

        4. A MongoDB database service: the main store, which holds
           the entire blockchain for a hub.

- The services 1 & 2 are be built into Docker images and deployed to docker hub using Travis CI, after automated tests have passed.
- They are then be pulled into a cluster environment alongside official images for the two data stores 3 & 4 and orchestrated to achieve the overrall app functionality.

## App Implementation Scenario

- Multiple hubs (each containing a multi-node cluster) can be spun up to create a blockchain peer network.
- Each hub will run the application on it's cluster and store it's own blockchain of the records.
- Record queries from and additions to the blockchain can be perfomed at each of the hubs.
- Each hub will automatically sync with the other peer hubs via an API in the flask service, to gurantee the blockchain's validity across the peer network.

## App Demo

- The application is deployed to _GCP_ on two independent blockchain hubs/peers.
- Each of the hubs are on different subnets in different regions.
- VMs on one hub cannot communicate directly with VMs on the other hub across GCP's network. Inter-hub communication is only possible via the internet, thus emulating a distributed blockchain network.

### Hub 1

- The _frontend service_ is accessible here > [Home](http://35.211.97.185), from where records can be added and searched.
- From the provided drop-down list link, application logs handy for checking block forging status, can be viewed.
- _The backend service exposes a public endpoint_ allowing the viewing of the blockchain at the hub. This endpoint is accessible here > [Blockchain](http://35.211.97.185:8080/backend/v1/blockchain)

### Hub 2

- It's _frontend service_ is accessible here > [Home](http://35.210.175.76)
- The blockchain endpoint for this hub is accessible here > [Blockchain](http://35.210.175.76:8080/backend/v1/blockchain)

## Using the App

- A short intro video demonstating how to use the app is provided on the
  the homepage.
- Test tasks:

   1. Check the current blockchain on both hubs.
   2. Create a record on either hubs (Give it a moment to forge & sync)
   3. Verify the record exists on the hub created on and the other one as well.

- When a peer hub adds a new record, it prompts the other peer hubs to update
  their blockchains as well thus ensuring the blockchain is up-to date always. This
  is achieved through the validation and syncing process where each hub examines
  the newly updated blockchain and if more recent than the local copy, then the local
  copy is updated.
- This blockchain auto-sync ensures that the entire network keeps an updated copy
  of the blockchain thus facilitating searching of real-time updated records.

- Types of entries that can be added for an asset:

   1. New Record: when the asset has not yet been recorded on the
      blockchain. This happens when a search yields no results and the
      app allows you to add the asset's initial transfer transaction.

   2. Add transaction to record: when an asset exists; the app allows
      you to add a subsequent transfer record to the existing asset.
