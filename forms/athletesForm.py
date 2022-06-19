from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, URLField
from wtforms.validators import DataRequired


class AthleteForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    achievement = StringField('Достижение', validators=[DataRequired()])
    sport = StringField('Вид спорта', validators=[DataRequired()])
    img = URLField('Url фото', validators=[DataRequired()])
    submit = SubmitField('Добавить')
