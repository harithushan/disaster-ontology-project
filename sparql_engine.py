from rdflib import Graph, Namespace
from rdflib.plugins.sparql import prepareQuery

class SPARQLEngine:
    def __init__(self, ontology_path="ontology/disaster_ontology.rdf"):
        self.graph = Graph()
        self.graph.parse(ontology_path, format="xml")
        
        # Define namespaces
        self.d = Namespace("http://www.srilanka.gov/disaster.owl#")
        self.owl = Namespace("http://www.w3.org/2002/07/owl#")
        self.rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        self.rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
        
    def run_query(self, query_string):
        """Execute a SPARQL query and return results"""
        try:
            results = []
            qres = self.graph.query(query_string)
            
            # Get column headers
            if qres.vars:
                headers = [str(var) for var in qres.vars]
                results.append(headers)
            
            # Get data rows
            for row in qres:
                results.append([self._format_value(col) for col in row])
            
            return {
                "success": True,
                "results": results,
                "count": len(results) - 1 if results else 0  # Subtract header row
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "results": []
            }
    
    def _format_value(self, value):
        """Format RDF values for display"""
        if value is None:
            return "N/A"
        value_str = str(value)
        # Remove namespace prefixes for cleaner display
        if "#" in value_str:
            return value_str.split("#")[-1]
        return value_str
    
    # Predefined queries
    PREDEFINED_QUERIES = {
        "all_disasters": {
            "name": "All Disasters",
            "description": "List all disasters with their severity and location",
            "query": """
PREFIX d: <http://www.srilanka.gov/disaster.owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?disaster ?name ?severity ?location
WHERE {
  ?disaster rdf:type/rdfs:subClassOf* d:Disaster .
  OPTIONAL { ?disaster d:hasName ?name }
  OPTIONAL { ?disaster d:severityLevel ?severity }
  OPTIONAL { ?disaster d:occursIn ?loc .
             ?loc d:hasName ?location }
}
ORDER BY ?severity
"""
        },
        
        "high_severity": {
            "name": "High Severity Disasters",
            "description": "Find all high severity disasters",
            "query": """
PREFIX d: <http://www.srilanka.gov/disaster.owl#>

SELECT ?disaster ?name ?type ?location ?date
WHERE {
  ?disaster rdf:type ?type .
  ?type rdfs:subClassOf d:Disaster .
  ?disaster d:severityLevel "High" .
  OPTIONAL { ?disaster d:hasName ?name }
  OPTIONAL { ?disaster d:occursIn ?loc .
             ?loc d:hasName ?location }
  OPTIONAL { ?disaster d:dateOccurred ?date }
}
ORDER BY DESC(?date)
"""
        },
        
        "active_disasters": {
            "name": "Active Disasters",
            "description": "List all currently active disasters",
            "query": """
PREFIX d: <http://www.srilanka.gov/disaster.owl#>

SELECT ?disaster ?name ?severity ?location
WHERE {
  ?disaster rdf:type/rdfs:subClassOf* d:Disaster .
  ?disaster d:status "Active" .
  OPTIONAL { ?disaster d:hasName ?name }
  OPTIONAL { ?disaster d:severityLevel ?severity }
  OPTIONAL { ?disaster d:occursIn ?loc .
             ?loc d:hasName ?location }
}
"""
        },
        
        "shelter_capacity": {
            "name": "Shelter Capacity Analysis",
            "description": "Show shelters with their capacity and occupancy",
            "query": """
PREFIX d: <http://www.srilanka.gov/disaster.owl#>

SELECT ?shelter ?name ?capacity ?occupancy (?capacity - ?occupancy AS ?available)
WHERE {
  ?shelter rdf:type d:Shelter .
  OPTIONAL { ?shelter d:hasName ?name }
  OPTIONAL { ?shelter d:capacity ?capacity }
  OPTIONAL { ?shelter d:currentOccupancy ?occupancy }
}
ORDER BY DESC(?available)
"""
        },
        
        "available_shelters": {
            "name": "Available Shelters",
            "description": "Shelters with available space",
            "query": """
PREFIX d: <http://www.srilanka.gov/disaster.owl#>

SELECT ?shelter ?name ?capacity ?occupancy (?capacity - ?occupancy AS ?available) ?status
WHERE {
  ?shelter rdf:type d:Shelter .
  ?shelter d:capacity ?capacity .
  ?shelter d:currentOccupancy ?occupancy .
  FILTER(?capacity > ?occupancy)
  OPTIONAL { ?shelter d:hasName ?name }
  OPTIONAL { ?shelter d:status ?status }
}
ORDER BY DESC(?available)
"""
        },
        
        "floods_only": {
            "name": "All Floods",
            "description": "List only flood disasters",
            "query": """
PREFIX d: <http://www.srilanka.gov/disaster.owl#>

SELECT ?flood ?name ?severity ?location ?date
WHERE {
  ?flood rdf:type d:Flood .
  OPTIONAL { ?flood d:hasName ?name }
  OPTIONAL { ?flood d:severityLevel ?severity }
  OPTIONAL { ?flood d:occursIn ?loc .
             ?loc d:hasName ?location }
  OPTIONAL { ?flood d:dateOccurred ?date }
}
ORDER BY DESC(?date)
"""
        },
        
        "landslides_only": {
            "name": "All Landslides",
            "description": "List only landslide disasters",
            "query": """
PREFIX d: <http://www.srilanka.gov/disaster.owl#>

SELECT ?landslide ?name ?severity ?location ?date
WHERE {
  ?landslide rdf:type d:Landslide .
  OPTIONAL { ?landslide d:hasName ?name }
  OPTIONAL { ?landslide d:severityLevel ?severity }
  OPTIONAL { ?landslide d:occursIn ?loc .
             ?loc d:hasName ?location }
  OPTIONAL { ?landslide d:dateOccurred ?date }
}
ORDER BY DESC(?date)
"""
        },
        
        "disaster_resources": {
            "name": "Disaster Resources Required",
            "description": "Show disasters and their required resources",
            "query": """
PREFIX d: <http://www.srilanka.gov/disaster.owl#>

SELECT ?disaster ?disasterName ?resource ?resourceName
WHERE {
  ?disaster rdf:type/rdfs:subClassOf* d:Disaster .
  ?disaster d:requiresResource ?resource .
  OPTIONAL { ?disaster d:hasName ?disasterName }
  OPTIONAL { ?resource d:hasName ?resourceName }
}
ORDER BY ?disaster
"""
        },
        
        "volunteers_assignments": {
            "name": "Volunteer Assignments",
            "description": "List volunteers and their shelter assignments",
            "query": """
PREFIX d: <http://www.srilanka.gov/disaster.owl#>

SELECT ?volunteer ?volName ?shelter ?shelterName ?skillLevel
WHERE {
  ?volunteer rdf:type d:Volunteer .
  ?volunteer d:assignedTo ?shelter .
  OPTIONAL { ?volunteer d:hasName ?volName }
  OPTIONAL { ?volunteer d:skillLevel ?skillLevel }
  OPTIONAL { ?shelter d:hasName ?shelterName }
}
ORDER BY ?shelter
"""
        },
        
        "resource_inventory": {
            "name": "Resource Inventory",
            "description": "Show all resources and their quantities",
            "query": """
PREFIX d: <http://www.srilanka.gov/disaster.owl#>

SELECT ?resource ?name ?type ?quantity
WHERE {
  ?resource rdf:type ?type .
  ?type rdfs:subClassOf* d:Resource .
  OPTIONAL { ?resource d:hasName ?name }
  OPTIONAL { ?resource d:quantityAvailable ?quantity }
}
ORDER BY ?quantity
"""
        },
        
        "district_disasters": {
            "name": "Disasters by District",
            "description": "Count disasters per district",
            "query": """
PREFIX d: <http://www.srilanka.gov/disaster.owl#>

SELECT ?district ?districtName (COUNT(?disaster) AS ?disasterCount)
WHERE {
  ?district rdf:type d:District .
  OPTIONAL { ?district d:hasName ?districtName }
  OPTIONAL { ?disaster d:occursIn ?district }
}
GROUP BY ?district ?districtName
ORDER BY DESC(?disasterCount)
"""
        },
        
        "full_shelter_info": {
            "name": "Complete Shelter Information",
            "description": "Detailed shelter information including contact",
            "query": """
PREFIX d: <http://www.srilanka.gov/disaster.owl#>

SELECT ?shelter ?name ?capacity ?occupancy ?status ?contact
WHERE {
  ?shelter rdf:type d:Shelter .
  OPTIONAL { ?shelter d:hasName ?name }
  OPTIONAL { ?shelter d:capacity ?capacity }
  OPTIONAL { ?shelter d:currentOccupancy ?occupancy }
  OPTIONAL { ?shelter d:status ?status }
  OPTIONAL { ?shelter d:contactNumber ?contact }
}
ORDER BY ?name
"""
        },
        
        "disasters_2024": {
            "name": "Disasters in 2024",
            "description": "All disasters that occurred in 2024",
            "query": """
PREFIX d: <http://www.srilanka.gov/disaster.owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?disaster ?name ?type ?severity ?date
WHERE {
  ?disaster rdf:type ?type .
  ?type rdfs:subClassOf d:Disaster .
  ?disaster d:dateOccurred ?date .
  FILTER(YEAR(?date) = 2024)
  OPTIONAL { ?disaster d:hasName ?name }
  OPTIONAL { ?disaster d:severityLevel ?severity }
}
ORDER BY ?date
"""
        },
        
        "critical_resources": {
            "name": "Critical Resource Levels",
            "description": "Resources with quantity less than 1000",
            "query": """
PREFIX d: <http://www.srilanka.gov/disaster.owl#>

SELECT ?resource ?name ?quantity
WHERE {
  ?resource rdf:type/rdfs:subClassOf* d:Resource .
  ?resource d:quantityAvailable ?quantity .
  FILTER(?quantity < 1000)
  OPTIONAL { ?resource d:hasName ?name }
}
ORDER BY ?quantity
"""
        },
        
        "central_province_disasters": {
            "name": "Central Province Disasters",
            "description": "Disasters in Central Province districts",
            "query": """
PREFIX d: <http://www.srilanka.gov/disaster.owl#>

SELECT ?disaster ?disasterName ?district ?districtName ?severity
WHERE {
  ?disaster d:occursIn ?district .
  ?district d:locatedIn d:CentralProvince .
  OPTIONAL { ?disaster d:hasName ?disasterName }
  OPTIONAL { ?district d:hasName ?districtName }
  OPTIONAL { ?disaster d:severityLevel ?severity }
}
"""
        },
        
        "advanced_volunteers": {
            "name": "Advanced Skill Volunteers",
            "description": "Volunteers with advanced skills",
            "query": """
PREFIX d: <http://www.srilanka.gov/disaster.owl#>

SELECT ?volunteer ?name ?shelter ?shelterName ?contact
WHERE {
  ?volunteer rdf:type d:Volunteer .
  ?volunteer d:skillLevel "Advanced" .
  OPTIONAL { ?volunteer d:hasName ?name }
  OPTIONAL { ?volunteer d:assignedTo ?shelter .
             ?shelter d:hasName ?shelterName }
  OPTIONAL { ?volunteer d:contactNumber ?contact }
}
"""
        }
    }
    
    def get_predefined_queries(self):
        """Return list of predefined queries"""
        return [
            {
                "id": key,
                "name": value["name"],
                "description": value["description"]
            }
            for key, value in self.PREDEFINED_QUERIES.items()
        ]
    
    def run_predefined_query(self, query_id):
        """Run a predefined query by ID"""
        if query_id in self.PREDEFINED_QUERIES:
            query_string = self.PREDEFINED_QUERIES[query_id]["query"]
            return self.run_query(query_string)
        else:
            return {
                "success": False,
                "error": "Query not found",
                "results": []
            }

# For direct usage
def run_sparql(query: str):
    """Wrapper function for backward compatibility"""
    engine = SPARQLEngine("ontology/disaster_ontology.rdf")
    result = engine.run_query(query)
    return result["results"]