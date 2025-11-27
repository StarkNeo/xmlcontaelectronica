import os
import io
from flask import send_file
import pandas as pd
from lxml import etree

"""def validate_xml(xml_path, xsd_path):
    try:
        # Load the XSD schema
        print("Este XSD estoy usando: ", xsd_path)
        print("Este XML voy a validar: ", xml_path)
        with open(xsd_path, 'rb') as xsd_file:
            #schema_root = etree.XML(xsd_file.read())
            #schema = etree.XMLSchema(schema_root)
            schema_doc = etree.XML(xsd_file.read())
            schema = etree.XMLSchema(schema_doc)
        # load the XML file
        with open(xml_path, 'rb') as xml_file:
            xml_doc = etree.parse(xml_file)
            
        # Validation
        #if schema.validate(xml_doc):
         #   return "XML valido"
        #else:
         #   error = schema.error_log.last_error
          #  return f"XML invalido: {error.message} (linea {error.line})"
        
        schema.assertValid(xml_doc)
        return " XML valido"    
    except etree.DocumentInvalid as e:
        return f"XML invalido: {str(e)}"
    except Exception as e:
        return f"Error al procesar: {str(e)}"
"""
def validate_xml(xml_path, xsd_path):
    try:
        # Parser that allows external imports
        parser = etree.XMLParser(load_dtd=True, no_network=False)

        # Load the main XSD (e.g. CatalogoCuentas_1_3.xsd)
        with open(xsd_path, 'rb') as xsd_file:
            schema_doc = etree.parse(xsd_file, parser)
            schema = etree.XMLSchema(schema_doc)

        # Load the XML to validate
        with open(xml_path, 'rb') as xml_file:
            xml_doc = etree.parse(xml_file, parser)

        # Validate
        if schema.validate(xml_doc):
            return "XML válido"
        else:
            error = schema.error_log.last_error
            return f"XML inválido: {error.message} (línea {error.line})"

    except etree.DocumentInvalid as e:
        return f"XML inválido: {str(e)}"
    except Exception as e:
        return f"Error al procesar {xml_path}: {str(e)}"


       
def extract_excel_balanza(excel_path,sheet_balanza="BZA"):
    df_balanza = pd.read_excel(excel_path, sheet_name=sheet_balanza, dtype=str)
    
    
    # Procesar balanza de comprobacion
    balanza = []
    for _,row in df_balanza.iterrows():
        cuenta = {
            "NumCta": row["NumCta"],
            "SaldoIni":row["SaldoIni"],
            "Debe": row["Debe"],
            "Haber": row["Haber"],
            "SaldoFin": row["SaldoFin"],
            }
        balanza.append(cuenta)
    
    return balanza


def extract_excel_catalogo(excel_path, sheet_catalogo = "CT"):
    df_catalogo = pd.read_excel(excel_path, sheet_name=sheet_catalogo, dtype=str)
    # Procesar catálogo de cuentas
    catalogo = []
    
    for _, row in df_catalogo.iterrows():
        cuenta = {
            "CodAgrup": row["CodAgrup"],
            "NumCta": row["NumCta"],
            "Desc": row["Desc"],
            "SubCtaDe": row["SubCtaDe"],
            "Nivel": row["Nivel"],
            "Natur": row["Natur"],            
        }
        catalogo.append(cuenta)
    
    return catalogo

metadata_catalogo = {
    "xmlns:xsi":"http://www.w3.org/2001/XMLSchema-instance",
    "xmlns:catalogocuentas":"http://www.sat.gob.mx/esquemas/ContabilidadE/1_3/CatalogoCuentas",
    "xsi:schemaLocation":"http://www.sat.gob.mx/esquemas/ContabilidadE/1_3/CatalogoCuentas http://www.sat.gob.mx/esquemas/ContabilidadE/1_3/CatalogoCuentas/CatalogoCuentas_1_3.xsd",
    "Version":"1.3",
    "RFC": "",
    "Mes":"",
    "Anio": ""
}

