from flask import Flask, request, render_template, jsonify
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, OWL, XSD
from SPARQLWrapper import SPARQLWrapper, JSON
import os
from datetime import datetime
import json
from googletrans import Translator
import urllib.parse

app = Flask(__name__)
translator = Translator()

# Configurar namespaces
ONTOLOGY_NS = Namespace("http://www.semanticweb.org/cabez/ontologies/2025/2/untitled-ontology-3#")
DBPEDIA_NS = Namespace("http://dbpedia.org/resource/")
DBPEDIA_ONTOLOGY_NS = Namespace("http://dbpedia.org/ontology/")

# Cargar la ontología
g = Graph()
try:
    if os.path.exists("noticias_ontologia.rdf"):
        g.parse("noticias_ontologia.rdf", format="xml")
    elif os.path.exists("noticias_ontologia.owl"):
        g.parse("noticias_ontologia.owl", format="xml")
    print(f"Ontología cargada correctamente con {len(g)} tripletas")
except Exception as e:
    print(f"Error al cargar la ontología: {e}")

# Configuración de idiomas
LANGUAGES = {
    'es': 'Español',
    'en': 'English',
    'pt': 'Português'
}

# Traducciones completas
TRANSLATIONS = {
    'search_placeholder': {
        'es': 'Buscar noticias...',
        'en': 'Search news...',
        'pt': 'Pesquisar notícias...'
    },
    'search_button': {
        'es': 'Buscar',
        'en': 'Search',
        'pt': 'Pesquisar'
    },
    'title': {
        'es': 'Buscador de Noticias',
        'en': 'News Search',
        'pt': 'Pesquisa de Notícias'
    },
    'no_results': {
        'es': 'No se encontraron noticias para',
        'en': 'No news found for',
        'pt': 'Nenhuma notícia encontrada para'
    },
    'results_for': {
        'es': 'Resultados para',
        'en': 'Results for',
        'pt': 'Resultados para'
    },
    'date': {
        'es': 'Fecha',
        'en': 'Date',
        'pt': 'Data'
    },
    'topic': {
        'es': 'Tema',
        'en': 'Topic',
        'pt': 'Tema'
    },
    'author': {
        'es': 'Autor',
        'en': 'Author',
        'pt': 'Autor'
    },
    'verification': {
        'es': 'Verificación',
        'en': 'Verification',
        'pt': 'Verificação'
    },
    'not_verified': {
        'es': 'No verificada',
        'en': 'Not verified',
        'pt': 'Não verificada'
    },
    'view_details': {
        'es': 'Ver detalles',
        'en': 'View details',
        'pt': 'Ver detalhes'
    },
    'view_on_dbpedia': {
        'es': 'Ver en DBpedia',
        'en': 'View on DBpedia',
        'pt': 'Ver no DBpedia'
    },
    'local_results': {
        'es': 'Resultados Locales',
        'en': 'Local Results',
        'pt': 'Resultados Locais'
    },
    'dbpedia_results': {
        'es': 'Resultados de DBpedia',
        'en': 'DBpedia Results',
        'pt': 'Resultados do DBpedia'
    },
    'inferred_results': {
        'es': 'Resultados Inferidos',
        'en': 'Inferred Results',
        'pt': 'Resultados Inferidos'
    },
    'back': {
        'es': '← Volver',
        'en': '← Back',
        'pt': '← Voltar'
    },
    'news_details': {
        'es': 'Detalle de la Noticia',
        'en': 'News Details',
        'pt': 'Detalhes da Notícia'
    },
    'dark_mode': {
        'es': 'Modo Oscuro',
        'en': 'Dark Mode',
        'pt': 'Modo Escuro'
    },
    'light_mode': {
        'es': 'Modo Claro',
        'en': 'Light Mode',
        'pt': 'Modo Claro'
    },
    'translated_from': {
        'es': 'Traducido del',
        'en': 'Translated from',
        'pt': 'Traduzido do'
    },
    'no_dbpedida_results': {
        'es': 'No se encontraron resultados en DBpedia',
        'en': 'No results found in DBpedia',
        'pt': 'Nenhum resultado encontrado no DBpedia'
    },
    'possible_properties': {
        'es': 'Propiedades posibles',
        'en': 'Possible properties',
        'pt': 'Propriedades possíveis'
    },
    'existing_properties': {
        'es': 'Propiedades existentes',
        'en': 'Existing properties',
        'pt': 'Propriedades existentes'
    },
    'inferred_classes': {
        'es': 'Clases inferidas',
        'en': 'Inferred classes',
        'pt': 'Classes inferidas'
    },
    'type': {
        'es': 'Tipo',
        'en': 'Type',
        'pt': 'Tipo'
    },
    'value': {
        'es': 'Valor',
        'en': 'Value',
        'pt': 'Valor'
    }
}

