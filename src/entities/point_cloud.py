from .base import Base


class PointCloud(Base):

    def __init__(self):
        super().__init__("PointCloud", "Point Cloud generated from image by the vision system")
        self.input_image_link = "urn:ngsi-ld:IMAGE:id:1"
        self.status = True
        self.error = "No error"
        self.pcl = []
        with open(r"../assets/raw_point_cloud.txt", "r") as d:
            lines = [l.replace("\n", "") for l in d.readlines()]
        for l in lines:
            line = []
            data = l.split("@")
            for d in data:
                if d != "":
                    x, y, z = d.split("#")
                    line.append({"x": float(x), "y": float(y), "z": float(z)})
            self.pcl.append(line)

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
                "value": self.pcl,
            },
            "status": {
                "type": "Boolean",
                "value": self.status},
            "error": {
                "type": "Text",
                "value": self.error}
        }
