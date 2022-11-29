# Installation Guide


## Prerequisites

Deployment requires Docker Compose, that you can install alongside Docker: you can find [here](https://docs.docker.com/get-docker/).

During initial installation, Internet access is required in order to download application requirements.

## ROSE-AP

Execute the following commands to build TrackGen image from source:
    ```sh
    cd src
    docker build -f ..\docker\Dockerfile . -t trackgen
    ```

## Other RAMP IoT platform components

- Configure parameters in ```docker-compose.yml``` file (docker folder) and run it to download images and create container:
    ```sh
    cd docker
    docker-compose up -d
    ```

If you don't have access to hardware (PLC/robot/sander), you can find more information about simulation in [User & Programmers Manual](usermanual.md).