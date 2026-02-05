from owlready2 import *

onto = get_ontology("ontology/ontology.rdf").load()

def add_disaster(name, dtype, severity, location, resources):
    with onto:
        if dtype == "Flood":
            d = onto.Flood(name)
        else:
            d = onto.Landslide(name)

        d.severityLevel = [severity]

        loc = onto[location]
        d.occursIn = [loc]

        for r in resources:
            d.requiresResource.append(onto[r])

    onto.save(file="ontology/ontology.rdf", format="rdfxml")
