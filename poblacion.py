import os
import datetime
from rdflib import Graph, Namespace, Literal, URIRef, RDF, XSD
from config import g, ONTOLOGY_NS, BASE_URI
from utils import generar_uri

def insertar_noticia():
    """Interfaz para insertar una nueva noticia"""
    print("\n--- Insertar Nueva Noticia ---")
    
    noticia_uri = generar_uri(BASE_URI, "Noticia")
    titulo = input("Título de la noticia: ")
    autor = input("Autor: ")
    tematica = input("Temática (separar con comas si son varias): ")
    ubicacion = input("Ubicación: ")
    idioma = input("Idioma: ")
    fecha_pub = input("Fecha de publicación (YYYY-MM-DD o dejar vacío para hoy): ")
    fecha_pub = fecha_pub if fecha_pub else datetime.date.today().strftime("%Y-%m-%d")
    multimedia = input("¿Tiene contenido multimedia? (s/n): ").lower() == 's'

    print("\nSeleccione el formato de la noticia:")
    print("1. Artículo")
    print("2. Reportaje")
    print("3. Entrevista")
    print("4. Crónica")
    print("5. Columna")
    opcion_formato = input("Opción (1-5): ")
    
    formatos = {
        "1": "Artículo",
        "2": "Reportaje",
        "3": "Entrevista",
        "4": "Crónica",
        "5": "Columna"
    }
    tipo_formato = formatos.get(opcion_formato, "Artículo")

    g.add((noticia_uri, RDF.type, ONTOLOGY_NS.Noticia))
    g.add((noticia_uri, ONTOLOGY_NS.Título, Literal(titulo)))
    g.add((noticia_uri, ONTOLOGY_NS.Autor, Literal(autor)))
    
    for tema in tematica.split(','):
        g.add((noticia_uri, ONTOLOGY_NS.Temática, Literal(tema.strip())))
    
    g.add((noticia_uri, ONTOLOGY_NS.Ubicación, Literal(ubicacion)))
    g.add((noticia_uri, ONTOLOGY_NS.Idioma, Literal(idioma)))
    g.add((noticia_uri, ONTOLOGY_NS.Fecha_publicación, Literal(fecha_pub, datatype=XSD.date)))
    g.add((noticia_uri, ONTOLOGY_NS.Multimedia_asociado, Literal(multimedia, datatype=XSD.boolean)))
    
    formato_uri = generar_uri(BASE_URI, tipo_formato)
    g.add((formato_uri, RDF.type, ONTOLOGY_NS[tipo_formato]))
    g.add((noticia_uri, ONTOLOGY_NS.tiene, formato_uri))
    
    print("\n--- Contenido de la Noticia ---")
    contenido_texto = input("Texto principal de la noticia: ")
    if contenido_texto:
        texto_uri = generar_uri(BASE_URI, "Texto")
        g.add((texto_uri, RDF.type, ONTOLOGY_NS.Texto))
        g.add((texto_uri, ONTOLOGY_NS.ContenidoTexto, Literal(contenido_texto)))
        g.add((texto_uri, ONTOLOGY_NS.pertenece_a, noticia_uri))
        g.add((noticia_uri, ONTOLOGY_NS.tiene, texto_uri))
    
    if multimedia:
        print("\n--- Detalles Multimedia ---")
        tipo_multimedia = input("Tipo de multimedia (Imagen/Video/Audio): ").capitalize()
        if tipo_multimedia in ["Imagen", "Video", "Audio"]:
            multimedia_uri = generar_uri(BASE_URI, tipo_multimedia)
            g.add((multimedia_uri, RDF.type, ONTOLOGY_NS[tipo_multimedia]))
            g.add((noticia_uri, ONTOLOGY_NS.tiene, multimedia_uri))
            
            if tipo_multimedia == "Imagen":
                resolucion = input("Resolución de la imagen: ")
                modo_color = input("Modo de color: ")
                g.add((multimedia_uri, ONTOLOGY_NS.ResoluciónImágen, Literal(resolucion)))
                g.add((multimedia_uri, ONTOLOGY_NS.ModoColor, Literal(modo_color)))
            
            elif tipo_multimedia == "Video":
                duracion = input("Duración en segundos: ")
                tasa_fotogramas = input("Tasa de fotogramas: ")
                resolucion = input("Resolución: ")
                g.add((multimedia_uri, ONTOLOGY_NS.Duración, Literal(int(duracion), datatype=XSD.integer)))
                g.add((multimedia_uri, ONTOLOGY_NS.TasaFotogramas, Literal(float(tasa_fotogramas), datatype=XSD.float)))
                g.add((multimedia_uri, ONTOLOGY_NS.ResoluciónVideo, Literal(resolucion)))
            
            elif tipo_multimedia == "Audio":
                duracion = input("Duración en segundos: ")
                canales = input("Número de canales: ")
                g.add((multimedia_uri, ONTOLOGY_NS.DuraciónAudio, Literal(int(duracion), datatype=XSD.integer)))
                g.add((multimedia_uri, ONTOLOGY_NS.Canales, Literal(float(canales), datatype=XSD.float)))
    
    if input("\n¿Desea agregar información de verificación? (s/n): ").lower() == 's':
        insertar_verificacion(noticia_uri)
    
    g.serialize(destination="noticias_ontologia.rdf", format="xml")
    print("\n¡Noticia agregada exitosamente!")

