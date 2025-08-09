# RUTA: app/application/forms.py

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, SelectField, DateField, TextAreaField
from wtforms.validators import DataRequired, Length, Regexp, Optional, Email, NumberRange

class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar Sesión')

class TwoFactorForm(FlaskForm):
    code = StringField('Código de 6 dígitos', validators=[
        DataRequired(),
        Length(min=6, max=6, message="El código debe tener 6 dígitos."),
        Regexp('^[0-9]*$', message="El código solo debe contener números.")
    ])
    submit = SubmitField('Verificar y Entrar')

class FiltroPersonalForm(FlaskForm):
    dni = StringField('Buscar por DNI', validators=[Optional(), Length(max=8)])
    nombres = StringField('Buscar por Nombre o Apellidos', validators=[Optional(), Length(max=100)])
    submit = SubmitField('Buscar')

class PersonalForm(FlaskForm):
    nombres = StringField('Nombres Completos', validators=[DataRequired(), Length(max=50)])
    apellidos = StringField('Apellidos Completos', validators=[DataRequired(), Length(max=50)])
    dni = StringField('DNI', validators=[DataRequired(), Length(min=8, max=8, message="El DNI debe tener 8 caracteres.")])
    email = StringField('Correo Electrónico', validators=[DataRequired(), Email(), Length(max=100)])
    sexo = SelectField('Sexo', choices=[('', '-- Seleccione --'), ('M', 'Masculino'), ('F', 'Femenino')], validators=[DataRequired(message="Debe seleccionar un género.")])
    id_unidad = SelectField('Unidad Administrativa', coerce=int, validators=[NumberRange(min=1, message="Debe seleccionar una unidad válida.")])
    fecha_ingreso = DateField('Fecha de Ingreso', validators=[DataRequired()])
    direccion = StringField('Dirección', validators=[Optional(), Length(max=200)])
    telefono = StringField('Teléfono', validators=[Optional(), Length(max=20)])
    estado_civil = StringField('Estado Civil', validators=[Optional(), Length(max=20)])
    nacionalidad = StringField('Nacionalidad', validators=[Optional(), Length(max=50)])
    fecha_nacimiento = DateField('Fecha de Nacimiento', validators=[Optional()])
    submit = SubmitField('Guardar Legajo')

class DocumentoForm(FlaskForm):
    id_seccion = SelectField('Sección del Legajo', coerce=int, validators=[NumberRange(min=1, message="Debe seleccionar una sección.")])
    id_tipo = SelectField('Tipo de Documento', coerce=int, validators=[NumberRange(min=1, message="Debe seleccionar un tipo de documento.")])
    descripcion = TextAreaField('Descripción (Opcional)', validators=[Optional(), Length(max=500)])
    archivo = FileField('Seleccionar Archivo', validators=[
        DataRequired(message="Debe seleccionar un archivo."),
        FileAllowed(['pdf', 'png', 'jpg', 'jpeg'], '¡Solo se permiten archivos de imagen y PDF!')
    ])
    submit = SubmitField('Subir Documento')