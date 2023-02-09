# API

Through Subscriptions, Orion context broker can forward state changes of the NGSI entities to both the ROSE-AP component 
for the processing cycle and cloud infrastructure (QuantumLeap + Crate DB) for their monitoring.

Here you have all HTTP APIs exposed by the component.

## HTTP API

All API are HTTP methods.

- ```POST notify```: it is the core API of the system. A Orion Subscription should be created to send the new "PointCloud" NGSI entities. 
   The result - a new "Measurement" NGSI entity - is asynchronous and delivered to the target application by the Orion 
   context broker through another subscription. TrackGen treats z-axis values of -100 as no object. Coordinates can be float values.   

```sh
curl -i -X POST -H "Content-Type: application/json" -d '{"data": [{"id" : "Example", "pointCloud": { \
                    "type": "StructuredValue", "value": [ \
                    [{"y": 0, "x": 0, "z": -100},		\
                    {"y": 20, "x": 0, "z": -100},		\
                    {"y": 40, "x": 0, "z": -100},		\
                    {"y": 60, "x": 0, "z": -100},		\
                    {"y": 80, "x": 0, "z": -100}],		\
                    [{"y": 0, "x": 20, "z": -100},		\
                    {"y": 20, "x": 20, "z": 100},	    \
                    {"y": 40, "x": 20, "z": 100},	    \
                    {"y": 60, "x": 20, "z": -100},		\
                    {"y": 80, "x": 20, "z": -100}],		\
                    [{"y": 0, "x": 40, "z": -100},		\
                    {"y": 20, "x": 40, "z": 100},	    \
                    {"y": 40, "x": 40, "z": 100},	    \
                    {"y": 60, "x": 40, "z": 100},	    \
                    {"y": 80, "x": 40, "z": -100}],		\
                    [{"y": 0, "x": 60, "z": -100},		\
                    {"y": 20, "x": 60, "z": 100},	    \
                    {"y": 40, "x": 60, "z": 100},	    \
                    {"y": 60, "x": 60, "z": -100},		\
                    {"y": 80, "x": 60, "z": -100}],		\
                    [{"y": 0, "x": 80, "z": -100},		\
                    {"y": 20, "x": 80, "z": -100},		\
                    {"y": 40, "x": 80, "z": -100},		\
                    {"y": 60, "x": 80, "z": -100},		\
                    {"y": 80, "x": 80, "z": -100}]		\
                ]}}]}' http://localhost:5050/notify/
```
	
- ```POST speed```: this API is useful to define the speed of the movement (m/s), that is used to estimate the processing time. 
   ROSE-AP should be subscribed to changes in the state of the "targetSpeed" attribute of the "DeviceOperation" NGSI entities.

```sh
curl -i -X POST -H "Content-Type: application/json" -d '{"data": [{"targetSpeed": { "type": "Float", "value": 1.0 }}]}'  http://localhost:5050/speed/
```

- ```POST overlap``` this API is useful to define the overlap percentage of the path. ROSE-AP should be subscribed to the
   changes in the state of the "requiredQuality" attribute of the "DeviceOperation" NGSI entities, because final quality of
   the processing depends on overlap percentage. Three possible values are defined: "Low" (maximum 30% overlap), "Medium"
   (maximum 40% overlap) and "High" (maximum 50% overlap).

```sh
curl -i -X POST -H "Content-Type: application/json" -d '{"data": [{"requiredQuality": { "type": "Text", "value": "High" }}]}'  http://localhost:5050/overlap/
```

- ```POST diameter``` this API is useful to update the diameter of the sander, that must be defined to compute the final path.
  ROSE-AP should be subscribed to the changes in the state of the "diameter" attribute of the "Device" NGSI entities. 

```sh
curl -i -X POST -H "Content-Type: application/json" -d '{"data": [{"diameter": { "type": "Float", "value": 125.0 }}]}'  http://localhost:5050/diameter/
```

- ```GET ping``` to check whether application is running

```sh
curl http://localhost:5050/ping/
```
