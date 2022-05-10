from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField
from wtforms.validators import DataRequired


class TestForm(FlaskForm):
    city = StringField('Ваш город', validators=[DataRequired()])
    submit = SubmitField('Войти')
