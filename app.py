from flask import Flask, jsonify, request
from flask_cors import CORS
from owlready2 import *
import os

app = Flask(__name__)
CORS(app)

# Load ontology
ONTOLOGY_PATH = "./ontology/disaster_ontology.rdf"
onto = get_ontology(ONTOLOGY_PATH).load()

@app.route("/")
def home():
    return jsonify({
        "message": "Sri Lanka Disaster Management Ontology API",
        "endpoints": {
            "disasters": "/disasters",
            "disasters_by_severity": "/disasters/severity/<level>",
            "disasters_by_type": "/disasters/type/<type>",
            "disasters_active": "/disasters/active",
            "shelters": "/shelters",
            "shelters_available": "/shelters/available",
            "shelter_by_id": "/shelter/<name>",
            "volunteers": "/volunteers",
            "volunteers_by_shelter": "/volunteers/shelter/<shelter>",
            "resources": "/resources",
            "resources_low": "/resources/low",
            "locations": "/locations",
            "districts": "/districts",
            "provinces": "/provinces",
            "organizations": "/organizations",
            "statistics": "/statistics"
        }
    })

# ==================== DISASTER ENDPOINTS ====================

# Helper function for disaster serialization
def _serialize_disaster(d):
    """Serialize a disaster object to a consistent dictionary format"""
    return {
        "id": d.name,
        "name": d.hasName[0] if d.hasName else d.name,
        "type": d.__class__.__name__,
        "severity": d.severityLevel[0] if d.severityLevel else "N/A",
        "location": d.occursIn[0].name if d.occursIn else "Unknown",
        "location_name": d.occursIn[0].hasName[0] if d.occursIn and d.occursIn[0].hasName else "Unknown",
        "date": str(d.dateOccurred[0]) if d.dateOccurred else "N/A",
        "status": d.status[0] if d.status else "Unknown",
        "resources": [r.hasName[0] if r.hasName else r.name for r in d.requiresResource],
        "affected_count": sum([pop.affectedCount[0] for pop in onto.AffectedPopulation.instances() 
                              if d.name in pop.hasName[0]]) if onto.AffectedPopulation.instances() else 0
    }

@app.route("/disasters")
def get_disasters():
    """Get all disasters"""
    data = []
    for d in onto.Disaster.instances():
        data.append(_serialize_disaster(d))
    return jsonify(data)

@app.route("/disasters/severity/<level>")
def get_disasters_by_severity(level):
    """Get disasters by severity level (Low, Medium, High)"""
    data = []
    for d in onto.Disaster.instances():
        if d.severityLevel and d.severityLevel[0].lower() == level.lower():
            data.append(_serialize_disaster(d))
    return jsonify(data)

@app.route("/disasters/type/<disaster_type>")
def get_disasters_by_type(disaster_type):
    """Get disasters by type (Flood, Landslide, Cyclone, etc.)"""
    data = []
    type_class = getattr(onto, disaster_type, None)
    if type_class:
        for d in type_class.instances():
            data.append(_serialize_disaster(d))
    return jsonify(data)

@app.route("/disasters/active")
def get_active_disasters():
    """Get all active disasters"""
    data = []
    for d in onto.Disaster.instances():
        if d.status and d.status[0] == "Active":
            data.append(_serialize_disaster(d))
    return jsonify(data)

# ==================== SHELTER ENDPOINTS ====================

@app.route("/shelters")
def get_shelters():
    """Get all shelters"""
    data = []
    for s in onto.Shelter.instances():
        capacity = s.capacity[0] if s.capacity else 0
        occupancy = s.currentOccupancy[0] if s.currentOccupancy else 0
        available = capacity - occupancy
        
        shelter_info = {
            "id": s.name,
            "name": s.hasName[0] if s.hasName else s.name,
            "capacity": capacity,
            "current_occupancy": occupancy,
            "available_space": available,
            "occupancy_rate": round((occupancy / capacity * 100), 1) if capacity > 0 else 0,
            "status": s.status[0] if s.status else "Unknown",
            "contact": s.contactNumber[0] if s.contactNumber else "N/A"
        }
        data.append(shelter_info)
    return jsonify(data)

