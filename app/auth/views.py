from flask import render_template, request, url_for, redirect, flash
from flask import current_app
from flask_login import login_user, logout_user, login_required
from flask_login import current_user

from .forms import LoginForm, RegistrationForm, ChangePasswordForm
from .forms import ResetPasswordForm, ResetPasswordRequestForm
from .forms import ChangeEmailRequestForm
from ..models import User
from . import auth
from .. import db
from ..email import send_email


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    # validate_on_submit is from Flask-WTF
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            # login_user is from flask_login
            login_user(user, form.remember_me.data)
            user.ping()
            return redirect(request.args.get('next') or url_for('main.index'))
        else:
            flash('Invalid username or password')

    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    # logout_user is from flask_login
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            username=form.username.data,
            password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(
            user.email,
            'Confirm Your Account',
            'auth/email/confirm',
            user=user,
            token=token)
        if current_app.config['MINIBLOG_ADMIN']:
            send_email(
                current_app.config['MINIBLOG_ADMIN'],
                'New User',
                'mail/new_user',
                user=user)

        flash('A confirmation has been sent to you by email.')
        return redirect(url_for('main.index'))

    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    elif current_user.confirm(token):
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')

    return redirect(url_for('main.index'))


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        if not current_user.confirmed \
           and request.endpoint[:5] != 'auth.' and \
                                       request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    else:
        return render_template('auth/unconfirmed.html')


@auth.route('/confirm/')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(
        current_user.email,
        'Confirm Your Account',
        'auth/email/confirm',
        user=current_user,
        token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))


@auth.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.new_password.data
            db.session.add(current_user)
            db.session.commit()
            flash('Your password has been updated!')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid password!')
    return render_template('auth/change_password.html', form=form)


@auth.route('/reset', methods=['GET', 'POST'])
def reset_password_request():
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))

    form = ResetPasswordRequestForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user:
            token = user.generate_reset_token()
            send_email(
                user.email,
                'Reset Your Password',
                'auth/email/reset_password',
                user=user,
                token=token)
            flash('An Email with instructions to reset your'
                  ' password has been sent to you.')
            return redirect(url_for('main.index'))
        else:
            flash('Email not registered.')
    return render_template('auth/reset_password.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if not current_user.is_anonymous:
        return redirect('main.index')

    form = ResetPasswordForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if not user:
            flash('Email is not registered.')
            return redirect(url_for('main.index'))

        if user.reset_password(token, form.new_password.data):
            flash('Your password has been updated.')
            return redirect(url_for('auth.login'))
        else:
            flash('Your reset password link is invalid or has expired.')
            return redirect(url_for('main.index'))

    return render_template('auth/reset_password.html', form=form)


@auth.route('/change_email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    if current_user.is_anonymous:
        return redirect(url_for('auth.login'))

    form = ChangeEmailRequestForm()

    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered.')
        else:
            token = current_user.generate_change_email_token(form.email.data)
            send_email(
                form.email.data,
                'Change Your Email',
                'auth/email/change_email',
                user=current_user,
                token=token)
            flash('An email with instructions to change your email has been'
                  ' sent to your new Email box.')
            return redirect(url_for('main.index'))

    return render_template('auth/change_email.html', form=form)


@auth.route('/change_email/<token>')
def change_email(token):
    if current_user.is_anonymous:
        return redirect(url_for('auth.login'))

    if current_user.change_email(token):
        flash('Your Email address has been updated.')
    else:
        flash('Your link is invalid or has expired.')

    return redirect(url_for('auth.login'))
