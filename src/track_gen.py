import os
import json
import requests
import numpy as np
from loguru import logger
from flask import Flask, request
from concurrent.futures import ThreadPoolExecutor

from entities import Measurement

app = Flask(__name__)

hostname = os.environ['ORION_HOST']
port = os.environ["TRACKGEN_PORT"]

robot_speed = 20
sander_diameter = 125
overlap_percentage = 25
overlap_dist = sander_diameter * (100 - overlap_percentage) / 100
MOVE_FROM_SIDE_TO_SIDE_CONST = 0.0001


def compute_time(pa, pb):
    return np.sqrt((pa[0]-pb[0])**2 + (pa[1]-pb[1])**2 + (pa[2]-pb[2])**2) / robot_speed


def line_from_points(P, Q):
    a = Q[1] - P[1]
    b = P[0] - Q[0]
    c = a*(P[0]) + b*(P[1])
    if c != 0:
        a /= c
        b /= c
        c = 1
    return a, b, c


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
            if p["y"] in rows:
                rows[p["y"]].append(p["x"])
                pts[(p["y"], p["x"])] = p["z"]
            else:
                rows[p["y"]] = [p["x"]]
                pts[(p["y"], p["x"])] = p["z"]
        if min_x is None or p["y"] < min_x:
            min_x = p["y"]
        if min_y is None or p["x"] < min_y:
            min_y = p["x"]
        if max_x is None or p["y"] > max_x:
            max_x = p["y"]
        if max_y is None or p["x"] > max_y:
            max_y = p["x"]
        if p["y"] not in unique_row_indeces:
            unique_row_indeces.append(p["y"])
        if p["x"] not in unique_column_indeces:
            unique_column_indeces.append(p["x"])

    # Estimate number of rows to skip 
    point_dist = np.abs(data[1]["x"] - data[0]["x"]) if np.abs(data[1]["x"] - data[0]["x"]) != 0 else np.abs(data[1]["y"] - data[0]["y"])
    n_skipped_lines = int(overlap_dist / point_dist)

    # Create point cloud
    matrix = np.zeros((len(unique_row_indeces), len(unique_column_indeces)))
    unique_row_indeces = np.array(sorted(unique_row_indeces))
    unique_column_indeces = np.array(sorted(unique_column_indeces))
    point_map = {}
    rev_map = {}
    for p in data:
        y = np.where(unique_row_indeces == p["y"])[0][0]
        x = np.where(unique_column_indeces == p["x"])[0][0]
        point_map[p["y"], p["x"]] = y, x
        rev_map[y, x] = [p["y"], p["x"], p["z"]]
        matrix[point_map[p["y"], p["x"]]] = p["z"]

    # Iterate over not-empty rows and select only significant points for surface
    is_reverse = False
    points = []
    for i, r in enumerate(rows):
        if len(rows[r]) == 1:
            points.append([r, rows[r][0], pts[r, rows[r][0]]])
        else:
            if i % n_skipped_lines == 0:
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
    fp = None
    for p in points:
        step_time = 0 if lp is None else compute_time(p, lp)
        if fp == None:
            fp = p
        traj.append({"x": p[1], "y": p[0], "z": p[2], "time": step_time, "side": "surface"})
        total_time += step_time
        lp = p

    # Iterate over matrix to select only border points
    min_x_ind = 0
    max_x_ind = len(unique_row_indeces) - 1
    min_y_ind = 0
    max_y_ind = len(unique_column_indeces) - 1
    _pts = []
    inter_pts = []
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
                    if matrix[i-1][j] == 0:
                        _pts.append((rev_map[i, j], "top"))
                    if matrix[i][j-1] == 0:
                        _pts.append((rev_map[i, j], "left"))
                    if matrix[i][j+1] == 0:
                        _pts.append((rev_map[i, j], "right"))
                    if matrix[i+1][j] == 0:
                        _pts.append((rev_map[i, j], "bottom"))

    # Initialize border trajectory with first point
    start_stop = None
    label = None
    if len(inter_pts) == 0:
        for i, p in enumerate(_pts):
            if p[0] == fp:
                start_stop, label = _pts.pop(i)
                inter_pts.append((start_stop, label))
                break

    # Iterate over points to select border trajectory
    while len(_pts) > 0:
        best_match = None
        for i, p in enumerate(_pts):
            t = compute_time(inter_pts[-1][0], p[0])
            if best_match is None or (is_contigous(inter_pts[-1], p) and t <= best_match[1]):
                best_match = i, t
        element = _pts.pop(best_match[0])
        inter_pts.append(element)

    # Iterate over selected points to remove intermediate ones
    line = None
    lpoint = None
    spoint = None
    fin_pts = []
    lines = []
    num = 0
    inter_pts.append(inter_pts[0]) # Same starting and ending points
    for i, px in enumerate(inter_pts):
        p = px[0]
        if lpoint is None:
            spoint = px
            lpoint = p
            fin_pts.append(px)
            continue
        if p == lpoint:
            continue
        if line is None:
            line = line_from_points(lpoint[:2], p[:2])
            num += 1
        else:
            cur_line = line_from_points(lpoint[:2], p[:2])
            if cur_line == line:
                num += 1
            else:
                lines.append([line, num, (spoint, inter_pts[i-1])])
                num = 1
                line = cur_line
                spoint = inter_pts[i-1]
                fin_pts.append(inter_pts[i-1])
        lpoint = p
    lines.append([line, num, (spoint, p)])
    fin_pts.append(inter_pts[i])

    # Check if it is clockwise or not
    if fin_pts[1][0][1] > fin_pts[0][0][1]:
        fin_pts = list(reversed(fin_pts))

    # Merge lines
    v_1 = None
    u_1 = None
    counter = 0
    rem_pnts = []
    temp = None
    for l in lines:
        coeff, length, points = l
        if v_1 is None:
            v_1 = l
            continue
        if u_1 is None:
            if ((coeff[0] == 0 and v_1[0][1] != 0) or (coeff[1] == 0 and v_1[0][0] != 0) or \
               (v_1[0][0] * coeff[0] > 0 and v_1[0][1] * coeff[1] > 0)) and (length == 1 or v_1[1] == 1):
                u_1 = l
            else:
                v_1 = None
            continue
        if counter == 0:
            if (coeff[0] == 0 and v_1[0][0] == 0) or (coeff[1] == 0 and v_1[0][1] == 0) or \
                (coeff[0] / coeff[1] == v_1[0][0] / v_1[0][1]):
                if v_1[1] == 1 != length:
                    counter = 0
                    v_1 = None
                    u_1 = None
                    temp = None
                    continue
                counter = 1
                temp = l
                if u_1[2][0][0] not in rem_pnts:
                    rem_pnts.append(u_1[2][0])
                if u_1[2][0][1] not in rem_pnts:
                    rem_pnts.append(u_1[2][1])
                if temp[2][0][0] not in rem_pnts:
                    rem_pnts.append(temp[2][0])
            else:
                counter = 0
                v_1 = None
                u_1 = None
                temp = None
        else:
            if (coeff[0] == 0 and u_1[0][0] == 0) or (coeff[1] == 0 and u_1[0][1] == 0) or \
                (coeff[0] / coeff[1] == u_1[0][0] / u_1[0][1]):
                if u_1[1] == 1 != length:
                    counter = 0
                    v_1 = None
                    u_1 = None
                    temp = None
                    continue
                counter = 0
                temp = l
                if temp[2][0][0] not in rem_pnts:
                    rem_pnts.append(temp[2][0])
            else:
                counter = 1
                v_1 = None
                u_1 = None
                temp = None

    # To merge lines, remove other "intermediate" points
    final_pts = []
    for p in fin_pts:
        if p not in rem_pnts:
            final_pts.append(p)

    # Iterate over points to compute times of the second part of the trajectory (borders)
    for i, px in enumerate(final_pts):
        p = px[0]
        step_time = 0 if lp is None else compute_time(p, lp)
        # If current and last point are external, then send command to move from one side to the other
        if p != lp and \
                (p[0] == lp[0] == min_x or p[1] == lp[1] == min_y or p[0] == lp[0] == max_x or p[1] == lp[1] == max_y):
            step_time = MOVE_FROM_SIDE_TO_SIDE_CONST
        traj.append({"x": p[1], "y": p[0], "z": p[2], "time": step_time, "side": px[1]})
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
    return trajectory


