# Blockchain Demo App

[![Build Status](https://travis-ci.org/Kenneth-Macharia/BlockChain-App.svg?branch=master)](https://travis-ci.org/Kenneth-Macharia/BlockChain-App)

## Description

A minimalist demo application, simulating records deployed as a blockchain.

## The Components

The app is made up of:

    1. A Node.js frontend service
    2. A Redis cache service between the frontend and backend services
    3. A Flask-Restful backend service
    4. A MongoDB service

Each service will be packaged into a Docker image and deployed to an image registry through Travis CI, after automated tests pass.

## Author

Kenneth Macharia
