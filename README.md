# Blockchain Demo App
## Description
A minimalist demo application, simulating land records deployed as a blockchain.

## The Components
The app is made up of:

    1. A Node.js frontend service
    2. A Python backend service

And will also require:

    1. A Redis cache between the frontend and backend services
    2. A MongoDB database connected to the backend service

Each service will be packaged in a Docker container and deployed to a Swarm cluster alongisde containers for the two data stores.

## Author
Kenneth Macharia
