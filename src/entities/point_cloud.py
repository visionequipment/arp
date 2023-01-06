from .base import Base


class PointCloud(Base):

    def __init__(self):
        super().__init__("PointCloud", "Point Cloud generated from image by the vision system")
        self.input_image_link = "urn:ngsi-ld:IMAGE:id:1"
        self.status = True
        self.error = "No error"

    def get(self):
        self.next()
        return {
            "id": "urn:ngsi-ld:" + self.urlname + ":id:" + str(self.id),
            "type": self.class_type,
            "description": {
                "type": "Text",
                "value": self.description},
            "imageIdentifier": {
                "type": "Text",
                "value": self.input_image_link},
            "pointCloud": {
                "type": "StructuredValue",
                "value": [
                    [{"y": 0, "x": 0, "z": -100},
                     {"y": 20, "x": 0, "z": -100},
                     {"y": 40, "x": 0, "z": -100},
                     {"y": 60, "x": 0, "z": -100},
                     {"y": 80, "x": 0, "z": -100}],
                    [{"y": 0, "x": 20, "z": -100},
                     {"y": 20, "x": 20, "z": 100},
                     {"y": 40, "x": 20, "z": 100},
                     {"y": 60, "x": 20, "z": 100 if self.id < 3 else -100},
                     {"y": 80, "x": 20, "z": -100}],
                    [{"y": 0, "x": 40, "z": -100},
                     {"y": 20, "x": 40, "z": 100},
                     {"y": 40, "x": 40, "z": 100},
                     {"y": 60, "x": 40, "z": 100},
                     {"y": 80, "x": 40, "z": -100}],
                    [{"y": 0, "x": 60, "z": -100},
                     {"y": 20, "x": 60, "z": 100},
                     {"y": 40, "x": 60, "z": 100},
                     {"y": 60, "x": 60, "z": 100 if self.id > 3 else -100},
                     {"y": 80, "x": 60, "z": -100}],
                    [{"y": 0, "x": 80, "z": -100},
                     {"y": 20, "x": 80, "z": -100},
                     {"y": 40, "x": 80, "z": -100},
                     {"y": 60, "x": 80, "z": -100},
                     {"y": 80, "x": 80, "z": -100}]
                ]
            },
            "status": {
                "type": "Boolean",
                "value": self.status},
            "error": {
                "type": "Text",
                "value": self.error}
        }