def insertar_verificacion(noticia_uri):
    """Interfaz para insertar una verificación de noticia"""
    print("\n--- Información de Verificación ---")
    
    verificacion_uri = generar_uri(BASE_URI, "Verificacion")
    fecha_verificacion = input("Fecha de verificación (YYYY-MM-DD o dejar vacío para hoy): ")
    fecha_verificacion = fecha_verificacion if fecha_verificacion else datetime.date.today().strftime("%Y-%m-%d")
    
    print("\nSeleccione el método de verificación:")
    print("1. Fact-checking")
    print("2. Verificación de Fuente")
    print("3. Verificación de Imagen")
    print("4. Verificación de Video")
    print("5. Patrones Lingüísticos")
    opcion_metodo = input("Opción (1-5): ")
    
    metodos = {
        "1": ("Fact-checking", "Fact-checking"),
        "2": ("Verificación_de_Fuente", "Verificación de Fuente"),
        "3": ("Verificación_de_Imágen", "Verificación de Imagen"),
        "4": ("Verificación_de_Video", "Verificación de Video"),
        "5": ("Patrones_lingüísticos", "Patrones Lingüísticos")
    }
    
    metodo_uri, metodo_nombre = metodos.get(opcion_metodo, ("Fact-checking", "Fact-checking"))
    
    g.add((verificacion_uri, RDF.type, ONTOLOGY_NS.Verificación))
    g.add((verificacion_uri, ONTOLOGY_NS.evalua, noticia_uri))
    g.add((verificacion_uri, ONTOLOGY_NS.FechaVerificación, Literal(fecha_verificacion, datatype=XSD.date)))
    
    metodo_inst_uri = generar_uri(BASE_URI, metodo_uri)
    g.add((metodo_inst_uri, RDF.type, ONTOLOGY_NS[metodo_uri]))
    g.add((verificacion_uri, ONTOLOGY_NS.se_apoya_en, metodo_inst_uri))
    
    if metodo_uri == "Fact-checking":
        fuentes = input("Fuentes consultadas (separar con comas): ")
        cantidad_fuentes = input("Cantidad de fuentes: ")
        for fuente in fuentes.split(','):
            g.add((metodo_inst_uri, ONTOLOGY_NS.FuentesUtilizadasFC, Literal(fuente.strip())))
        g.add((metodo_inst_uri, ONTOLOGY_NS.CantidadFuentes, Literal(int(cantidad_fuentes), datatype=XSD.integer)))
    
    elif metodo_uri == "Verificación_de_Fuente":
        autoridad = input("Autoridad de la fuente: ")
        registro = input("¿Tiene registro oficial? (s/n): ").lower() == 's'
        g.add((metodo_inst_uri, ONTOLOGY_NS.AutoridadFuente, Literal(autoridad)))
        g.add((metodo_inst_uri, ONTOLOGY_NS.RegistroOficial, Literal(registro, datatype=XSD.boolean)))
    
    elif metodo_uri == "Verificación_de_Imágen":
        coincidencia = input("Coincidencia visual: ")
        deteccion = input("¿Se detectaron ediciones? (s/n): ").lower() == 's'
        g.add((metodo_inst_uri, ONTOLOGY_NS.CoincidenciaVisual, Literal(coincidencia)))
        g.add((metodo_inst_uri, ONTOLOGY_NS.DetecciónEdiciones, Literal(deteccion, datatype=XSD.boolean)))
    
    elif metodo_uri == "Verificación_de_Video":
        coherencia = input("¿Hay coherencia audiovisual? (s/n): ").lower() == 's'
        contexto = input("Coincidencia contextual: ")
        g.add((metodo_inst_uri, ONTOLOGY_NS.CoherenciaAudiovisual, Literal(coherencia, datatype=XSD.boolean)))
        g.add((metodo_inst_uri, ONTOLOGY_NS.CoincidenciaContextual, Literal(contexto)))
    
    elif metodo_uri == "Patrones_lingüísticos":
        complejidad = input("Complejidad del texto: ")
        deteccion_sesgo = input("¿Se detectó sesgo? (s/n): ").lower() == 's'
        g.add((metodo_inst_uri, ONTOLOGY_NS.Complejidad, Literal(complejidad)))
        g.add((metodo_inst_uri, ONTOLOGY_NS.DetecciónSesgo, Literal(deteccion_sesgo, datatype=XSD.boolean)))
    
    resultado = input("Resultado de la verificación: ")
    estado = input("Estado (Finalizada/En proceso/Rechazada): ")
    g.add((verificacion_uri, ONTOLOGY_NS.Resultado, Literal(resultado)))
    g.add((verificacion_uri, ONTOLOGY_NS.Estado, Literal(estado)))
    
    print("\n--- Entidad Responsable ---")
    print("1. Organización")
    print("2. Medio de Comunicación")
    print("3. Usuario")
    print("4. Algoritmo de IA")
    opcion_responsable = input("Opción (1-4): ")
    
    if opcion_responsable in ["1", "2", "3", "4"]:
        responsable_uri = generar_uri(BASE_URI, "EntidadResponsable")
        tipos = {
            "1": ("Organización", "TipoOrganización"),
            "2": ("Medio_de_comunicación", "AlineaciónEditorial"),
            "3": ("Usuarios", "Rol"),
            "4": ("Algoritmo_de_IA", "TipoAprendizaje")
        }
        tipo_entidad, propiedad_especifica = tipos[opcion_responsable]
        
        nombre = input(f"Nombre de la {tipo_entidad.replace('_', ' ')}: ")
        especifico = input(f"{propiedad_especifica.replace('_', ' ')}: ")
        experiencia = input("Años de experiencia (opcional): ")
        
        g.add((responsable_uri, RDF.type, ONTOLOGY_NS[tipo_entidad]))
        g.add((responsable_uri, ONTOLOGY_NS[propiedad_especifica], Literal(especifico)))
        g.add((responsable_uri, ONTOLOGY_NS.Especialización, Literal(nombre)))
        
        if experiencia:
            g.add((responsable_uri, ONTOLOGY_NS.Experiencia, Literal(int(experiencia), datatype=XSD.integer)))
        
        g.add((verificacion_uri, ONTOLOGY_NS.se_realiza_por, responsable_uri))
    
    print("\n¡Verificación agregada exitosamente!")

