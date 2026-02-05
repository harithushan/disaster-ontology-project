from rdflib import Graph

g = Graph()
g.parse("ontology/ontology.rdf", format="xml")

def run_sparql(query: str):
    results = []
    qres = g.query(query)
    for row in qres:
        results.append([str(col) for col in row])
    return results
