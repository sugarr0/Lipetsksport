from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField
from wtforms.validators import DataRequired


class EventForm(FlaskForm):
    when = StringField('Дата проведения', validators=[DataRequired()])
    name = StringField('Название', validators=[DataRequired()])
    about = StringField('Место проведения', validators=[DataRequired()])
    sport = StringField('Спортивное направление', validators=[DataRequired()])
    img = StringField('Url картинки', validators=[DataRequired()])
    submit = SubmitField('Добавить')
