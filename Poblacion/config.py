from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, XSD

# Configuración de namespaces
ONTOLOGY_NS = Namespace("http://www.semanticweb.org/cabez/ontologies/2025/2/untitled-ontology-3#")
BASE_URI = "http://www.semanticweb.org/cabez/ontologies/2025/2/untitled-ontology-3"

# Inicializar grafo RDF
g = Graph()
g.parse("noticias_ontologia.rdf", format="xml")