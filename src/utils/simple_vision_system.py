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
    feed = Feedback()

    ents = [["Camera", cam, [1]], ["Image", img, [1, 5, 7, 11, 13, 15, 19]],
            ["PointCloud", pcloud, [1, 5, 7, 11, 13, 15, 19]], ["Robot", rob, [1]], ["OrbSander", orb, [1]],
            ["DevOperation", op, [r for r in range(1, 20)]], ["Feedback", feed, [11, 12, 13, 20, 21, 22, 23]]]

    # Generate data

    stored_devoperations = []
    stored_feedbacks = []

    s = datetime.utcnow().replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")
    for count in range(1, 25):
        print(count)
        time.sleep(5)
        for e in ents:
            if len(e[2]) > 0 and count == e[2][0]:
                print(e[0])
                e[2] = e[2][1:]
                elem = e[1].get()
                if e[0] == "DevOperation":
                    stored_devoperations.append(elem)
                if e[0] == "Feedback":
                    stored_feedbacks.append(elem)
                send_request("http://localhost:1026/v2/entities/", elem)
    e = datetime.utcnow().replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")

    r = requests.get("http://localhost:1026/v2/entities/?type=Measurement")
    stored_measurements = r.content.decode('UTF-8')

    # Compute KPIs
    qual = KPI("OEE Quality", "Quality", feedbacks=stored_feedbacks)
    perf = KPI("OEE Performance", "Performance", devoperations=stored_devoperations, measurements=stored_measurements)
    avail = KPI("OEE Availability", "Availability", devoperations=stored_devoperations)

    print("Sending KPIs")
    send_request("http://localhost:1026/v2/entities/", qual.get(s, e))
    send_request("http://localhost:1026/v2/entities/", perf.get(s, e))
    send_request("http://localhost:1026/v2/entities/", avail.get(s, e))
