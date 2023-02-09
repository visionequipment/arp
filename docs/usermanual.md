# User Manual

You can find the whole software and hardware requirements in [Architecture](architecture.md).

## Usage

If you want to know the API exposed by the ROSE-AP application, see [API](api.md).

To start using ARP ROSE-AP (TrackGen), the user must create at least two FIWARE subscriptions on the Orion context broker:

- TrackGen subscription for the PointCloud entities (Orion must forward them to TrackGen);

- target application subscription for the Measurement entities (Orion must forward them to the target application).

A simple python script to communicate subscriptions to the FIWARE Orion context broker is provided. 
Orion default port is settled. To run it:

```sh
cd src/utils
python subscriptions.py
```

After subscriptions are created, the user can generate point clouds and send them as NGSI entities to the Orion context broker.

To overwrite TrackGen application parameters (robot speed, sander diameter and overlap percentage), user should create other subscriptions
on the Orion context broker.

## Simulation

If operator doesn't have access to hardware, he can simulate point cloud with additional software provided.

TrackGen will receive the NGSI entities from the Orion context broker and will answer with NGSI Measurement entities, that are the output trajectories. 
The Orion context broker will forward the NGSI Measurement entities to the Target application.

The simple python script ```simple_vision_system.py``` can be run to simulate the execution flow as it follows:
```sh
cd src/utils
python simple_vision_system.py
``` 
