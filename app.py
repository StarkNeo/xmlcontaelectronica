import os
import sys
from flask import Flask, render_template, redirect, url_for,send_file, request
from werkzeug.utils import secure_filename
from utils.helpers import (
    validate_xml,
    extract_excel_balanza,
    extract_excel_catalogo,
    generate_catalogo_xml,
    generate_balanza_xml,
)
from utils.forms import UploadForm, XMLForm
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["UPLOAD_FOLDER"] = os.path.join(BASE_PATH, "uploads")
app.config["XML_FOLDER"] = os.path.join(BASE_PATH, "xml")
app.config["XSD_FOLDER"] = os.path.join(BASE_PATH, "xsd")

# index route main view


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/validator", methods=["GET", "POST"])
def xmlValidator():
    form = UploadForm()
    result = None

    if form.validate_on_submit():
        xml = form.xml_file.data
        xml_path = os.path.join(app.config["XML_FOLDER"], secure_filename(xml.filename))
        #xsd_path = os.path.join(app.root_path, "xsd", "BalanzaComprobacion_1_3.xsd")
        xsd_path = os.path.join(app.config["XSD_FOLDER"], "BalanzaComprobacion_1_3.xsd")
        message = validate_xml(xml_path, xsd_path)
        result = message

    return render_template("validator.html", form=form, result=result)



@app.route("/generator", methods=["GET", "POST"])
def xmlGenerator():
    form = XMLForm()
    message = None

    if form.validate_on_submit():
        # Reading common data fields of the form submited
        RFC = form.rfc.data
        month = form.month.data
        year = form.year.data
        file_type = form.doc_type.data
        excel = form.excel_file.data
        # Create a path for excel file, this es neccesary to save it locally to be available when uploading for transformation
        excel_path = os.path.join(
            app.config["UPLOAD_FOLDER"], secure_filename(excel.filename)
        )

        # Save each file into its folder
        excel.save(excel_path)

        if file_type == "catalogo":
            # Extract data from excel
            catalogo = extract_excel_catalogo(excel_path)
            # Transform data to xml file and save it to XML folder
            filename = f"xml/{RFC}{year}{month}CT.xml"
            xml_cat_path = os.path.join(app.config["XML_FOLDER"],filename)
            generate_catalogo_xml(catalogo, xml_cat_path, RFC, month, year)
            return render_template("confirmation.html", filename = filename)
        
            # if file type is balanza
        elif file_type == "balanza":
            # Extract data from excel
            balanza = extract_excel_balanza(excel_path)
            instance = form.instance_type.data
            if instance == "N":
                filename = f"xml/{RFC}{year}{month}BN.xml"
                xml_bal_path = os.path.join(app.config["XML_FOLDER"],filename)
                generate_balanza_xml(
                    balanza, xml_bal_path, RFC, month, year, instance
                )                
            else:
                filename = f"xml/{RFC}{year}{month}BC.xml"
                xml_bal_path = os.path.join(app.config["XML_FOLDER"],filename)
                mod_date = str(form.mod_date.data)
                generate_balanza_xml(
                    balanza, xml_bal_path, RFC, month, year, instance, mod_date
                )

        message = f"XML generado exitosamente"
        return render_template("confirmation.html", filename = filename)
        
    return render_template("generator.html", form=form, message=message)


@app.route("/download_xml/<filename>")
def download_xml(filename):
    file_path = os.path.join(app.config["XML_FOLDER"], filename)
    return send_file(file_path, mimetype="application/xml", as_attachment=True)



if __name__ == "__main__":
    os.makedirs(os.path.join(BASE_PATH, "uploads"), exist_ok=True)
    os.makedirs(os.path.join(BASE_PATH, "xml"), exist_ok=True)
    os.makedirs(os.path.join(BASE_PATH, "xsd"), exist_ok=True)
    app.run(debug=True)