@app.route("/shelters/available")
def get_available_shelters():
    """Get shelters with available space"""
    data = []
    for s in onto.Shelter.instances():
        capacity = s.capacity[0] if s.capacity else 0
        occupancy = s.currentOccupancy[0] if s.currentOccupancy else 0
        
        if capacity > occupancy:
            shelter_info = {
                "id": s.name,
                "name": s.hasName[0] if s.hasName else s.name,
                "available_space": capacity - occupancy,
                "capacity": capacity,
                "status": s.status[0] if s.status else "Unknown"
            }
            data.append(shelter_info)
    return jsonify(data)

@app.route("/shelter/<shelter_name>")
def get_shelter_details(shelter_name):
    """Get detailed information about a specific shelter"""
    shelter = onto[shelter_name]
    if shelter and isinstance(shelter, onto.Shelter.__class__):
        capacity = shelter.capacity[0] if shelter.capacity else 0
        occupancy = shelter.currentOccupancy[0] if shelter.currentOccupancy else 0
        
        # Get volunteers assigned to this shelter
        volunteers = []
        for v in onto.Volunteer.instances():
            if v.assignedTo and v.assignedTo[0].name == shelter_name:
                volunteers.append({
                    "name": v.hasName[0] if v.hasName else v.name,
                    "skill_level": v.skillLevel[0] if v.skillLevel else "Unknown",
                    "contact": v.contactNumber[0] if v.contactNumber else "N/A"
                })
        
        shelter_data = {
            "id": shelter.name,
            "name": shelter.hasName[0] if shelter.hasName else shelter.name,
            "capacity": capacity,
            "current_occupancy": occupancy,
            "available_space": capacity - occupancy,
            "occupancy_rate": round((occupancy / capacity * 100), 1) if capacity > 0 else 0,
            "status": shelter.status[0] if shelter.status else "Unknown",
            "contact": shelter.contactNumber[0] if shelter.contactNumber else "N/A",
            "volunteers": volunteers
        }
        return jsonify(shelter_data)
    return jsonify({"error": "Shelter not found"}), 404

# ==================== VOLUNTEER ENDPOINTS ====================

@app.route("/volunteers")
def get_volunteers():
    """Get all volunteers"""
    data = []
    for v in onto.Volunteer.instances():
        volunteer_info = {
            "id": v.name,
            "name": v.hasName[0] if v.hasName else v.name,
            "assigned_shelter": v.assignedTo[0].hasName[0] if v.assignedTo and v.assignedTo[0].hasName else "Unassigned",
            "shelter_id": v.assignedTo[0].name if v.assignedTo else None,
            "skill_level": v.skillLevel[0] if v.skillLevel else "Unknown",
            "contact": v.contactNumber[0] if v.contactNumber else "N/A"
        }
        data.append(volunteer_info)
    return jsonify(data)

@app.route("/volunteers/shelter/<shelter_name>")
def get_volunteers_by_shelter(shelter_name):
    """Get volunteers assigned to a specific shelter"""
    data = []
    for v in onto.Volunteer.instances():
        if v.assignedTo and v.assignedTo[0].name == shelter_name:
            volunteer_info = {
                "name": v.hasName[0] if v.hasName else v.name,
                "skill_level": v.skillLevel[0] if v.skillLevel else "Unknown",
                "contact": v.contactNumber[0] if v.contactNumber else "N/A"
            }
            data.append(volunteer_info)
    return jsonify(data)

# ==================== RESOURCE ENDPOINTS ====================

@app.route("/resources")
def get_resources():
    """Get all resources"""
    data = []
    for r in onto.Resource.instances():
        resource_info = {
            "id": r.name,
            "name": r.hasName[0] if r.hasName else r.name,
            "type": r.__class__.__name__,
            "quantity": r.quantityAvailable[0] if r.quantityAvailable else 0
        }
        data.append(resource_info)
    return jsonify(data)

@app.route("/resources/low")
def get_low_resources():
    """Get resources with low stock (< 1000 units)"""
    data = []
    for r in onto.Resource.instances():
        quantity = r.quantityAvailable[0] if r.quantityAvailable else 0
        if quantity < 1000:
            resource_info = {
                "name": r.hasName[0] if r.hasName else r.name,
                "type": r.__class__.__name__,
                "quantity": quantity,
                "status": "Critical" if quantity < 500 else "Low"
            }
            data.append(resource_info)
    return jsonify(data)

