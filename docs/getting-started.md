# Getting started

## Start application

To start working with this ROSE-AP - that we call TrackGen - the user must first install it. PLease see the 
[Installation guide](installationguide.md) for that and then continue the reading.

After having started the container, the user must define two required FIWARE subscription on the Orion context broker
(TrackGen should be subscribed to new "PointCloud" NGSI entities, while the application that will consume the result should 
be subscribed to new "Measurement" NGSI entities).

## Create subscriptions

A simple python script to communicate subscriptions to the FIWARE Orion context broker is provided. 
Orion default port is settled. To run it:

```sh
cd src/utils
python subscriptions.py
```

By running the following cURL command, you can check if subscriptions has been created:

```sh
curl http://localhost:1026/v2/subscriptions 
```

The output should be similar to the following:

```
[
   {
      "id":"63f8a67e0560a13e2b53035f",
      "description":"Notify TrackGen of a new Point Cloud",
      "status":"active",
      "subject":{
         "entities":[
            {
               "idPattern":".*",
               "type":"PointCloud"
            }
         ],
         "condition":{
            "attrs":[
               "pointCloud"
            ]
         }
      },
      "notification":{
         "attrs":[
            "pointCloud"
         ],
         "onlyChangedAttrs":false,
         "attrsFormat":"normalized",
         "http":{
            "url":"http://trackgen:5050/notify/"
         },
         "covered":false
      }
   },
   {
      "id":"63f8a67e0560a13e2b530362",
      "description":"Notify Robot of new trajectories",
      "status":"active",
      "subject":{
         "entities":[
            {
               "idPattern":".*",
               "type":"Measurement"
            }
         ],
         "condition":{
            "attrs":[
               "outputTrajectory"
            ]
         }
      },
      "notification":{
         "attrs":[
            "outputTrajectory"
         ],
         "onlyChangedAttrs":false,
         "attrsFormat":"normalized",
         "http":{
            "url":"http://host.docker.internal:5500/notify/"
         },
         "covered":false
      }
   },
   {
      "id":"63f8a67e0560a13e2b530364",
      "description":"Notify TrackGen of new robot speed",
      "status":"active",
      "subject":{
         "entities":[
            {
               "idPattern":".*ROBOT.*",
               "type":"Device"
            }
         ],
         "condition":{
            "attrs":[
               "extraParameters"
            ]
         }
      },
      "notification":{
         "attrs":[
            "extraParameters"
         ],
         "onlyChangedAttrs":false,
         "attrsFormat":"normalized",
         "http":{
            "url":"http://trackgen:5050/speed/"
         },
         "covered":false
      }
   }
]
```

## Test path generation 

After creating the subscriptions, the core functionality of the ROSE-AP can be tested.

A simple python script to generate entities is provided. To run it:

```sh
cd src/utils
python simple_vision_system.py
```

Among the entities that should have been generated, there must be at least one "PointCloud", which can be retrieved with the
following cURL command:

```sh
curl http://localhost:1026/v2/entities?idPattern=POINTCLOUD:id:1
```

The json data should be similar to:

```
[
   {
      "id":"urn:ngsi-ld:POINTCLOUD:id:1",
      "type":"PointCloud",
      "description":{
         "type":"Text",
         "value":"Point Cloud generated from image by the vision system",
         "metadata":{
            
         }
      },
      "error":{
         "type":"Text",
         "value":"No error",
         "metadata":{
            
         }
      },
      "imageIdentifier":{
         "type":"Text",
         "value":"urn:ngsi-ld:IMAGE:id:1",
         "metadata":{
            
         }
      },
      "pointCloud":{
         "type":"StructuredValue",
         "value":[
            [
               {
                  "y":0,
                  "x":0,
                  "z":-100
               },
               {
                  "y":20,
                  "x":0,
                  "z":-100
               },
               {
                  "y":40,
                  "x":0,
                  "z":-100
               },
               {
                  "y":60,
                  "x":0,
                  "z":-100
               },
               {
                  "y":80,
                  "x":0,
                  "z":-100
               }
            ],
            [
               {
                  "y":0,
                  "x":20,
                  "z":-100
               },
               {
                  "y":20,
                  "x":20,
                  "z":100
               },
               {
                  "y":40,
                  "x":20,
                  "z":100
               },
               {
                  "y":60,
                  "x":20,
                  "z":100
               },
               {
                  "y":80,
                  "x":20,
                  "z":-100
               }
            ],
            [
               {
                  "y":0,
                  "x":40,
                  "z":-100
               },
               {
                  "y":20,
                  "x":40,
                  "z":100
               },
               {
                  "y":40,
                  "x":40,
                  "z":100
               },
               {
                  "y":60,
                  "x":40,
                  "z":100
               },
               {
                  "y":80,
                  "x":40,
                  "z":-100
               }
            ],
            [
               {
                  "y":0,
                  "x":60,
                  "z":-100
               },
               {
                  "y":20,
                  "x":60,
                  "z":100
               },
               {
                  "y":40,
                  "x":60,
                  "z":100
               },
               {
                  "y":60,
                  "x":60,
                  "z":-100
               },
               {
                  "y":80,
                  "x":60,
                  "z":-100
               }
            ],
            [
               {
                  "y":0,
                  "x":80,
                  "z":-100
               },
               {
                  "y":20,
                  "x":80,
                  "z":-100
               },
               {
                  "y":40,
                  "x":80,
                  "z":-100
               },
               {
                  "y":60,
                  "x":80,
                  "z":-100
               },
               {
                  "y":80,
                  "x":80,
                  "z":-100
               }
            ]
         ],
         "metadata":{
            
         }
      },
      "status":{
         "type":"Boolean",
         "value":true,
         "metadata":{
            
         }
      }
   }
]
```

