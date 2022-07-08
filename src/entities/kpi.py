from .base import Base


class KPI(Base):

    def __init__(self, ent_des, opt_name, **kwargs):
        super().__init__("KeyPerformanceIndicator", ent_des, opt_name)
        self.devoperations = kwargs.get("devoperations", [])
        self.measurements = kwargs.get("measurements", [])
        self.feedbacks = kwargs.get("feedbacks", [])

    def get(self, s, e):
        self.next()
        kpi_val = 0.0
        formula = ""
        aggData = []
        if len(self.feedbacks) > 0:
            kpi_val = 100 * (len([f for f in self.feedbacks if f["result"]["value"] != "low"]) / len(self.feedbacks))
            formula = "100 x ratio between the number of good processed parts and the number of total processed parts"
            aggData = [{"entityType": "Feedback", "attrs": ["result"]}]
        elif len(self.measurements) > 0:
            # performance
            pass
        else:
            # availability
            pass
        return {
            "id": "urn:ngsi-ld:" + self.urlname + ":id:" + str(self.id),
            "type": self.class_type,
            "description": {
                "type": "Text",
                "value": self.description},
            "category": {
                "type": "Text",
                "value": "quantitative"},
            "startTime": {
                "type": "Text",
                "value": s},
            "endTime": {
                "type": "Text",
                "value": e},
            "calculationMethod":  {
                "type": "Text",
                "value": "automatic"},
            "calculationFormula": {
                "type": "Text",
                "value": formula},
            "process": {
                "type": "Text",
                "value": "Sanding"},
            "calculationFrequency": {
                "type": "Text",
                "value": "daily"},
            "kpiValue": {
                "type": "Float",
                "value": kpi_val},
            "aggregatedData": {
                "type": "array",
                "value": aggData}
        }
