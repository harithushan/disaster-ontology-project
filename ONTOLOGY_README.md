# 🇱🇰 Sri Lanka Disaster Management Ontology Guide

## 📖 Overview
This project utilizes a **semantic web ontology (OWL)** to model and manage disaster-related data for Sri Lanka. Unlike a traditional relational database, this ontology captures **relationships**, **hierarchies**, and **inferred knowledge** about disasters, resources, locations, and response efforts.

## 🎯 Use Cases
1.  **Dynamic Disaster Tracking**: Classifying and querying disasters (Floods, Landslides, etc.) along with their severity and status.
2.  **Resource Allocation**: Identifying which resources (Food, Water, Medical) are required for specific disasters and checking their availability.
3.  **Volunteer Coordination**: Managing volunteers based on their skill levels and assigning them to appropriate shelters.
4.  **Location-Based Analysis**: Understanding the hierarchical relationship between Provinces and Districts to aggregate disaster impact.
5.  **Smart Reasoning**: Using inference to automatically link related entities (e.g., inferring that a "Flood" in "Colombo" requires "WaterRescue" resources).

---

## 🏗️ Ontology Structure

### 1. Class Hierarchy
The core backbone of the ontology. Classes represent the "types" of things that exist.

*   **Disaster** (Base Class)
    *   `Flood`
    *   `Landslide`
    *   `Cyclone`
    *   `Drought`
    *   `Tsunami`
    *   *(Dynamic classes can be added via the UI)*
*   **Location**
    *   `Province` (e.g., Western Province)
    *   `District` (e.g., Colombo, Gampaha)
*   **Resource**
    *   `FoodResource`
    *   `MedicalResource`
    *   `WaterResource`
    *   `ClothingResource`
*   **Party / Agent**
    *   `Organization` (e.g., Red Cross, DMC)
    *   `Volunteer`
    *   `AffectedPopulation`
*   **Infrastructure**
    *   `Shelter`

### 2. Object Properties
These define relationships **between** two instances (e.g., "Flood A" *occurs in* "Colombo").

| Property | Domain (Subject) | Range (Object) | Description |
| :--- | :--- | :--- | :--- |
| **occursIn** | `Disaster` | `Location` | Defines where a disaster is happening. |
| **locatedIn** | `District` | `Province` | Hierarchical link (District belongs to Province). |
| **requiresResource** | `Disaster` | `Resource` | Links a disaster to the supplies needed. |
| **hasShelter** | `Location` | `Shelter` | Links a location to available shelters. |
| **assignedTo** | `Volunteer` | `Shelter` | Tracks where a volunteer is working. |
| **managedBy** | `Shelter` | `Organization` | (Optional) Organization running the shelter. |
| **affects** | `Disaster` | `AffectedPopulation`| Links disaster to the people affected. |

### 3. Data Properties
These store specific **values** (strings, numbers, dates) for an instance.

| Property | Applies To | Data Type | Description |
| :--- | :--- | :--- | :--- |
| **hasName** | *All Classes* | `string` | The human-readable name of the entity. |
| **severityLevel** | `Disaster` | `string` | Low, Medium, High. |
| **status** | `Disaster` | `string` | Active, Monitoring, Resolved. |
| **dateOccurred** | `Disaster` | `date/string`| When the event started. |
| **capacity** | `Shelter` | `int` | Max number of people a shelter can hold. |
| **currentOccupancy**| `Shelter` | `int` | Current number of people in the shelter. |
| **contactNumber** | `Volunteer`, `Org` | `string` | Phone number/Contact info. |
| **skillLevel** | `Volunteer` | `string` | Basic, Advanced, Medical, etc. |
| **quantityAvailable**| `Resource` | `int` | Stock count of the resource. |

---

## 🛠️ Technical Implementation

### Key Technologies
*   **Owlready2 (Python)**: Used to load, query, and modify the ontology programmatically.
*   **RDF/XML**: The file format used to save the ontology (`ontology.rdf`).
*   **SPARQL**: Used for complex querying (filtering by date, severity, etc.).

### Example SPARQL Query
*Find all Active High-Severity Disasters:*
```sparql
PREFIX exc: <http://example.org/disaster.owl#>
SELECT ?disaster ?name ?loc
WHERE {
  ?disaster rdf:type/rdfs:subClassOf* exc:Disaster .
  ?disaster exc:severityLevel "High" .
  ?disaster exc:status "Active" .
  ?disaster exc:hasName ?name .
  ?disaster exc:occursIn ?locObj .
  ?locObj exc:hasName ?loc .
}
```

## 🚀 How to Add New Knowledge
You can extend the ontology directly through the **Add Data** tab in the application:
1.  **Dynamic Types**: You can invent new Disaster Types (e.g., "MeteorImpact") and the system will create the class structure for you.
2.  **New Locations**: Add new districts or provinces as needed.
3.  **Entities**: Instantly create new Volunteers, Resources, and Organizations.
