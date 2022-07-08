from .base import Base
from random import choice


class Feedback(Base):

    def __init__(self):
        super().__init__("Feedback", "This entity represent a feedback from a quality checker")

    def get(self):
        self.next()
        return {
            "id": "urn:ngsi-ld:" + self.urlname + ":id:" + str(self.id),
            "type": self.class_type,
            "description": {
                "type": "Text",
                "value": self.description},
            "result": {
                "type": "Text",
                "value": choice(["high", "medium", "low"])}
        }
