import os
import json
import math
import requests
import numpy as np
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
    return math.sqrt((pa[0]-pb[0])**2 + (pa[1]-pb[1])**2 + (pa[2]-pb[2])**2) / robot_speed


def is_contigous(p1, p2):
    contigous_directions = {"a": {"top": ["right", "left"], "bottom": ["right", "left"],
                                  "right": ["top", "bottom"], "left": ["top", "bottom"]},
                            "x": {"top": ["top"], "bottom": ["bottom"], "right": [], "left": []},
                            "y": {"top": [], "bottom": [], "right": ["right"], "left": ["left"]},
                            "s": {"top": {True: "left", False: "right"}, "bottom": {True: "left", False: "right"},
                                  "right": {True: "top", False: "bottom"}, "left": {True: "top", False: "bottom"}}}
    # Two directions available if same point
    if p1[0][0] == p2[0][0] and p1[0][1] == p2[0][1]:
        return p2[1] in contigous_directions["a"][p1[1]]
    # Same direction available if same row only in horizontal
    elif p1[0][0] == p2[0][0]:
        return p2[1] in contigous_directions["x"][p1[1]]
    # Same direction available if same column only in vertical
    elif p1[0][1] == p2[0][1]:
        return p2[1] in contigous_directions["y"][p1[1]]
    # Two direction available if not adiacent points on condition
    else:
        if p2[0][1] > p1[0][1] and p1[1] == "right" or p2[0][1] < p1[0][1] and p1[1] == "left":
            return p2[1] == contigous_directions["s"][p1[1]][p2[0][0] > p1[0][0]]
        elif p2[0][0] < p1[0][0] and p1[1] == "top" or p2[0][0] > p1[0][0] and p1[1] == "bottom":
            return p2[1] == contigous_directions["s"][p1[1]][p2[0][1] > p1[0][1]]
        else:
            return False


