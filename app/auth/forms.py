from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired


class SignInForm(FlaskForm):
    username = StringField('Username:',
                           validators=[DataRequired("Username can't be null")],
                           render_kw={'placeholder': 'Your username'})
    email = StringField('Email address:',
                        validators=[DataRequired("Email can't be null")],
                        render_kw={'placeholder': 'Your email'})
    password = PasswordField('Password:',
                             validators=[DataRequired("Password can't be null")],
                             render_kw={'placeholder': 'Enter password'})
    passwordConfirm = PasswordField('Password Confirm:',
                                    validators=[DataRequired("Password confirm can't be null")],
                                    render_kw={'placeholder': 'Enter password again'})
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    email = StringField('Email address:',
                        validators=[DataRequired("Email can't be null")],
                        render_kw={'placeholder': 'Your email'})
    password = PasswordField('Password:',
                             validators=[DataRequired("Password can't be null")],
                             render_kw={'placeholder': 'Enter password'})
