from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField
from wtforms.validators import DataRequired


class ImageForm(FlaskForm):
    filename = StringField('Filename', validators=[DataRequired()])
    photo = FileField(validators=[FileRequired()])