def translate_text(text, src_lang, dest_lang):
    """Traduce texto entre idiomas usando Google Translate"""
    try:
        if src_lang == dest_lang or not text or text.strip() == "?":
            return text
        translation = translator.translate(text, src=src_lang, dest=dest_lang)
        return translation.text
    except Exception as e:
        print(f"Error translating text: {e}")
        return text

def query_dbpedia(search_term, lang='en'):
    """Consulta DBpedia para obtener noticias relacionadas con manejo robusto de errores"""
    try:
        sparql = SPARQLWrapper("http://dbpedia.org/sparql")
        sparql.setTimeout(30)  # Aumentar tiempo de espera
        
        # Consulta más flexible que busca en múltiples campos y tipos de recursos
        query = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX dbp: <http://dbpedia.org/property/>
        
        SELECT DISTINCT ?resource ?label ?abstract ?date ?author ?thumbnail
        WHERE {
            {
                ?resource a dbo:News ;
                          rdfs:label ?label ;
                          dbo:abstract ?abstract .
                FILTER (LANG(?label) = "%s" && LANG(?abstract) = "%s")
                FILTER (CONTAINS(LCASE(?label), LCASE("%s")))
            }
            UNION
            {
                ?resource a dbo:Event ;
                          rdfs:label ?label ;
                          dbo:abstract ?abstract .
                FILTER (LANG(?label) = "%s" && LANG(?abstract) = "%s")
                FILTER (CONTAINS(LCASE(?label), LCASE("%s")))
            }
            
            OPTIONAL { ?resource dbp:date ?date . }
            OPTIONAL { ?resource dbp:author ?author . }
            OPTIONAL { ?resource dbo:thumbnail ?thumbnail . }
        }
        LIMIT 10
        """ % (lang, lang, search_term, lang, lang, search_term)
        
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        
        # Procesar resultados
        formatted_results = []
        for result in results["results"]["bindings"]:
            formatted = {
                "resource": result["resource"]["value"],
                "label": result["label"]["value"],
                "abstract": result["abstract"]["value"]
            }
            
            if "date" in result:
                formatted["date"] = result["date"]["value"]
            if "author" in result:
                formatted["author"] = result["author"]["value"]
            if "thumbnail" in result:
                formatted["thumbnail"] = result["thumbnail"]["value"]
                
            formatted_results.append(formatted)
        
        return formatted_results
        
    except Exception as e:
        print(f"Error en consulta a DBpedia: {str(e)}")
        return []

def infer_properties(subject):
    """Realiza inferencias sobre un sujeto en la ontología con manejo robusto"""
    inferred = {}
    
    try:
        # Obtener todas las clases del sujeto (incluyendo superclases)
        classes = set()
        for s, p, o in g.triples((subject, RDF.type, None)):
            classes.add(o)
            # Obtener superclases
            for s2, p2, o2 in g.triples((o, RDFS.subClassOf, None)):
                classes.add(o2)
        
        inferred['classes'] = [str(c).split("#")[-1] for c in classes if "#" in str(c)]
        
        # Inferir propiedades basadas en las clases
        properties = set()
        for class_uri in classes:
            for s, p, o in g.triples((class_uri, RDFS.domain, None)):
                properties.add(p)
            for s, p, o in g.triples((None, RDFS.domain, class_uri)):
                properties.add(p)
        
        inferred['possible_properties'] = [str(p).split("#")[-1] for p in properties if "#" in str(p)]
        
        # Obtener propiedades existentes
        existing_props = []
        for s, p, o in g.triples((subject, None, None)):
            prop_name = str(p).split("#")[-1] if "#" in str(p) else str(p)
            prop_value = str(o)
            
            # Manejar diferentes tipos de valores
            if isinstance(o, Literal):
                if o.datatype == XSD.dateTime:
                    try:
                        prop_value = o.toPython().strftime("%Y-%m-%d")
                    except:
                        prop_value = str(o)
                else:
                    prop_value = str(o)
            
            existing_props.append({
                'property': prop_name,
                'value': prop_value,
                'type': 'literal' if isinstance(o, Literal) else 'resource'
            })
        
        inferred['existing_properties'] = existing_props
        
    except Exception as e:
        print(f"Error en inferencia de propiedades: {str(e)}")
        inferred['error'] = str(e)
    
    return inferred

@app.route("/", methods=["GET", "POST"])
def search():
    lang = request.args.get('lang', 'es')
    dark_mode = request.cookies.get('dark_mode', 'true') == 'true'
    
    local_results = []
    dbpedia_results = []
    inferred_results = []
    keyword = ""
    
    if request.method == "POST":
        keyword = request.form.get("keyword", "").strip()
        lang = request.form.get("lang", lang)
        
        if keyword:
            # Consulta SPARQL para resultados locales
            query = """
            PREFIX untitled-ontology-3: <http://www.semanticweb.org/cabez/ontologies/2025/2/untitled-ontology-3#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            
            SELECT DISTINCT ?noticia ?titulo ?fecha ?tematica ?autor ?estadoVerificacion ?enlaceDBpedia
            WHERE {
                ?noticia rdf:type ?tipoNoticia .
                ?tipoNoticia rdfs:subClassOf* untitled-ontology-3:Noticia .

                OPTIONAL { ?noticia untitled-ontology-3:Título ?titulo . }
                OPTIONAL { ?noticia untitled-ontology-3:Fecha_publicación ?fecha . }
                OPTIONAL { ?noticia untitled-ontology-3:Temática ?tematica . }
                OPTIONAL { ?noticia untitled-ontology-3:Autor ?autor . }
                OPTIONAL { ?noticia untitled-ontology-3:EnlaceDBpedia ?enlaceDBpedia . }
                
                FILTER (
                    CONTAINS(LCASE(STR(?titulo)), LCASE("%s")) || 
                    CONTAINS(LCASE(STR(?tematica)), LCASE("%s")) || 
                    CONTAINS(LCASE(STR(?autor)), LCASE("%s"))
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
                    # Formatear la fecha
                    fecha = row.fecha.toPython().strftime("%Y-%m-%d") if row.fecha and hasattr(row.fecha, 'toPython') else str(row.fecha) if row.fecha else "?"
                    
                    # Traducir contenido si es necesario
                    titulo = translate_text(str(row.titulo), 'es', lang) if row.titulo else "Sin título"
                    tematica = translate_text(str(row.tematica), 'es', lang) if row.tematica else "?"
                    autor = translate_text(str(row.autor), 'es', lang) if row.autor else "?"
                    
                    local_results.append({
                        "uri": str(row.noticia),
                        "titulo": titulo,
                        "fecha": fecha,
                        "tematica": tematica,
                        "autor": autor,
                        "verificacion": str(row.estadoVerificacion) if row.estadoVerificacion else TRANSLATIONS['not_verified'][lang],
                        "enlaceDBpedia": str(row.enlaceDBpedia) if row.enlaceDBpedia else None,
                        "original_lang": "es"
                    })
                    
                    # Realizar inferencias
                    try:
                        inferred = infer_properties(URIRef(row.noticia))
                        if inferred:
                            inferred_results.append({
                                "uri": str(row.noticia),
                                "titulo": titulo,
                                "inferred": inferred
                            })
                    except Exception as e:
                        print(f"Error en inferencia para {row.noticia}: {str(e)}")
                
            except Exception as e:
                print(f"Error en la consulta SPARQL local: {str(e)}")
            
            # Consultar DBpedia con manejo de errores
            try:
                dbpedia_results = query_dbpedia(keyword, lang)
            except Exception as e:
                print(f"Error al consultar DBpedia: {str(e)}")
                dbpedia_results = []
    
    return render_template(
        "search.html",
        local_results=local_results,
        dbpedia_results=dbpedia_results,
        inferred_results=inferred_results,
        keyword=keyword,
        languages=LANGUAGES,
        current_lang=lang,
        translations=TRANSLATIONS,
        dark_mode=dark_mode
    )

@app.route("/noticia/<path:uri>")
def detalle_noticia(uri):
    lang = request.args.get('lang', 'es')
    dark_mode = request.cookies.get('dark_mode', 'true') == 'true'
    
    # Decodificar URI (maneja caracteres especiales)
    try:
        uri_decoded = urllib.parse.unquote(uri)
    except:
        uri_decoded = uri
    
    # Consulta para obtener todos los detalles de una noticia específica
    query = """
    PREFIX untitled-ontology-3: <http://www.semanticweb.org/cabez/ontologies/2025/2/untitled-ontology-3#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    
    SELECT ?propiedad ?valor
    WHERE {
        <%s> ?propiedad ?valor .
        FILTER (
            STRSTARTS(STR(?propiedad), "http://www.semanticweb.org/cabez/ontologies/2025/2/untitled-ontology-3#") ||
            ?propiedad IN (rdf:type, rdfs:label, rdfs:comment)
        )
    }
    """ % uri_decoded
    
    detalles = {}
    try:
        for row in g.query(query):
            prop_name = str(row.propiedad).split("#")[-1] if "#" in str(row.propiedad) else str(row.propiedad)
            
            # Manejar diferentes tipos de valores
            if isinstance(row.valor, Literal):
                if row.valor.datatype == XSD.dateTime:
                    try:
                        detalles[prop_name] = row.valor.toPython().strftime("%Y-%m-%d")
                    except:
                        detalles[prop_name] = str(row.valor)
                else:
                    detalles[prop_name] = str(row.valor)
            else:
                detalles[prop_name] = str(row.valor)
    except Exception as e:
        print(f"Error al obtener detalles: {str(e)}")
    
    # Obtener inferencias
    try:
        inferred = infer_properties(URIRef(uri_decoded))
    except Exception as e:
        print(f"Error en inferencia: {str(e)}")
        inferred = {}
    
    # Traducir los detalles si es necesario
    if lang != 'es':
        for key, value in detalles.items():
            if not value.startswith('http') and not value.replace('-', '').isdigit():
                detalles[key] = translate_text(value, 'es', lang)
    
    return render_template(
        "detalle.html",
        noticia=detalles,
        inferred=inferred,
        translations=TRANSLATIONS,
        languages=LANGUAGES,
        current_lang=lang,
        dark_mode=dark_mode
    )

@app.route("/toggle_dark_mode", methods=["POST"])
def toggle_dark_mode():
    dark_mode = request.json.get('dark_mode', True)
    response = jsonify({"success": True})
    response.set_cookie('dark_mode', str(dark_mode).lower())
    return response

if __name__ == "__main__":
    app.run(debug=True)