def menu_principal():
    """Menú principal del sistema de población"""
    while True:
        print("\n--- Sistema de Población de Ontología de Noticias ---")
        print("1. Insertar nueva noticia")
        print("2. Insertar verificación (sin noticia)")
        print("3. Insertar herramienta de verificación")
        print("4. Insertar modelo de IA")
        print("5. Salir y guardar")
        
        opcion = input("Seleccione una opción: ")
        
        if opcion == "1":
            insertar_noticia()
        elif opcion == "2":
            print("\nNoticias disponibles para verificar:")
            query = """
            PREFIX untitled-ontology-3: <http://www.semanticweb.org/cabez/ontologies/2025/2/untitled-ontology-3#>
            SELECT ?noticia ?titulo
            WHERE {
                ?noticia a untitled-ontology-3:Noticia ;
                         untitled-ontology-3:Título ?titulo .
                FILTER NOT EXISTS { ?verificacion untitled-ontology-3:evalua ?noticia }
            }
            """
            resultados = g.query(query)
            for i, row in enumerate(resultados, 1):
                print(f"{i}. {row.titulo} ({row.noticia})")
            
            seleccion = input("\nSeleccione el número de la noticia a verificar (o 0 para cancelar): ")
            if seleccion.isdigit() and 0 < int(seleccion) <= len(resultados):
                noticia_uri = list(resultados)[int(seleccion)-1].noticia
                insertar_verificacion(noticia_uri)
        elif opcion == "3":
            from herramientas import insertar_herramienta
            insertar_herramienta()
        elif opcion == "4":
            from herramientas import insertar_modelo_ia
            insertar_modelo_ia()
        elif opcion == "5":
            g.serialize(destination="noticias_ontologia.rdf", format="xml")
            print("Cambios guardados. Saliendo...")
            break
        else:
            print("Opción no válida. Intente nuevamente.")

if __name__ == "__main__":
    menu_principal()