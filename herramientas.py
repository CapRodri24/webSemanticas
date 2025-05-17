from rdflib import Literal
from rdflib.namespace import RDF, XSD
from utils import generar_uri
from config import g, ONTOLOGY_NS, BASE_URI

def insertar_herramienta():
    """Interfaz para insertar una nueva herramienta de verificación"""
    print("\n--- Insertar Nueva Herramienta ---")
    
    herramienta_uri = generar_uri(BASE_URI, "Herramienta")
    nombre = input("Nombre de la herramienta: ")
    tipo = input("Tipo de herramienta: ")
    plataforma = input("Plataforma: ")
    accesibilidad = input("Accesibilidad (Gratuita/De paga/Mixta): ")
    efectividad = input("Nivel de efectividad (1-100): ")
    
    g.add((herramienta_uri, RDF.type, ONTOLOGY_NS.Herramienta))
    g.add((herramienta_uri, ONTOLOGY_NS.TipoHerramienta, Literal(tipo)))
    g.add((herramienta_uri, ONTOLOGY_NS.Plataforma, Literal(plataforma)))
    g.add((herramienta_uri, ONTOLOGY_NS.Accesibilidad, Literal(accesibilidad)))
    g.add((herramienta_uri, ONTOLOGY_NS.NivelEfectividad, Literal(int(efectividad), datatype=XSD.integer)))
    
    print("\nSeleccione el tipo específico de herramienta:")
    print("1. Motor de búsqueda inversa")
    print("2. Plataforma de detección automática")
    print("3. Base de datos de fake news")
    print("4. Análisis de metadatos")
    opcion = input("Opción (1-4): ")
    
    if opcion == "1":
        g.add((herramienta_uri, RDF.type, ONTOLOGY_NS.Motor_de_búsqueda_inversa))
        tipo_busqueda = input("Tipo de búsqueda: ")
        fuentes = input("Fuentes consultadas: ")
        latencia = input("Latencia de procesamiento: ")
        g.add((herramienta_uri, ONTOLOGY_NS.TipoBúsqueda, Literal(tipo_busqueda)))
        g.add((herramienta_uri, ONTOLOGY_NS.FuentesConsultadas, Literal(fuentes)))
        g.add((herramienta_uri, ONTOLOGY_NS.LatenciaProcesamiento, Literal(float(latencia), datatype=XSD.float)))
    
    elif opcion == "2":
        g.add((herramienta_uri, RDF.type, ONTOLOGY_NS.Plataforma_de_detección_automática))
        latencia = input("Latencia de procesamiento: ")
        g.add((herramienta_uri, ONTOLOGY_NS.latenciaProcesamientoPDA, Literal(float(latencia), datatype=XSD.float)))
    
    elif opcion == "3":
        g.add((herramienta_uri, RDF.type, ONTOLOGY_NS.DB_de_FakeNews))
        alcance = input("Alcance: ")
        registros = input("Número de registros: ")
        frecuencia = input("Frecuencia de actualización: ")
        g.add((herramienta_uri, ONTOLOGY_NS.Alcance, Literal(alcance)))
        g.add((herramienta_uri, ONTOLOGY_NS.NúmeroRegistros, Literal(int(registros), datatype=XSD.integer)))
        g.add((herramienta_uri, ONTOLOGY_NS.FrecuenciaActualización, Literal(frecuencia)))
    
    elif opcion == "4":
        g.add((herramienta_uri, RDF.type, ONTOLOGY_NS.Análisis_de_metadatos))
        formatos = input("Formatos soportados: ")
        deteccion = input("¿Detecta manipulación? (s/n): ").lower() == 's'
        g.add((herramienta_uri, ONTOLOGY_NS.FormatosSoportados, Literal(formatos)))
        g.add((herramienta_uri, ONTOLOGY_NS.DetecciónManipulación, Literal(deteccion, datatype=XSD.boolean)))
    
    g.serialize(destination="noticias_ontologia.rdf", format="xml")
    print("\n¡Herramienta agregada exitosamente!")

def insertar_modelo_ia():
    """Interfaz para insertar un nuevo modelo de IA"""
    print("\n--- Insertar Nuevo Modelo de IA ---")
    
    modelo_uri = generar_uri(BASE_URI, "ModeloIA")
    nombre = input("Nombre del modelo: ")
    precision = input("Precisión (1-100): ")
    actualizacion = input("Fecha de última actualización (YYYY-MM-DD): ")
    entrenado_con = input("Datos de entrenamiento: ")
    
    g.add((modelo_uri, RDF.type, ONTOLOGY_NS.Modelo_IA))
    g.add((modelo_uri, ONTOLOGY_NS.Precisión_Modelo_IA, Literal(int(precision), datatype=XSD.integer)))
    g.add((modelo_uri, ONTOLOGY_NS.Actualización, Literal(actualizacion, datatype=XSD.date)))
    g.add((modelo_uri, ONTOLOGY_NS.Entrenado_con, Literal(entrenado_con)))
    
    idiomas = input("Idiomas soportados (separar con comas): ")
    for idioma in idiomas.split(','):
        g.add((modelo_uri, ONTOLOGY_NS.IdiomaSoportaModelo_IA, Literal(idioma.strip())))
    
    g.serialize(destination="noticias_ontologia.rdf", format="xml")
    print("\n¡Modelo de IA agregado exitosamente!")