# ==================== LOCATION ENDPOINTS ====================

@app.route("/locations")
def get_locations():
    """Get all locations"""
    data = []
    for loc in onto.Location.instances():
        location_info = {
            "id": loc.name,
            "name": loc.hasName[0] if loc.hasName else loc.name,
            "type": loc.__class__.__name__,
            "shelters": [s.hasName[0] if s.hasName else s.name for s in loc.hasShelter] if loc.hasShelter else []
        }
        data.append(location_info)
    return jsonify(data)

@app.route("/districts")
def get_districts():
    """Get all districts"""
    data = []
    for dist in onto.District.instances():
        # Count active disasters in this district
        active_disasters = 0
        for d in onto.Disaster.instances():
            if d.occursIn and d.occursIn[0].name == dist.name and d.status and d.status[0] == "Active":
                active_disasters += 1
        
        district_info = {
            "id": dist.name,
            "name": dist.hasName[0] if dist.hasName else dist.name,
            "province": dist.locatedIn[0].hasName[0] if dist.locatedIn and dist.locatedIn[0].hasName else "Unknown",
            "shelters_count": len(dist.hasShelter) if dist.hasShelter else 0,
            "active_disasters": active_disasters
        }
        data.append(district_info)
    return jsonify(data)

@app.route("/provinces")
def get_provinces():
    """Get all provinces"""
    data = []
    for prov in onto.Province.instances():
        province_info = {
            "id": prov.name,
            "name": prov.hasName[0] if prov.hasName else prov.name
        }
        data.append(province_info)
    return jsonify(data)

# ==================== ORGANIZATION ENDPOINTS ====================

@app.route("/organizations")
def get_organizations():
    """Get all organizations"""
    data = []
    for org in onto.Organization.instances():
        org_info = {
            "id": org.name,
            "name": org.hasName[0] if org.hasName else org.name,
            "contact": org.contactNumber[0] if org.contactNumber else "N/A"
        }
        data.append(org_info)
    return jsonify(data)

# ==================== STATISTICS ENDPOINTS ====================

@app.route("/statistics")
def get_statistics():
    """Get overall statistics"""
    stats = {
        "total_disasters": len(list(onto.Disaster.instances())),
        "active_disasters": len([d for d in onto.Disaster.instances() if d.status and d.status[0] == "Active"]),
        "total_shelters": len(list(onto.Shelter.instances())),
        "total_capacity": sum([s.capacity[0] if s.capacity else 0 for s in onto.Shelter.instances()]),
        "total_occupancy": sum([s.currentOccupancy[0] if s.currentOccupancy else 0 for s in onto.Shelter.instances()]),
        "total_volunteers": len(list(onto.Volunteer.instances())),
        "total_resources": len(list(onto.Resource.instances())),
        "total_districts": len(list(onto.District.instances())),
        "total_provinces": len(list(onto.Province.instances())),
        "disasters_by_type": {
            "Flood": len(list(onto.Flood.instances())),
            "Landslide": len(list(onto.Landslide.instances())),
            "Cyclone": len(list(onto.Cyclone.instances())),
            "Drought": len(list(onto.Drought.instances())),
            "Tsunami": len(list(onto.Tsunami.instances()))
        },
        "disasters_by_severity": {
            "High": len([d for d in onto.Disaster.instances() if d.severityLevel and d.severityLevel[0] == "High"]),
            "Medium": len([d for d in onto.Disaster.instances() if d.severityLevel and d.severityLevel[0] == "Medium"]),
            "Low": len([d for d in onto.Disaster.instances() if d.severityLevel and d.severityLevel[0] == "Low"])
        }
    }
    return jsonify(stats)

# ==================== POST ENDPOINTS (Add New Data) ====================

