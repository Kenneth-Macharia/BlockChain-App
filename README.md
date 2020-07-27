# Blockchain Demo App

[![Build Status](https://travis-ci.org/Kenneth-Macharia/BlockChain-App.svg?branch=master)](https://travis-ci.org/Kenneth-Macharia/BlockChain-App)
[![Coverage Status](https://coveralls.io/repos/github/Kenneth-Macharia/BlockChain-App/badge.svg?branch=master&service=github)](https://coveralls.io/github/Kenneth-Macharia/BlockChain-App?branch=master)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/2aeb21c8472244498f1c634303d3d105)](https://www.codacy.com/manual/Kenneth-Macharia/BlockChain-App?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Kenneth-Macharia/BlockChain-App&amp;utm_campaign=Badge_Grade)

## Description

A demo application that implements land records as a blockchain.

## The Components

The app is made up of the following micro-services:

    1. A Node.js frontend
    2. A Redis cache between the frontend and backend services
    3. A Flask-Restful backend
    4. A Mongo database

- Each service will be packaged into a Docker image and deployed to an image registry through Travis CI, after automated tests pass.
- They can then be pulled into a cluster environment and orchestrated.

## Implementation Scenario

- Multiple hubs (containing a minimum 3-node cluster each) can be spun up to create a blockchain peer network.
- Each hub will run the application on it's cluster and store it's own blockchain of the records.
- Record/ block queries can be perfomed at each of the hubs as well as adding new blocks/ new records to the blockchain.
- Each hub will automatically sync with the other peer hubs before forging a new block to gurantee the blockchain's validity.

## Author

Kenneth Macharia
