from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField, SelectField, StringField, PasswordField, DateField
from wtforms.validators import DataRequired
import datetime


class UploadForm(FlaskForm):
    xml_file = FileField("Archivo XML", validators=[DataRequired()])
    xsd_file = FileField("Esquema XSD")
    submit = SubmitField('Validar')
    
    
class XMLForm(FlaskForm):
    rfc = StringField('RFC', validators=[DataRequired()])
    month = SelectField('Mes', choices=["01","02","03","04","05","06","07","08","09","10","11","12"], validators=[DataRequired()])
    year = StringField('Ejercicio', validators=[DataRequired()])
    sign = SelectField("Firmar el documento?", choices=[('si','Si'),('no','No')],default='no', validators=[DataRequired()])
    doc_type = SelectField('Tipo de documento', choices=[('catalogo', 'Catálogo'), ('balanza', 'Balanza')])
    instance_type = SelectField('Tipo de envio', choices=["N","C"], default='N')
    mod_date = DateField("Fecha Modificacion", format="%Y-%m-%d",default=datetime.date.today)
    excel_file = FileField('Archivo Excel', validators=[DataRequired()])
    cer_file = FileField('Certificado .cer')
    key_file = FileField('Clave privada .key')
    password = PasswordField('Contraseña de clave privada')
    submit = SubmitField('Generar XML')