@app.route("/disasters/add", methods=["POST"])
def add_disaster():
    """Add a new disaster with dynamic type creation"""
    try:
        data = request.json
        disaster_name = data.get("name")
        disaster_type = data.get("type", "Flood")
        severity = data.get("severity", "Medium")
        location = data.get("location")
        date_occurred = data.get("date")
        create_new_type = data.get("create_new_type", False)
        
        with onto:
            # Handle dynamic type creation
            if create_new_type:
                # Check if class exists, if not create it
                if not getattr(onto, disaster_type, None):
                    NewClass = types.new_class(disaster_type, (onto.Disaster,))
            
            # Create disaster instance
            disaster_class = getattr(onto, disaster_type, onto.Flood)
            new_disaster = disaster_class(disaster_name.replace(" ", "_"))
            new_disaster.hasName = [disaster_name]
            new_disaster.severityLevel = [severity]
            new_disaster.status = ["Active"]
            
            if date_occurred:
                new_disaster.dateOccurred = [date_occurred]
            
            # Link to location
            if location:
                # Check if location needs creation (if passed as name and create_new_loc is True)
                # For now assume location ID is passed, or if special prefix indicating new
                loc = onto[location]
                if loc:
                    new_disaster.occursIn = [loc]
            
            # Save ontology
            onto.save(file=ONTOLOGY_PATH, format="rdfxml")
        
        return jsonify({"message": "Disaster added successfully", "id": new_disaster.name}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/volunteers/add", methods=["POST"])
def add_volunteer():
    """Add a new volunteer"""
    try:
        data = request.json
        name = data.get("name")
        contact = data.get("contact")
        skill = data.get("skill_level", "Basic")
        shelter_id = data.get("assigned_shelter")
        
        with onto:
            vol_id = f"Volunteer_{name.replace(' ', '_')}"
            new_vol = onto.Volunteer(vol_id)
            new_vol.hasName = [name]
            new_vol.contactNumber = [contact]
            new_vol.skillLevel = [skill]
            
            if shelter_id and shelter_id != "Unassigned":
                shelter = onto[shelter_id]
                if shelter:
                    new_vol.assignedTo = [shelter]
            
            onto.save(file=ONTOLOGY_PATH, format="rdfxml")
            
        return jsonify({"message": "Volunteer added successfully", "id": new_vol.name}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/resources/add", methods=["POST"])
def add_resource():
    """Add a new resource"""
    try:
        data = request.json
        name = data.get("name")
        res_type = data.get("type", "Resource") # WaterResource, FoodResource, etc.
        quantity = int(data.get("quantity", 0))
        
        with onto:
            res_class = getattr(onto, res_type, onto.Resource)
            res_id = f"Resource_{name.replace(' ', '_')}"
            new_res = res_class(res_id)
            new_res.hasName = [name]
            new_res.quantityAvailable = [quantity]
            
            onto.save(file=ONTOLOGY_PATH, format="rdfxml")
            
        return jsonify({"message": "Resource added successfully", "id": new_res.name}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/organizations/add", methods=["POST"])
def add_organization():
    """Add a new organization"""
    try:
        data = request.json
        name = data.get("name")
        contact = data.get("contact")
        
        with onto:
            org_id = f"Org_{name.replace(' ', '_')}"
            new_org = onto.Organization(org_id)
            new_org.hasName = [name]
            new_org.contactNumber = [contact]
            
            onto.save(file=ONTOLOGY_PATH, format="rdfxml")
            
        return jsonify({"message": "Organization added successfully", "id": new_org.name}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/locations/add", methods=["POST"])
def add_location():
    """Add a new location (District/Province) dynamically"""
    try:
        data = request.json
        name = data.get("name")
        loc_type = data.get("type", "District") # District or Province
        parent_id = data.get("parent_id")
        
        with onto:
            loc_class = getattr(onto, loc_type, onto.District)
            loc_id = name.replace(" ", "_")
            
            # Dynamic class creation check
            if not loc_class and data.get("create_new_type"):
                 loc_class = types.new_class(loc_type, (onto.Location,))
            
            new_loc = loc_class(loc_id)
            new_loc.hasName = [name]
            
            if parent_id:
                parent = onto[parent_id]
                if parent:
                    new_loc.locatedIn = [parent]
            
            onto.save(file=ONTOLOGY_PATH, format="rdfxml")
            
        return jsonify({"message": "Location added successfully", "id": new_loc.name}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)