The ROSE-AP should have processed this input in real-time and should have already sent an output to the Orion context
broker, that we can retrieve with the following cURL command:

```sh
curl http://localhost:1026/v2/entities?idPattern=MEASUREMENT:id:1
```

The computed path retrieved with this command should be similar to:

```
[
   {
      "id":"urn:ngsi-ld:MEASUREMENT:id:1",
      "type":"Measurement",
      "description":{
         "type":"Text",
         "value":"Estimated trajectory",
         "metadata":{
            
         }
      },
      "error":{
         "type":"Text",
         "value":"No error",
         "metadata":{
            
         }
      },
      "estimatedWorkpieceProcessingTime":{
         "type":"Float",
         "value":0.034601126,
         "metadata":{
            
         }
      },
      "outputTrajectory":{
         "type":"StructuredValue",
         "value":[
            {
               "x":40,
               "y":20,
               "z":100,
               "time":0,
               "side":"surface"
            },
            {
               "x":40,
               "y":60,
               "z":100,
               "time":0.008,
               "side":"surface"
            },
            {
               "x":20,
               "y":20,
               "z":100,
               "time":0,
               "side":"top"
            },
            {
               "x":60,
               "y":40,
               "z":100,
               "time":0.008944272,
               "side":"right"
            },
            {
               "x":40,
               "y":60,
               "z":100,
               "time":0.005656854,
               "side":"right"
            },
            {
               "x":20,
               "y":60,
               "z":100,
               "time":0.004,
               "side":"top"
            },
            {
               "x":20,
               "y":20,
               "z":100,
               "time":0.008,
               "side":"top"
            }
         ],
         "metadata":{
            
         }
      },
      "overlap":{
         "type":"Boolean",
         "value":true,
         "metadata":{
            
         }
      },
      "pointCloudIdentifier":{
         "type":"Text",
         "value":"urn:ngsi-ld:POINTCLOUD:id:1",
         "metadata":{
            
         }
      },
      "pointDensity":{
         "type":"Float",
         "value":10,
         "metadata":{
            
         }
      },
      "status":{
         "type":"Boolean",
         "value":true,
         "metadata":{
            
         }
      }
   }
]
```

As further confirmation of success, it can be seen that the code in the "pointCloudIdentifier" field of the last fetched 
entity is equal to the identifier of the input "PointCloud" entity.

## Advanced usage 

The solution does not contain the vision system, necessary to acquire images and process them to obtain point clouds.
This is convenient because the system is not tied to 2D cameras from a particular vendor.

The basic workflow of the solution is the following:

- install the requirements following the [Installation guide](installationguide.md).

- define the two required FIWARE subscriptions on the Orion context broker (TrackGen should be subscribed to new PointCloud
  entities, while the target application to the new Measurement entities), as defined in the [User Manual](usermanual.md).
  Other useful subscriptions are reported in the [API](api.md) and allow the user to update the sanding parameters. 

- acquire a 2D image and generate a point cloud. In order to generate a good image and then valid point cloud, the user should:

    1. put a light above (and/or under) the object to make it clearly distinguishable from the background in the 2D image.
    
    2. remove noise (objects that should not be sanded) from the 2D grayscale image, then threshold it. 
       Background points should have low values, i.e. less than the threshold value of -100 (in the robot coordinate system), 
       while part to be sanded should have values higher of the threshold (the height of the object in the robot coordinate
       system). 
    
    3. sample the image with fixed step in both axes to obtain a point cloud. During this step, each point of the image 
       should be mapped in the coordinate system of the robot, i.e. the point in top-left corner of the image, with x=0,
       y=0 and z=20, becomes x=x', y=y', z=20.
    
- encode the point cloud in a NGSI PointCloud entity and send it to the Orion context broker.

- the ROSE-AP component will receive the data forwarded from the Orion context broker. 

- the ROSE-AP will generate the path to process the part, then will encode it in a NGSI Measurement entity and send to 
  the Orion context broker.

- finally, the target application will receive the resulting path, delivered by the Orion context broker. The Orion CB 
  can be configured also to send the NGSI entities to the cloud infrastructure provided by this solution, in order to
  make it possible to monitor operations remotely. 

Thanks to this approach, our solution is completely indipendent of hardware, both models and brands of robots and cameras, 
but it is still highly configurable because all sanding parameters (speed of the movement, sander diameter, overlap 
percentage) can be updated for each new part through the FIWARE subscriptions.

A point cloud example (it is parsed in the [PointCloud Python class](../src/entities/point_cloud.py)) can
be found at this [link](../src/assets/raw_point_cloud.txt).
