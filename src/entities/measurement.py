from .base import Base


class Measurement(Base):

    def __init__(self):
        super().__init__("Measurement", "Estimated trajectory")
        self.status = True
        self.error = "No error"
        self.overlap = True
        self.point_density = 10.0

    def get(self, traj, input_pc, total_time):
        self.next()
        return {
            "id": "urn:ngsi-ld:" + self.urlname + ":id:" + str(self.id),
            "type": self.class_type,
            "description": {
                "type": "Text",
                "value": self.description},
            "pointCloudIdentifier": {
                "type": "Text",
                "value": input_pc},
            "outputTrajectory": {
                "type": "StructuredValue",
                "value": traj},
            "status": {
                "type": "Boolean",
                "value": self.status},
            "error": {
                "type": "Text",
                "value": self.error},
            "overlap": {
                "type": "Boolean",
                "value": self.overlap},
            "pointDensity": {
                "type": "Float",
                "value": self.point_density},
            "estimatedWorkpieceProcessingTime": {
                "type": "Float",
                "value": total_time}
        }
