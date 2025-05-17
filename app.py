from flask import Flask, request, render_template
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, RDFS
import os

app = Flask(__name__)

# Configurar el namespace correcto (usando el de tu ontología)
ONTOLOGY_NS = Namespace("http://www.semanticweb.org/cabez/ontologies/2025/2/untitled-ontology-3#")

# Cargar la ontología RDF
g = Graph()
try:
    g.parse("noticias_ontologia.rdf", format="xml")
    print(f"Ontología cargada correctamente con {len(g)} tripletas")
except Exception as e:
    print(f"Error al cargar la ontología: {e}")

@app.route("/", methods=["GET", "POST"])
def search():
    results = []
    keyword = ""
    
    if request.method == "POST":
        keyword = request.form.get("keyword", "").strip().lower()
        
        if keyword:
            # Consulta SPARQL mejorada
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
                
                # Búsqueda en múltiples campos
                FILTER (
                    CONTAINS(LCASE(STR(?titulo)), "%s") || 
                    CONTAINS(LCASE(STR(?tematica)), "%s") || 
                    CONTAINS(LCASE(STR(?autor)), "%s")
                )
                
                # Información de verificación (opcional)
                OPTIONAL {
                    ?verificacion untitled-ontology-3:evalua ?noticia ;
                                  untitled-ontology-3:Estado ?estadoVerificacion .
                }
            }
            ORDER BY DESC(?fecha)
            """ % (keyword, keyword, keyword)
            
            try:
                query_results = g.query(query)
                results = []
                
                for row in query_results:
                    # Formatear la fecha para mejor visualización
                    fecha = row.fecha.toPython().strftime("%Y-%m-%d") if hasattr(row.fecha, 'toPython') else str(row.fecha)
                    
                    results.append({
                        "uri": str(row.noticia),
                        "titulo": str(row.titulo),
                        "fecha": fecha,
                        "tematica": str(row.tematica),
                        "autor": str(row.autor),
                        "verificacion": str(row.estadoVerificacion) if row.estadoVerificacion else "No verificada"
                    })
                
            except Exception as e:
                print(f"Error en la consulta SPARQL: {e}")
    
    return render_template("search.html", results=results, keyword=keyword)

@app.route("/noticia/<path:uri>")
def detalle_noticia(uri):
    # Consulta para obtener todos los detalles de una noticia específica
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
    
    detalles = {}
    try:
        for row in g.query(query):
            prop_name = str(row.propiedad).split("#")[-1]
            detalles[prop_name] = str(row.valor)
    except Exception as e:
        print(f"Error al obtener detalles: {e}")
    
    return render_template("detalle.html", noticia=detalles)

if __name__ == "__main__":
    app.run(debug=True)