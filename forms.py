"""Formularios Flask-WTF del proyecto."""
from flask_wtf import FlaskForm
from wtforms import DecimalField, PasswordField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, NumberRange

class RegisterForm(FlaskForm):
    username = StringField("Usuario", validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField("Correo", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Contraseña", validators=[DataRequired(), Length(min=4)])
    submit = SubmitField("Crear cuenta")
class LoginForm(FlaskForm):
    email = StringField("Correo", validators=[DataRequired(), Email()])
    password = PasswordField("Contraseña", validators=[DataRequired()])
    submit = SubmitField("Ingresar")
class ProductForm(FlaskForm):
    name = StringField("Nombre", validators=[DataRequired(), Length(max=100)])
    genre = StringField("Género", validators=[DataRequired(), Length(max=80)])
    price = DecimalField("Precio", validators=[DataRequired(), NumberRange(min=0)], places=2)
    description = TextAreaField("Descripción", validators=[Length(max=500)])
    submit = SubmitField("Guardar producto")
