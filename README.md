# Blockchain Application

[![Build Status](https://travis-ci.com/Kenneth-Macharia/BlockChain-App.svg?branch=master)](https://travis-ci.com/Kenneth-Macharia/BlockChain-App)
[![Coverage Status](https://coveralls.io/repos/github/Kenneth-Macharia/BlockChain-App/badge.svg?branch=master)](https://coveralls.io/github/Kenneth-Macharia/BlockChain-App?branch=master)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/2aeb21c8472244498f1c634303d3d105)](https://www.codacy.com/manual/Kenneth-Macharia/BlockChain-App?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Kenneth-Macharia/BlockChain-App&amp;utm_campaign=Badge_Grade)

- A web app that implements a blockchain for storing land /asset records.
- Blockchains offer improved security against records tampering making them ideal to safeguard ownership records of high-value assets.
- They also give a history of transactions that have occured on a particular asset rather than just the asset's current ownership state.

## The Components

- The application is made up of the following containerized services:

        1. A node.js (express) service which renders the UI for performing searches
           and adding records. It can be used to link the app to other external
           applications via APIs.

        2. A flask-restful service which secures the blockchain and
           co-ordinates data flow between the node service and the main DB. It also
           has the blockchain peer network controller that manages interaction with
           the other peer nodes.

        3. A Redis cache and queue service between the node and flask
           services.

               The cache keep a simplified copy of the blockchain, offering
               fast record look-up without having to hit the main DB. The cache is
               updated whenever a new block/ transaction is added to the blockchain.

               The queue holds new transactions captured by the node service before
               being persisted to the main DB, ensuring asynchronous data capture.
               Transactions are popped from the queue by a separate thread
               running in the flask service.

        4. A MongoDB database service: the main data store, which holds
           the entire blockchain for a hub.

- The services 1 & 2 are be built into Docker images and deployed to docker hub using Travis CI, after automated tests have passed.
- They are then be pulled into a cluster environment alongside official images for the two data stores 3 & 4 and orchestrated to achieve the overrall app functionality.

## Use Case

- Multiple sites/hubs (each with a multi-node cluster) can be spun up to create a blockchain peer network e.g 1 per county.
- Each hub will run the application on it's cluster and store it's own blockchain of the records.
- Records can be queried and additions to the blockchain can be perfomed at each of the hubs.
- Each hub will automatically sync with the other peer hubs to gurantee the blockchain's validity and homogeneity across the peer network.

## Demo

- The application is deployed to _GCP_ on two independent blockchain hubs, each comprising 3 Linux VMs and runnig 2 replicas of each of the 4 services mention above.
- Each of the hubs are on different subnets in different regions and the applications on each hub communicate over
  the internet and not across the VPC network.

### Hub 1

- The _frontend service_ is accessible here > [Home](http://35.206.155.11), from where records can be added and searched.
- _The backend service exposes a public endpoint_ allowing the viewing of the blockchain at the hub. This endpoint is accessible here > [Blockchain](http://35.206.155.11:8080/backend/v1/blockchain)

### Hub 2

- It's _frontend service_ is accessible here > [Home](http://35.211.54.229)
- The blockchain endpoint for this hub is accessible here > [Blockchain](http://35.211.54.229:8080/backend/v1/blockchain)

## Using the App

- A short intro video demonstating how to use the app is provided on the
  the homepage.
- Test tasks:

   1. Check the current blockchain on both hubs.
   2. Create a record on either hubs.
   3. Verify the record exists on the hub created on and on the other one as well.
   4. Perform searches of the added record on both hubs to verify search works.

- When a peer hub adds a new record, it prompts the other peer hubs to update
  their blockchains as well ensuring the blockchain is up-to date always. This
  is achieved through the sync and validation process where each hub examines
  the newly updated blockchain and if more recent than the local copy, then the local
  copy is updated.
- This blockchain auto-sync ensures that the entire network keeps an updated copy
  of the blockchain thus facilitating searching of real-time updated records at any
  of the hubs/ sites.

- Types of entries that can be added for an asset:

   1. New Record: when the asset has not yet been recorded on the
      blockchain. This happens when a search yields no results and the
      app allows you to add the asset's initial transfer transaction.

   2. Add transaction to existing record: when an search yields a result, the app
      allows you to add a subsequent transfer record to the existing asset.