def process_points(data):
    pts = {}
    rows = {}
    min_x = None
    min_y = None
    max_x = None
    max_y = None
    unique_row_indeces = []
    unique_column_indeces = []

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
        if p["x"] not in unique_row_indeces:
            unique_row_indeces.append(p["x"])
        if p["y"] not in unique_column_indeces:
            unique_column_indeces.append(p["y"])

    # Create point cloud
    matrix = np.zeros((len(unique_row_indeces), len(unique_column_indeces)))
    unique_row_indeces = np.array(sorted(unique_row_indeces))
    unique_column_indeces = np.array(sorted(unique_column_indeces))
    point_map = {}
    rev_map = {}
    for p in data:
        x = np.where(unique_row_indeces == p["x"])[0][0]
        y = np.where(unique_column_indeces == p["y"])[0][0]
        point_map[p["x"], p["y"]] = x, y
        rev_map[x, y] = [p["x"], p["y"], p["z"]]
        matrix[point_map[p["x"], p["y"]]] = p["z"]

    # Iterate over not-empty rows and select only significant points for surface
    is_reverse = False
    points = []
    for r in rows:
        if len(rows[r]) == 1:
            points.append([r, rows[r][0], pts[r, rows[r][0]]])
        else:
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
        traj.append({"x": p[0], "y": p[1], "z": p[2], "time": step_time, "side": "surface"})
        total_time += step_time
        lp = p

    # Iterate over matrix to select only border points
    min_x_ind = 0
    max_x_ind = len(unique_row_indeces) - 1
    min_y_ind = 0
    max_y_ind = len(unique_column_indeces) - 1
    _pts = []
    fin_pts = []
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            if matrix[i][j] != 0:
                # Check whether point is on the working area borders
                if i == min_x_ind or i == max_x_ind or j == min_y_ind or j == max_y_ind:
                    if i == min_x_ind:
                        _pts.append((rev_map[i, j], "top"))
                        if (j != min_y_ind and j != max_y_ind) and matrix[i][j - 1] == 0:
                            _pts.append((rev_map[i, j], "left"))
                        if (j != min_y_ind and j != max_y_ind) and matrix[i][j + 1] == 0:
                            _pts.append((rev_map[i, j], "right"))
                        if i != max_y_ind and matrix[i + 1][j] == 0:
                            _pts.append((rev_map[i, j], "bottom"))
                    if i == max_x_ind:
                        _pts.append((rev_map[i, j], "bottom"))
                        if (j != min_y_ind and j != max_y_ind) and matrix[i][j - 1] == 0:
                            _pts.append((rev_map[i, j], "left"))
                        if (j != min_y_ind and j != max_y_ind) and matrix[i][j + 1] == 0:
                            _pts.append((rev_map[i, j], "right"))
                        if i != min_x_ind and matrix[i - 1][j] == 0:
                            _pts.append((rev_map[i, j], "top"))
                    if j == min_y_ind:
                        _pts.append((rev_map[i, j], "left"))
                        if (i != min_x_ind and i != max_x_ind) and matrix[i - 1][j] == 0:
                            _pts.append((rev_map[i, j], "top"))
                        if j != max_y_ind and matrix[i][j + 1] == 0:
                            _pts.append((rev_map[i, j], "right"))
                        if (i != min_x_ind and i != max_x_ind) and matrix[i + 1][j] == 0:
                            _pts.append((rev_map[i, j], "bottom"))
                    if j == max_y_ind:
                        _pts.append((rev_map[i, j], "right"))
                        if (i != min_x_ind and i != max_x_ind) and matrix[i - 1][j] == 0:
                            _pts.append((rev_map[i, j], "top"))
                        if j != min_y_ind and matrix[i][j - 1] == 0:
                            _pts.append((rev_map[i, j], "left"))
                        if (i != min_x_ind and i != max_x_ind) and matrix[i + 1][j] == 0:
                            _pts.append((rev_map[i, j], "bottom"))
                else:
                    if matrix[i - 1][j] == 0:
                        _pts.append((rev_map[i, j], "top"))
                    if matrix[i][j - 1] == 0:
                        _pts.append((rev_map[i, j], "left"))
                    if matrix[i][j + 1] == 0:
                        _pts.append((rev_map[i, j], "right"))
                    if matrix[i + 1][j] == 0:
                        _pts.append((rev_map[i, j], "bottom"))

    # Initialize border trajectory with last point
    start_stop = None
    label = None
    if len(fin_pts) == 0:
        for i, p in enumerate(_pts):
            if p[0] == lp:
                start_stop, label = _pts.pop(i)
                fin_pts.append((start_stop, label))
                break
    # Iterate over points to select border trajectory
    while len(_pts) > 0:
        best_match = None
        for i, p in enumerate(_pts):
            t = compute_time(fin_pts[-1][0], p[0])
            if best_match is None or (is_contigous(fin_pts[-1], p) and t <= best_match[1]):
                best_match = i, t
        element = _pts.pop(best_match[0])
        fin_pts.append(element)

    # Iterate over points to compute times of the second part of the trajectory (borders)
    for i, px in enumerate(fin_pts):
        p = px[0]
        step_time = 0 if lp is None else compute_time(p, lp)
        # If step_time = 0, then send command to move from surface to side
        if i == 0:
            step_time = MOVE_FROM_SURFACE_TO_SIDE_CONST
        # If current and last point are external, then send command to move from one side to the other
        elif p != lp and \
                (p[0] == lp[0] == min_x or p[1] == lp[1] == min_y or p[0] == lp[0] == max_x or p[1] == lp[1] == max_y):
            step_time = MOVE_FROM_SIDE_TO_SIDE_CONST
        traj.append({"x": p[0], "y": p[1], "z": p[2], "time": step_time, "side": px[1]})
        total_time += step_time
        lp = p
    # Add last point to complete trajectory where it started
    step_time = compute_time(lp, start_stop)
    traj.append({"x": start_stop[0], "y": start_stop[1], "z": start_stop[2], "time": step_time, "side": label})
    total_time += step_time
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
