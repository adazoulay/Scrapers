#!/bin/bash

# Stop and remove existing containers, if running
docker-compose down

# Build and run the containers
docker-compose up --build -d
