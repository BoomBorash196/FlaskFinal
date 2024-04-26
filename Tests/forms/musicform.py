from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField
from wtforms.validators import DataRequired


class MusicForm(FlaskForm):
    filename = StringField('Filename', validators=[DataRequired()])
    music_file = FileField(validators=[FileRequired()])
