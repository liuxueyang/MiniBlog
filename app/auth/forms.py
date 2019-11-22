#! coding=utf-8

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms import ValidationError
from wtforms.validators import DataRequired, Email, Length, Regexp, EqualTo
from ..models import User


class LoginForm(FlaskForm):
    email = StringField(
        'Email', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')


class RegistrationForm(FlaskForm):
    email = StringField(
        'Email', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField(
        'Username',
        validators=[
            DataRequired(), Length(1, 64),
            Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                   'Username must have only letters'
                   ', numbers, dots or '
                   'underscores. And must start with letters.')
        ])
    password = PasswordField(
        'Password',
        validators=[DataRequired(),
                    EqualTo('password1', 'Passwords must match.')])
    password1 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Register')

    @staticmethod
    def validate_email(field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    @staticmethod
    def validate_username(field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username is taken.')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('old password', validators=[DataRequired()])
    new_password = PasswordField(
        'new password',
        validators=[
            DataRequired(), EqualTo('new_password1', 'Passwords must match.')
        ])
    new_password1 = PasswordField('confirm password',
                                  validators=[DataRequired()])
    submit = SubmitField('Submit')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField(
        'Email', validators=[DataRequired(), Length(1, 64), Email()])
    submit = SubmitField('Reset Password')


class ResetPasswordForm(FlaskForm):
    email = StringField(
        'Email', validators=[DataRequired(), Length(1, 64), Email()])
    new_password = PasswordField(
        'new password',
        validators=[
            DataRequired(), EqualTo('new_password1', 'Passwords must match.')
        ])
    new_password1 = PasswordField('confirm password',
                                  validators=[DataRequired()])

    submit = SubmitField('Reset Password')

    @staticmethod
    def validate_email(field):
        if not User.query.filter_by(email=field.data).first():
            raise ValidationError('Unknown email address.')


class ChangeEmailRequestForm(FlaskForm):
    email = StringField(
        'Email', validators=[DataRequired(), Length(1, 64), Email()])
    submit = SubmitField('Update Email')
