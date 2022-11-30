# Architecture

The solution consists of the following (hardware and software) components:
- the ROSE-AP application, called TrackGen, which is a Flask application that processes point clouds (extracted in an intelligent way
  by the vision system) and returns trajectories for the target application.
- a tailored FIWARE connector that acts also as vision system, acquires images from an USB camera, generates point clouds from images
  and handle communication with PLC and robot;
- a local instance of FIWARE Orion Context Broker, which is ready and runs in the plant. 
  The database MongoDB stores the NGSI entities that come from the context broker;
- a local instance of FIWARE QuantumLeap as historical data connector to feed a CrateDB, a local data historian.
- a PLC that commands a conveyor belt.
- a robot that executes the sanding.

In this repository, you can find the ROSE-AP code, the Docker Compose YAML file to reproduce the FIWARE environment
 and a simulated vision system, to test the component. PLC and robot software is not provided.
