from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class NewPostForm(FlaskForm):
    """new pin form
    """

    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Description', validators=[DataRequired()])
    post_img = FileField('Pin Image', validators=[FileAllowed(['jpg', 'png', 'jpeg']), DataRequired()])
    img_tag = StringField('Image Tag', validators=[DataRequired()])
    post = SubmitField('Post')


class UpdatePostForm(FlaskForm):
    """update pin form
    """

    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Description', validators=[DataRequired()])
    img_tag = StringField('Image Tag', validators=[DataRequired()])
    update = SubmitField('Update')


# new board --------------------------------
class NewBoardForm(FlaskForm):
    """create new board form
    """

    name = StringField('Name', validators=[DataRequired()])
    create = SubmitField('Create')
