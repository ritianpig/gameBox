from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField
from wtforms.validators import DataRequired


class ClickForm(FlaskForm):
    name = StringField('Name',validators=[DataRequired()])
    channel = StringField('Channel',validators=[DataRequired()])
    submit = SubmitField('提交')

