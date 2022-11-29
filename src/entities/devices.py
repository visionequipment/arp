from .base import Base


class Device(Base):

    def __init__(self, ent_name, des, name, sn, brand, model):
        super().__init__("Device", des, ent_name)
        self.name = name
        self.serial_num = sn
        self.brand = brand
        self.model = model
        self.status = "on"
        self.error = "No error"

    def get(self):
        self.next()
        return {
            "id": "urn:ngsi-ld:" + self.urlname + ":id:" + str(self.id),
            "type": self.class_type,
            "description": {
                "type": "Text",
                "value": self.description},
            "name": {
                "type": "Text",
                "value": self.name},
            "serialNumber": {
                "type": "Text",
                "value": self.serial_num},
            "brand": {
                "type": "Text",
                "value": self.brand},
            "model": {
                "type": "Text",
                "value": self.model},
            "status": {
                "type": "Text",
                "value": self.status},
            "error": {
                "type": "Text",
                "value": self.error}
        }


class Robot(Device):

    def __init__(self, name, sn, brand, model):
        super().__init__("Robot", "Robot device", name, sn, brand, model)

    def get(self):
        res = super().get()
        res["extraParameters"] = {
            "type": "StructuredValue",
            "value": [
                {"parameter": "availableArea", "value":
                    [
                        {"x": 0, "y": 0, "z": 0},
                        {"x": 1000, "y": 0, "z": 0},
                        {"x": 0, "y": 1000, "z": 0},
                        {"x": 1000, "y": 1000, "z": 0},
                        {"x": 0, "y": 0, "z": 1000},
                        {"x": 1000, "y": 0, "z": 1000},
                        {"x": 0, "y": 1000, "z": 1000},
                        {"x": 1000, "y": 1000, "z": 1000},
                    ]
                },
                {
                    "parameter": "speed", "value": 20
                }
            ]
        }
        return res


class OrbitalSander(Device):

    def __init__(self, name, sn, brand, model):
        super().__init__("OrbitalSander", "Orbital Sander", name, sn, brand, model)

    def get(self):
        res = super().get()
        res["diameter"] = {
                "type": "Float",
                "value": float(125)}
        return res
