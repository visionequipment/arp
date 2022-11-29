import json
import requests


def send_request(url, jdata):
    r = requests.post(url, data=json.dumps(jdata), headers={"content-type": "application/json"})
    print(r.content)


if __name__ == "__main__":

    subs = [{"description": "Notify TrackGen of a new Point Cloud", "subject": {
                "entities": [{"idPattern": ".*", "type": "PointCloud"}],
                "condition": {"attrs": ["pointCloud"]}},
             "url": "http://trackgen:5050/notify/", "attrs": "pointCloud"},

            {"description": "Notify Robot of new trajectories", "subject": {
                "entities": [{"idPattern": ".*", "type": "Measurement"}],
                "condition": {"attrs": ["outputTrajectory"]}},
             "url": "http://host.docker.internal:5500/notify/", "attrs": "outputTrajectory"},

            {"description": "Notify TrackGen of new robot speed", "subject": {
                "entities": [{"idPattern": ".*ROBOT.*", "type": "Device"}],
                "condition": {"attrs": ["extraParameters"]}},
             "url": "http://trackgen:5050/speed/", "attrs": "extraParameters"}]

    for s in subs:
        sub = {
            "description": s["description"], "subject": s["subject"],
            "notification": {"http": {"url": s["url"]}, "attrs": [s["attrs"]]}
        }
        send_request("http://localhost:1026/v2/subscriptions/", sub)
