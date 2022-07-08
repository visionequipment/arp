from datetime import datetime
from random import random

from .base import Base


class DeviceOperation(Base):

    def __init__(self, rec, mat, quality, oper_name, session):
        super().__init__("DeviceOperation", "Sanding a wooden board", "Sanding")
        self.active_recipe = rec
        self.type_of_material = mat
        self.required_quality = quality
        self.operator = oper_name
        self.session = session
        self.start = None
        self.sanding_progress = 0.0
        self.device = "urn:ngsi-ld:ORBSANDER:id:1"

    def get(self):
        self.next()
        if self.id in [2, 8, 15]:
            self.sanding_progress = 30
            status = "Error"
            end = datetime.utcnow().replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")
        elif self.id in [4, 6, 10, 12, 14, 18, 20]:
            status = "Finished"
            self.sanding_progress = 100
            end = datetime.utcnow().replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")
        else:
            status = "Running"
            self.sanding_progress = 0 if self.sanding_progress == 100 else 50
            end = None
            self.start = datetime.utcnow().replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")
        return {
            "id": "urn:ngsi-ld:" + self.urlname + ":id:" + str(self.id),
            "type": self.class_type,
            "description": {
                "type": "Text",
                "value": self.description},
            "activeRecipe": {
                "type": "Text",
                "value": self.active_recipe},
            "typeOfMaterial": {
                "type": "Text",
                "value": self.type_of_material},
            "requiredQuality": {
                "type": "Text",
                "value": self.required_quality},
            "operator": {
                "type": "Text",
                "value": self.operator},
            "deviceIdentifier": {
                "type": "Text",
                "value": self.device},
            "session": {
                "type": "Text",
                "value": self.session},
            "status": {
                "type": "Text",
                "value": status},
            "start": {
                "type": "Text",
                "value": self.start},
            "end": {
                "type": "Text",
                "value": end},
            "progress": {
                "type": "Float",
                "value": self.sanding_progress},
            "nominalValue": {
                "type": "Float",
                "value": float(random())},
            "operatingValue": {
                "type": "Float",
                "value": float(random())},
            "extraParameters": {
                "type": "StructuredValue",
                "value": [{"parameter": "sandingPaperUsage", "value": 0.99}]
            }
        }
