# Agile Robotized Processing (ARP)

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Documentation Status](https://readthedocs.org/projects/arp/badge/?version=latest)](https://arp.readthedocs.io/en/latest)

This project is part of [DIH^2](http://www.dih-squared.eu/). For more information check the RAMP Catalogue entry for the components.
This repository contains the ROSE-AP component (TrackGen) and other components developed for the TTE.

| :books: [Documentation](https://arp.readthedocs.io/en/latest) |
| --------------------------------------------- | 


## Background

### Application Domain

Sanding of wooden panels for the furniture industry.

### Use Case Needs / Agility Challenge Description

Use Case Needs: Panels in different shapes and sizes need to be processed from the top and from the sides as part of preparation 
of the surface for different types of finish. Processing is done manually due to lack of flexible solutions which can 
easily adapt to frequently changing production in a user friendly way.

The challenges for the company originate mainly from two sources: the
increased demand and unpredictability of their production. Different workers
require different processing times depending on their skill and experience, and
inconsistencies in production quality mean that sometimes a workpiece may
even be returned for corrective re-processing to ensure that the quality of the
finished product is not compromised.

### Main Objectives

The proposed solution aims to achieve high flexibility requirements for automating the processing flat workpieces which account for
more than 90% of the workload in sanding phase.
Combined knowhow and experience of workers will be gathered and stored in a database of recipes, and it will contain information about correct
set of sanding parameters for a certain type of material in relation to the desired finish The worker will be able to choose the correct
recipe from the database and, based on that, the system will automatically configure all processing parameters.
The required high flexibility will be achieved through set of intelligent capabilities which give the system the ability to self reconfigure
and adapt to workpieces. The system will have the ability to measure shape and coordinates of the workpiece and ensure they will be
properly held during processing.
The quality inconsistencies and re processing issue will be completely solved through automation of the sanding process using robotized 
solution with force feedback and automatic sanding disk exchanger.

### Solution

The solution consists of the following components:
- the ROSE-AP application, called TrackGen, which is a Flask application that processes point clouds (extracted in an intelligent way
  by the vision system) and returns trajectories for the target application.
- a tailored FIWARE connector that acts also as vision system, acquires images from an USB camera, generates point clouds from images
  and handle communication with PLC and robot;
- a local instance of FIWARE Orion Context Broker, which is ready and runs in the plant. 
  The database MongoDB stores the NGSI entities that come from the context broker;
- a local instance of FIWARE QuantumLeap as historical data connector to feed a CrateDB, a local data historian.

## Install

Information about how to install the ARP ROSE-AP can be found in the [Installation Guide](docs/installationguide.md).

## Usage

Information about how to use the component can be found in the [User Manual] (docs/usermanual.md).

## License

[Apache2.0](LICENSE) © 2022 Vision Equipment 
