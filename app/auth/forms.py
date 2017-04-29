#! coding=utf-8

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms import ValidationError
from wtforms.validators import Required, Email, Length, Regexp, EqualTo
from ..models import User


class LoginForm(FlaskForm):
    email = StringField(
        'Email', validators=[Required(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')


class RegistrationForm(FlaskForm):
    email = StringField(
        'Email', validators=[Required(), Length(1, 64), Email()])
    username = StringField(
        'Username',
        validators=[
            Required(), Length(1, 64),
            Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                   'Username must have only letters'
                   ', numbers, dots or '
                   'underscores. And must start with letters.')
        ])
    password = PasswordField(
        'Password',
        validators=[Required(), EqualTo('password1', 'Passwords must match.')])
    password1 = PasswordField('Confirm password', validators=[Required()])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username is taken.')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('old password', validators=[Required()])
    new_password = PasswordField(
        'new password',
        validators=[
            Required(), EqualTo('new_password1', 'Passwords must match.')
        ])
    new_password1 = PasswordField('confirm password', validators=[Required()])
    submit = SubmitField('Submit')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField(
        'Email', validators=[Required(), Length(1, 64), Email()])
    submit = SubmitField('Reset Password')


class ResetPasswordForm(FlaskForm):
    email = StringField(
        'Email', validators=[Required(), Length(1, 64), Email()])
    new_password = PasswordField(
        'new password',
        validators=[
            Required(), EqualTo('new_password1', 'Passwords must match.')
        ])
    new_password1 = PasswordField('confirm password', validators=[Required()])

    submit = SubmitField('Reset Password')

    def validate_email(self, field):
        if not User.query.filter_by(email=field.data).first():
            raise ValidationError('Unknown email address.')


class ChangeEmailRequestForm(FlaskForm):
    email = StringField(
        'Email', validators=[Required(), Length(1, 64), Email()])
    submit = SubmitField('Update Email')
