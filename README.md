# Blockchain Application

[![Build Status](https://travis-ci.org/Kenneth-Macharia/BlockChain-App.svg?branch=master)](https://travis-ci.org/Kenneth-Macharia/BlockChain-App)
[![Coverage Status](https://coveralls.io/repos/github/Kenneth-Macharia/BlockChain-App/badge.svg?branch=master&service=github)](https://coveralls.io/github/Kenneth-Macharia/BlockChain-App?branch=master)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/2aeb21c8472244498f1c634303d3d105)](https://www.codacy.com/manual/Kenneth-Macharia/BlockChain-App?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Kenneth-Macharia/BlockChain-App&amp;utm_campaign=Badge_Grade)

## Description

- A demo application that implements land records as a blockchain.
- Blockchains offer improved security against records tampering making them ideal to safeguard ownership records of high-value assets.
- They also give a history of transactions that have occured on a particular asset rather than just the asset's current ownership state.

## The Components

The application is made up of the following container services:

    1. A Node.js (Express) frontend service which renders the UI views and can
    be used to link the applcation to other external applications via
    APIs.

    2. A Redis cache between the frontend and backend services, which will
     offer fast record look-ups as well as a queue for transaction persisting to the main Database.

    3. A Flask-Restful backend service which secures the blockchain and
    co-ordinates data flow between the front and back end and across the peer
    network.

    4. A MongoDB database: the main persistance storage.

- Each service will be packaged into a Docker image and deployed to an image registry through Travis CI, after automated tests pass.
- They can then be pulled into a cluster environment and orchestrated.

## App Implementation Scenario

- Multiple hubs (each containing a 3-node cluster) can be spun up to create a blockchain peer network.
- Each hub will run the application on it's cluster and store it's own blockchain of the records.
- Record/ block queries can be perfomed at each of the hubs as well as adding new blocks/ new records to the blockchain.
- Each hub will automatically sync with the other peer hubs before forging a new block, to gurantee the blockchain's validity across the peer network.
