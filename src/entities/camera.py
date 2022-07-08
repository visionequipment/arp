from datetime import datetime

from .base import Base


class Camera(Base):

    def __init__(self, name, num, manufacturer, cam_model):
        super().__init__("Camera", "This entity represents a camera")
        self.camera_name = name
        self.__camera_num = num
        self.__start_date_time = datetime.utcnow().replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")
        self.end_date_time = datetime.utcnow().replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")
        self.camera_status = "idle"
        self.hardware_trigger = False
        self.exposure = 1000
        self.__manufacturer = manufacturer
        self.__camera_model = cam_model
        self.error_status = "No error"

    def get(self):
        self.next()
        return {
            "id": "urn:ngsi-ld:" + self.urlname + ":id:" + str(self.id),
            "type": self.class_type,
            "name": {
                "type": "Text",
                "value": self.camera_name},
            "serialNumber": {
                "type": "Text",
                "value": self.__camera_num},
            "dateCreated": {
                "type": "Text",
                "value": datetime.utcnow().replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")},
            "description": {
                "type": "Text",
                "value": self.description},
            "startDateTime": {
                "type": "Text",
                "value": self.__start_date_time},
            "endDateTime": {
                "type": "Text",
                "value": self.end_date_time},
            "status": {
                "type": "Text",
                "value": self.camera_status},
            "hardwareTrigger": {
                "type": "Boolean",
                "value": self.hardware_trigger},
            "exposure": {
                "type": "Integer",
                "value": self.exposure},
            "brand": {
                "type": "Text",
                "value": self.__manufacturer},
            "model": {
                "type": "Text",
                "value": self.__camera_model},
            "errorStatus": {
                "type": "Text",
                "value": self.error_status}
        }
