import os
import json
import math
import requests
from flask import Flask, request
from concurrent.futures import ThreadPoolExecutor

from entities import Measurement

app = Flask(__name__)

hostname = os.environ['ORION_HOST']
port = os.environ["TRACKGEN_PORT"]

working_area = None
robot_speed = None


def compute_time(pa, pb):
    return math.sqrt((pa[0]-pb[0])**2 + (pa[1]-pb[1])**2 + (pa[2]-pb[2])**2)/robot_speed


def process_points(data):
    pts = {}
    rows = {}
    # Iterate over all points and select only those with z other than 0
    for p in data:
        if p["z"] != 0:
            if p["x"] in rows:
                rows[p["x"]].append(p["y"])
                pts[(p["x"], p["y"])] = p["z"]
            else:
                rows[p["x"]] = [p["y"]]
                pts[(p["x"], p["y"])] = p["z"]
    print(rows)
    traj = []
    is_reverse = False
    total_time = 0
    last_point = None
    for r in rows:
        if len(rows[r]) == 1:
            step_time = 0 if last_point is None else compute_time([r, rows[r][0], pts[r, rows[r][0]]], last_point)
            traj.append({"x": r, "y": rows[r][0], "z": pts[r, rows[r][0]], "time": step_time})
            total_time += step_time
            last_point = [r, rows[r][0], pts[r, rows[r][0]]]
        else:
            cur_row = sorted(rows[r]) if not is_reverse else list(reversed(sorted(rows[r])))
            # Add first point of the row to trajectory
            step_time = 0 if last_point is None else compute_time([r, cur_row[0], pts[r, cur_row[0]]], last_point)
            traj.append({"x": r, "y": cur_row[0], "z": pts[r, cur_row[0]], "time": step_time})
            total_time += step_time
            last_point = [r, cur_row[0], pts[r, cur_row[0]]]
            # Add last point of the row to trajectory
            step_time = 0 if last_point is None else compute_time([r, cur_row[-1], pts[r, cur_row[-1]]], last_point)
            traj.append({"x": r, "y": cur_row[-1], "z": pts[r, cur_row[-1]], "time": step_time})
            total_time += step_time
            last_point = [r, cur_row[-1], pts[r, cur_row[-1]]]
            is_reverse = not is_reverse
    return traj, total_time


def return_trajectory(pointcloud):
    print(f"Data received: {pointcloud}")
    trajectory, total_est_time = process_points(pointcloud["data"][0]["pointCloud"]["value"])
    data = meas.get(trajectory, pointcloud["data"][0]["id"], total_est_time)
    print(f"Resulting trajectory: {data}")
    re = requests.post("http://" + hostname + ":1026/v2/entities/", data=json.dumps(data),
                       headers={"content-type": "application/json"})
    print(re.content.decode('UTF-8'))


@app.route("/notify/", methods=['POST'])
def notify():
    data = request.get_json()
    _ = ThreadPoolExecutor().submit(return_trajectory, data)
    return "OK"


@app.route("/area/", methods=['POST'])
def area():
    global working_area
    global robot_speed
    data = request.get_json()
    working_area = data["data"][0]['extraParameters']["value"][0]["value"]
    robot_speed = data["data"][0]['extraParameters']["value"][1]["value"]
    print(f"New area: {working_area}")
    print(f"New speed: {robot_speed}")
    return "OK"


if __name__ == "__main__":
    count = 0
    print(hostname)
    meas = Measurement()
    app.run(host="0.0.0.0", port=port)
