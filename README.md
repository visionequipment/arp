# Agile Robotized Processing (ARP)

This repository contains the ROSE-AP component (TrackGen) and other components developed for the TTE.

## Background
TrackGen processes point clouds and returns trajectories for a Target application.

The base RAMP IoT platform consists of the following components:
- a tailored FIWARE connector which is called “Vision System” and generates data;
- a local instance of FIWARE Orion Context Broker, which is ready and runs in the plant. The database MongoDB stores the NGSI entities that come from the context broker;
- a local instance of FIWARE QuantumLeap as historical data connector to feed a CrateDB, a local data historian.

## Install

Prerequisites:

- Deployment requires Docker Compose.
- During initial installation, internet access is required in order to download application requirements.

- Execute the following commands to build TrackGen image from source:
    ```sh
    cd src
    docker build -f ..\docker\Dockerfile . -t trackgen
    ```

- Configure parameters in ```docker-compose.yml``` file (docker folder) and run it:
    ```sh
    cd docker
    docker-compose up -d
    ```

## Usage

To start using TrackGen, the user must enstablish at least three FIWARE subscriptions:
- subscription for the PointCloud entities (Orion must forward them to TrackGen);
- subscription for the area parameter of the Device entities (Orion must forward them to TrackGen);
- subscription for the Measurement entities (Orion must forward them to the Target application).

A simple python script to communicate subscriptions to the FIWARE Orion context broker is provided. 
Orion default port is setted. To run it:

```sh
cd src/utils
python subscriptions.py
```

After subscriptions are created, the user can generate point clouds and send them as NGSI entities to the Orion context broker.

TrackGen will receive the NGSI entities from the Orion context broker and answer with NGSI Measurement entities, that are the output trajectories. 
The Orion context broker will forward the NGSI Measurement entities to the Target application.

The simple python script ```simple_vision_system.py``` can be run to simulate the execution flow as it follows:
```sh
cd src/utils
python simple_vision_system.py
```  

## License

[MIT](LICENSE) © <TTE>
