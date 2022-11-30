import json
import time
import requests
from datetime import datetime

from ..entities import *


def send_request(url, jdata):
    r = requests.post(url, data=json.dumps(jdata), headers={"content-type": "application/json"})
    print(r.content)


if __name__ == "__main__":

    cam = Camera("MyCam", "x1y2", "X", "Y")
    img = Image("RGB", [1024, 700])
    rob = Robot("MyRobot", "Y1X2", "X", "Y")
    orb = OrbitalSander("MyOrb", "SN123", "X", "Y")
    op = DeviceOperation("Sanding", "Wood", "Fine", "Z", "x1")
    pcloud = PointCloud()

    ents = [["Camera", cam, [1]], ["Image", img, [1, 5, 7, 11, 13, 15, 19]],
            ["PointCloud", pcloud, [1, 5, 7, 11, 13, 15, 19]], ["Robot", rob, [1]], ["OrbSander", orb, [1]],
            ["DevOperation", op, [r for r in range(1, 20)]]]

    # Generate data

    for count in range(1, 25):
        print(count)
        time.sleep(5)
        for e in ents:
            if len(e[2]) > 0 and count == e[2][0]:
                print(e[0])
                e[2] = e[2][1:]
                elem = e[1].get()
                send_request("http://localhost:1026/v2/entities/", elem)