@app.route("/notify/", methods=['POST'])
def notify():
    data = request.get_json()
    return return_trajectory(data)


@app.route("/speed/", methods=['POST'])
def speed():
    global robot_speed
    data = request.get_json()
    robot_speed = float(data["data"][0]['targetSpeed']["value"])
    logger.info(f"New speed: {robot_speed}")
    return "OK"


@app.route("/overlap/", methods=['POST'])
def overlap():
    global overlap_percentage
    global overlap_dist
    data = request.get_json()
    requiredQuality = data["data"][0]['requiredQuality']["value"]
    if requiredQuality == "Low":
        overlap_percentage = 25
        overlap_dist = sander_diameter * (100 - overlap_percentage) / 100
    if requiredQuality == "Medium":
        overlap_percentage = 37
        overlap_dist = sander_diameter * (100 - overlap_percentage) / 100
    elif requiredQuality == "High":
        overlap_percentage = 50
        overlap_dist = sander_diameter * (100 - overlap_percentage) / 100
    else:
        overlap_percentage = 25
        overlap_dist = sander_diameter * (100 - overlap_percentage) / 100
    logger.info(f"New overlap percentage: {overlap_percentage}")
    return "OK"


@app.route("/diameter/", methods=['POST'])
def diameter():
    global sander_diameter
    global overlap_dist
    data = request.get_json()
    sander_diameter = float(data["data"][0]['diameter']["value"])
    overlap_dist = sander_diameter * (100 - overlap_percentage) / 100
    logger.info(f"New sander diameter: {sander_diameter}")
    return "OK"


@app.route("/ping/", methods=['GET'])
def ping():
    return "OK"


if __name__ == "__main__":
    count = 0
    logger.info(hostname)
    meas = Measurement()
    app.run(host="0.0.0.0", port=port)
