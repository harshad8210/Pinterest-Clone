from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class SearchForm(FlaskForm):
    """pin search form
    """

    searched = StringField('searched', validators=[DataRequired()])
    search = SubmitField('Search')
