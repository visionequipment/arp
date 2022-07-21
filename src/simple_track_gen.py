import os
import json
import math
import requests
from loguru import logger
from flask import Flask, request
from concurrent.futures import ThreadPoolExecutor

from entities import Measurement

app = Flask(__name__)

hostname = os.environ['ORION_HOST']
port = os.environ["TRACKGEN_PORT"]

robot_speed = None

MOVE_FROM_SURFACE_TO_SIDE_CONST = 0.0001
MOVE_FROM_SIDE_TO_SIDE_CONST = 0.0002


def compute_time(pa, pb):
    return math.sqrt((pa[0]-pb[0])**2 + (pa[1]-pb[1])**2 + (pa[2]-pb[2])**2)/robot_speed


def process_points(data):
    pts = {}
    rows = {}
    min_x = None
    min_y = None
    max_x = None
    max_y = None
    # Iterate over all points and select only those with z other than 0
    for p in data:
        if p["z"] != 0:
            if p["x"] in rows:
                rows[p["x"]].append(p["y"])
                pts[(p["x"], p["y"])] = p["z"]
            else:
                rows[p["x"]] = [p["y"]]
                pts[(p["x"], p["y"])] = p["z"]
        if min_x is None or p["x"] < min_x:
            min_x = p["x"]
        if min_y is None or p["y"] < min_y:
            min_y = p["y"]
        if max_x is None or p["x"] > max_x:
            max_x = p["x"]
        if max_y is None or p["y"] > max_y:
            max_y = p["y"]

    # Iterate over not-empty rows and select only significant points (contours)
    is_reverse = False
    points = []
    r_pts = []
    l_pts = []
    for r in rows:
        if len(rows[r]) == 1:
            cur_pnt = [r, rows[r][0], pts[r, rows[r][0]]]
            points.append(cur_pnt)
            r_pts.append(cur_pnt)
            l_pts.append(cur_pnt)
        else:
            r_pts.append([r, rows[r][0], pts[r, rows[r][0]]])
            l_pts.append([r, rows[r][-1], pts[r, rows[r][-1]]])
            cur_row = sorted(rows[r]) if not is_reverse else list(reversed(sorted(rows[r])))
            # Add first point of the row to trajectory
            points.append([r, cur_row[0], pts[r, cur_row[0]]])
            # Add last point of the row to trajectory
            points.append([r, cur_row[-1], pts[r, cur_row[-1]]])
            is_reverse = not is_reverse

    # Iterate over points to generate first part of the trajectory (surface)
    traj = []
    total_time = 0
    lp = None
    for p in points:
        step_time = 0 if lp is None else compute_time(p, lp)
        traj.append({"x": p[0], "y": p[1], "z": p[2], "time": step_time})
        total_time += step_time
        lp = p

    # Sort points with respect to the last point of the surface trajectory
    pts = r_pts.copy()
    pts.extend(list(reversed(l_pts)))
    i = 0
    for i in range(len(pts)):
        if pts[i] == lp:
            break
    b_pts = pts[i:]
    b_pts.extend(pts[:i+1])

    # Iterate over points to generate second part of the trajectory (borders)
    for i, p in enumerate(b_pts):
        step_time = 0 if lp is None else compute_time(p, lp)
        # If step_time = 0, then send command to move from surface to side
        if step_time == 0:
            step_time = MOVE_FROM_SURFACE_TO_SIDE_CONST
        # If current and last point are external, then send command to move from one side to the other
        elif p != lp and \
                (p[0] == lp[0] == min_x or p[1] == lp[1] == min_y or p[0] == lp[0] == max_x or p[1] == lp[1] == max_y):
            step_time = MOVE_FROM_SIDE_TO_SIDE_CONST
        traj.append({"x": p[0], "y": p[1], "z": p[2], "time": step_time})
        total_time += step_time
        lp = p
    return traj, total_time


def return_trajectory(pointcloud):
    logger.info(f"Data received: {pointcloud}")
    trajectory, total_est_time = process_points(pointcloud["data"][0]["pointCloud"]["value"])
    data = meas.get(trajectory, pointcloud["data"][0]["id"], total_est_time)
    logger.info(f"Resulting trajectory: {data}")
    re = requests.post("http://" + hostname + ":1026/v2/entities/", data=json.dumps(data),
                       headers={"content-type": "application/json"})
    logger.info(re.content.decode('UTF-8'))


@app.route("/notify/", methods=['POST'])
def notify():
    data = request.get_json()
    _ = ThreadPoolExecutor().submit(return_trajectory, data)
    return "OK"


@app.route("/speed/", methods=['POST'])
def area():
    global robot_speed
    data = request.get_json()
    robot_speed = data["data"][0]['extraParameters']["value"][1]["value"]
    logger.info(f"New speed: {robot_speed}")
    return "OK"


if __name__ == "__main__":
    count = 0
    logger.info(hostname)
    meas = Measurement()
    app.run(host="0.0.0.0", port=port)
