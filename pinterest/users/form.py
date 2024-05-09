from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from pinterest.models import User
from pinterest.users.utils import password_check
from validate_email_address import validate_email


class LoginForm(FlaskForm):
    """user login form
    """

    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    login = SubmitField('Log in')


class RegistrationForm(FlaskForm):
    """user registration form
    """

    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=20)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        """validate user name
        :param username: string
        :return: if username is not valid raise validation error
        """

        same_user = User.query.filter_by(username=username.data).first()
        if same_user:
            raise ValidationError('That username is taken please choose another one.')

    def validate_email(self, email):
        """validate user email
        :param email: string
        :return: if email is not valid raise validation error
        """

        same_email = User.query.filter_by(email=email.data).first()
        if same_email:
            raise ValidationError('That email is taken please choose another one.')
        is_exists = validate_email(email.data, verify=True)
        if not is_exists:
            raise ValidationError('Email does not exists.')

    def validate_password(self, password):
        """validate user password
        :param password: string
        :return: if password is not valid raise validation error
        """

        error, msg = password_check(password.data)
        if error:
            raise ValidationError(msg)


class UpdateAccForm(FlaskForm):
    """update account form
    """

    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    profile_pic = FileField('Update profile picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        """validate user name
        :param username: string
        :return: if username is not valid raise validation error
        """

        if username.data != current_user.username:
            same_user = User.query.filter_by(username=username.data).first()
            if same_user:
                raise ValidationError('That username is taken please choose another one.')

    def validate_email(self, email):
        """validate user email
        :param email: string
        :return: if email is not valid raise validation error
        """

        same_email = User.query.filter_by(email=email.data).first()
        if same_email and same_email.email != email.data:
            raise ValidationError('That email is taken please choose another one.')


class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        """validate user email
        :param email: string
        :return: if email is not valid raise validation error
        """

        same_email = User.query.filter_by(email=email.data).first()
        if same_email is None:
            raise ValidationError('There is no account with that email, You must register first.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=20)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
