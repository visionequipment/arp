from datetime import datetime

from .base import Base


class Image(Base):

    def __init__(self, tp, res):
        super().__init__("Image", "Image captured by a camera")
        self.__image_type = tp
        self.__resolution = res if type(res) == list else [-1, -1]

    def get(self):
        self.next()
        return {
            "id": "urn:ngsi-ld:" + self.urlname + ":id:" + str(self.id),
            "type": self.class_type,
            "description": {
                "type": "Text",
                "value": self.description},
            "linkToImage": {
                "type": "Text",
                "value": ""},
            "cameraIdentifier": {
                "type": "Text",
                "value": "urn:ngsi-ld:CAMERA:id:1"},
            "dateCaptured": {
                "type": "Text",
                "value": datetime.utcnow().replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")},
            "imageFormat": {
                "type": "Text",
                "value": self.__image_type},
            "imageResolution": {
                "type": "object",
                "value": {
                    "type": "array",
                    "value": self.__resolution
                }
            }
        }
