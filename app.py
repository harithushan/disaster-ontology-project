from flask import Flask, jsonify
from owlready2 import *

app = Flask(__name__)

onto = get_ontology("./ontology/ontology.rdf").load()

@app.route("/disasters")
def disasters():
    data = []
    for d in onto.Disaster.instances():
        data.append({
            "name": d.name,
            "type": d.is_a[0].name,
            "severity": d.severityLevel[0] if d.severityLevel else "N/A",
            "location": d.occursIn[0].name if d.occursIn else "Unknown",
            "resources": [r.name for r in d.requiresResource]
        })
    return jsonify(data)

@app.route("/shelters")
def shelters():
    data = []
    for s in onto.Shelter.instances():
        data.append({
            "name": s.name,
            "capacity": s.capacity[0] if s.capacity else 0
        })
    return jsonify(data)

@app.route("/volunteers")
def volunteers():
    data = []
    for v in onto.Volunteer.instances():
        data.append({
            "name": v.hasName[0],
            "assigned_shelter": v.assignedTo[0].name
        })
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)
