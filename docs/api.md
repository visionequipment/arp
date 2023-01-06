# API

Since the ARP ROSE-AP component is a Flask application, you could execute HTTP requests directly to it, but you would lose
all benefits of using the FIWARE Orion Context Broker. Here you have all HTTP APIs exposed by the component.

## HTTP API

Except for the "ping" API, all APIs provided are HTTP POST methods.

- ```GET ping``` to check whether application is running

```sh
curl http://localhost:5050/ping/
```

- ```POST notify``` to send point clouds and receive trajectories. TrackGen treats z-axis values of -100 as no object. 
   Coordinates can be float values

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
	
- ```POST speed``` to update robot speed (it is useful to estimate the time to complete the trajectory

```sh
curl -i -X POST -H "Content-Type: application/json" -d '{"data": [{"targetSpeed": { "type": "Float", "value": 1.0 }}]}'  http://localhost:5050/speed/
```

- ```POST overlap``` to update overlap percentage (it is a parameter related to the final required quality)

```sh
curl -i -X POST -H "Content-Type: application/json" -d '{"data": [{"requiredQuality": { "type": "Text", "value": "High" }}]}'  http://localhost:5050/overlap/
```

- ```POST diameter``` to update robot speed (it is useful to estimate the time to complete the trajectory

```sh
curl -i -X POST -H "Content-Type: application/json" -d '{"data": [{"diameter": { "type": "Float", "value": 125.0 }}]}'  http://localhost:5050/diameter/
```

