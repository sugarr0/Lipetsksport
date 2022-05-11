from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class SportForm(FlaskForm):
    sport = StringField('Название вида спорта', validators=[DataRequired()])
    submit = SubmitField('Добавить')
