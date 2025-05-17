from flask import Flask, request, render_template
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, FOAF, DCTERMS
import os
from SPARQLWrapper import SPARQLWrapper, JSON

app = Flask(__name__)

# Configurar el namespace correcto (usando el de tu ontología)
ONTOLOGY_NS = Namespace("http://www.semanticweb.org/cabez/ontologies/2025/2/untitled-ontology-3#")

# Configurar SPARQL endpoint de DBpedia
DBPEDIA_SPARQL = "http://dbpedia.org/sparql"
sparql = SPARQLWrapper(DBPEDIA_SPARQL)
sparql.setReturnFormat(JSON)

# Cargar la ontología RDF
g = Graph()
try:
    g.parse("noticias_ontologia.rdf", format="xml")
    print(f"Ontología cargada correctamente con {len(g)} tripletas")
except Exception as e:
    print(f"Error al cargar la ontología: {e}")

def query_dbpedia(keyword):
    """Consulta DBpedia para información relacionada con la palabra clave"""
    query = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>
    
    SELECT DISTINCT ?resource ?label ?abstract ?thumbnail WHERE {
        ?resource rdfs:label ?label .
        FILTER(LANG(?label) = "en" || LANG(?label) = "es")
        FILTER(CONTAINS(LCASE(STR(?label)), "%s"))
        
        OPTIONAL { ?resource dbpedia-owl:abstract ?abstract .
                  FILTER(LANG(?abstract) = "en" || LANG(?abstract) = "es") }
        OPTIONAL { ?resource dbpedia-owl:thumbnail ?thumbnail }
        
        FILTER(STRSTARTS(STR(?resource), "http://dbpedia.org/resource/"))
    }
    LIMIT 5
    """ % keyword.lower()
    
    try:
        sparql.setQuery(query)
        results = sparql.query().convert()
        
        dbpedia_results = []
        for result in results["results"]["bindings"]:
            abstract = result.get("abstract", {}).get("value", "No description available")
            if len(abstract) > 200:
                abstract = abstract[:200] + "..."
                
            dbpedia_results.append({
                "uri": result["resource"]["value"],
                "label": result["label"]["value"],
                "abstract": abstract,
                "thumbnail": result.get("thumbnail", {}).get("value", "")
            })
        
        return dbpedia_results
    except Exception as e:
        print(f"Error al consultar DBpedia: {e}")
        return []

@app.route("/", methods=["GET", "POST"])
def search():
    local_results = []
    dbpedia_results = []
    keyword = ""
    
    if request.method == "POST":
        keyword = request.form.get("keyword", "").strip().lower()
        
        if keyword:
            # Consulta a la ontología local
            query = """
            PREFIX untitled-ontology-3: <http://www.semanticweb.org/cabez/ontologies/2025/2/untitled-ontology-3#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            
            SELECT DISTINCT ?noticia ?titulo ?fecha ?tematica ?autor ?estadoVerificacion
            WHERE {
                ?noticia rdf:type untitled-ontology-3:Noticia ;
                         untitled-ontology-3:Título ?titulo ;
                         untitled-ontology-3:Fecha_publicación ?fecha ;
                         untitled-ontology-3:Temática ?tematica ;
                         untitled-ontology-3:Autor ?autor .
                
                FILTER (
                    CONTAINS(LCASE(STR(?titulo)), "%s") || 
                    CONTAINS(LCASE(STR(?tematica)), "%s") || 
                    CONTAINS(LCASE(STR(?autor)), "%s")
                )
                
                OPTIONAL {
                    ?verificacion untitled-ontology-3:evalua ?noticia ;
                                  untitled-ontology-3:Estado ?estadoVerificacion .
                }
            }
            ORDER BY DESC(?fecha)
            """ % (keyword, keyword, keyword)
            
            try:
                query_results = g.query(query)
                local_results = []
                
                for row in query_results:
                    fecha = row.fecha.toPython().strftime("%Y-%m-%d") if hasattr(row.fecha, 'toPython') else str(row.fecha)
                    
                    local_results.append({
                        "uri": str(row.noticia),
                        "titulo": str(row.titulo),
                        "fecha": fecha,
                        "tematica": str(row.tematica),
                        "autor": str(row.autor),
                        "verificacion": str(row.estadoVerificacion) if row.estadoVerificacion else "No verificada"
                    })
                
            except Exception as e:
                print(f"Error en la consulta SPARQL local: {e}")
            
            # Consulta a DBpedia
            dbpedia_results = query_dbpedia(keyword)
    
    return render_template("search.html", 
                         local_results=local_results, 
                         dbpedia_results=dbpedia_results,
                         keyword=keyword)

@app.route("/noticia/<path:uri>")
def detalle_noticia(uri):
    detalles = {}
    
    # Determinar si es una URI local o de DBpedia
    if uri.startswith("http://www.semanticweb.org"):
        # Consulta local
        query = """
        PREFIX untitled-ontology-3: <http://www.semanticweb.org/cabez/ontologies/2025/2/untitled-ontology-3#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        
        SELECT ?propiedad ?valor
        WHERE {
            <%s> ?propiedad ?valor .
            FILTER (
                STRSTARTS(STR(?propiedad), "http://www.semanticweb.org/cabez/ontologies/2025/2/untitled-ontology-3#") ||
                ?propiedad IN (rdf:type, rdfs:label)
            )
        }
        """ % uri
        
        try:
            for row in g.query(query):
                prop_name = str(row.propiedad).split("#")[-1]
                detalles[prop_name] = str(row.valor)
        except Exception as e:
            print(f"Error al obtener detalles locales: {e}")
        
        return render_template("detalle.html", noticia=detalles, is_dbpedia=False)
    
    else:
        # Consulta a DBpedia
        query = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        
        SELECT ?property ?value WHERE {
            <%s> ?property ?value .
            FILTER(
                STRSTARTS(STR(?property), "http://dbpedia.org/ontology/") ||
                STRSTARTS(STR(?property), "http://www.w3.org/2000/01/rdf-schema#") ||
                ?property IN (foaf:depiction, foaf:isPrimaryTopicOf)
            )
        }
        """ % uri
        
        try:
            sparql.setQuery(query)
            results = sparql.query().convert()
            
            for result in results["results"]["bindings"]:
                prop_uri = result["property"]["value"]
                if "ontology/" in prop_uri:
                    prop_name = prop_uri.split("ontology/")[-1]
                elif "foaf/" in prop_uri:
                    prop_name = prop_uri.split("foaf/")[-1]
                else:
                    prop_name = prop_uri.split("#")[-1]
                
                detalles[prop_name] = result["value"]["value"]
            
            # Obtener la página wiki relacionada
            wiki_page = uri.replace("http://dbpedia.org/resource/", "https://es.wikipedia.org/wiki/")
            detalles["wikipedia_page"] = wiki_page
            
        except Exception as e:
            print(f"Error al obtener detalles de DBpedia: {e}")
        
        return render_template("detalle.html", noticia=detalles, is_dbpedia=True)

if __name__ == "__main__":
    app.run(debug=True)