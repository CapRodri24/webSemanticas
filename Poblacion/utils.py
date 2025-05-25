from rdflib import URIRef
import datetime

def generar_uri(base_uri, tipo_entidad):
    """Genera un URI único para una nueva entidad"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    return URIRef(f"{base_uri}/{tipo_entidad}_{timestamp}")

def mostrar_noticias_disponibles(g):
    """Muestra las noticias disponibles para verificar"""
    query = """
    PREFIX untitled-ontology-3: <http://www.semanticweb.org/cabez/ontologies/2025/2/untitled-ontology-3#>
    SELECT ?noticia ?titulo
    WHERE {
        ?noticia a untitled-ontology-3:Noticia ;
                 untitled-ontology-3:Título ?titulo .
    }
    ORDER BY ?titulo
    """
    resultados = g.query(query)
    for i, row in enumerate(resultados, 1):
        print(f"{i}. {row.titulo}")
    return resultados

def guardar_ontologia(g, archivo="noticias_ontologia.rdf"):
    """Guarda la ontología en un archivo"""
    g.serialize(destination=archivo, format="xml")
    print(f"Ontología guardada en {archivo}")