metadata_balanza = {
    "xsi:schemaLocation":"http://www.sat.gob.mx/esquemas/ContabilidadE/1_3/BalanzaComprobacion http://www.sat.gob.mx/esquemas/ContabilidadE/1_3/BalanzaComprobacion/BalanzaComprobacion_1_3.xsd",
    "xmlns:xsi":"http://www.w3.org/2001/XMLSchema-instance",
    "xmlns:BCE":"http://www.sat.gob.mx/esquemas/ContabilidadE/1_3/BalanzaComprobacion",
    "Version":"1.3",
    "RFC":"",
    "Mes":"",
    "Anio":"",
    "TipoEnvio":""
}






# Function to generate XML file for catalogo de cuentas

def generate_catalogo_xml(datos_catalogo, ruta_salida, rfc, month, year, metadata = metadata_catalogo):
    ns = metadata["xmlns:catalogocuentas"]
    nsmap = {
        "catalogocuentas": ns,
        "xsi": metadata["xmlns:xsi"]
    }
    metadata["RFC"] = rfc
    metadata["Mes"] = month
    metadata["Anio"] = year
    
    root_attrs = {
        "Version":metadata["Version"],
        "RFC": metadata["RFC"],
        "Mes": metadata["Mes"],
        "Anio": metadata["Anio"]
    }
    
            
    root = etree.Element("{%s}Catalogo" % ns, nsmap=nsmap, **root_attrs)
    
    # Add xsi:schemaLocation
    root.attrib["{%s}schemaLocation" % metadata["xmlns:xsi"]] = metadata["xsi:schemaLocation"]

    # Add node cuentas
    for cuenta in datos_catalogo:
        etree.SubElement(root, "{%s}Ctas" % ns,
                         CodAgrup=cuenta["CodAgrup"],
                         NumCta=cuenta["NumCta"],
                         Desc=cuenta["Desc"],
                         Nivel=str(cuenta["Nivel"]),
                         Natur=cuenta["Natur"])

    tree = etree.ElementTree(root)
    """
    # Guardar en memoria en lugar de archivo físico
    xml_bytes = io.BytesIO()
    tree.write(xml_bytes, encoding="UTF-8", xml_declaration=True, pretty_print=True)
    xml_bytes.seek(0)

    # Retornar para descarga
    return send_file(
        xml_bytes,
        mimetype="application/xml",
        as_attachment=True,
        download_name=f"Catalogo_{rfc}_{month}_{year}.xml"
    )
    """
    tree.write(ruta_salida, encoding="UTF-8", xml_declaration=True, pretty_print=True)


def generate_balanza_xml(datos_balanza, ruta_salida, rfc, month, year, instance, mod_date = None, metadata = metadata_balanza):
    ns = metadata["xmlns:BCE"]
    nsmap = {
        "BCE": ns,
        "xsi": metadata["xmlns:xsi"]
    }
    
    
    # Root node
    root_attrs = {
        "Version": metadata["Version"],
        "RFC": rfc,
        "Mes": month,
        "Anio": year,
        "TipoEnvio": instance
    }
    
    if instance == "C":
        metadata["FechaModBal"] = mod_date
        root_attrs["FechaModBal"] = mod_date
    
    root = etree.Element("{%s}Balanza" % ns, nsmap=nsmap, **root_attrs)            
        
    
    # Add xsi:schemaLocation    
    root.attrib["{%s}schemaLocation" % metadata["xmlns:xsi"]] = metadata["xsi:schemaLocation"]
    
    # Add node cuentas   
    
    for cuenta in datos_balanza:
        etree.SubElement(root, "{%s}Ctas" % ns,
                         NumCta=cuenta["NumCta"],
                         SaldoIni=str(cuenta["SaldoIni"]),
                         Debe=str(cuenta["Debe"]),
                         Haber=str(cuenta["Haber"]),
                         SaldoFin=str(cuenta["SaldoFin"]))

    
    tree = etree.ElementTree(root)
    tree.write(ruta_salida, encoding="UTF-8", xml_declaration=True, pretty_print=True)
   

