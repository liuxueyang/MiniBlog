from flask import render_template, redirect, url_for, flash
from flask import abort, request, current_app
from flask_login import login_required, current_user

from . import main
from .. import db
from .forms import EditProfileForm, EditProfileAdminForm, PostForm, CommentForm
from ..models import User, Role, Post, Permission, Comment
from ..decorators import admin_required


@main.route('/user/<username>')
def user(username):
    _user = User.query.filter_by(username=username).first()

    if not _user:
        abort(404)

    posts = _user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user.html', user=_user, posts=posts)


@main.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()

    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))

    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me

    return render_template('edit_profile.html', form=form)


@main.route('/edit_profile/<int:_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(_id):
    _user = User.query.get_or_404(_id)
    form = EditProfileAdminForm(user=_user)

    if form.validate_on_submit():
        _user.email = form.email.data
        _user.username = form.username.data
        _user.confirmed = form.confirmed.data
        _user.role = Role.query.get(form.role.data)
        _user.name = form.name.data
        _user.location = form.location.data
        _user.about_me = form.about_me.data
        db.session.add(_user)
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=_user.username))

    form.email.data = _user.email
    form.username.data = _user.username
    form.confirmed.data = _user.confirmed
    form.role.data = _user.role_id
    form.name.data = _user.name
    form.location.data = _user.location
    form.about_me.data = _user.about_me

    return render_template('edit_profile.html', form=form)


@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()

    if current_user.can(
            Permission.WRITE_ARTICLES) and form.validate_on_submit():
        _post = Post(
            body=form.body.data, author=current_user._get_current_object())
        db.session.add(_post)
        return redirect(url_for('.index'))

    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page,
        per_page=current_app.config['MINIBLOG_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template(
        'index.html', form=form, posts=posts, pagination=pagination)


@main.route('/post/<_id>', methods=['GET', 'POST'])
def post(_id):
    _post = Post.query.get_or_404(_id)
    form = CommentForm()

    if form.validate_on_submit():
        comment = Comment(
            body=form.body.data,
            post=_post,
            author=current_user._get_current_object())
        db.session.add(comment)
        flash('评论发表成功啦～')
        return redirect(url_for('.post', id=_post.id, page=-1))

    page = request.args.get('page', 1, type=int)

    if -1 == page:
        page = (_post.comments.count() - 1
                ) / current_app.config['MINIBLOG_COMMENTS_PER_PAGE'] + 1

    pagination = _post.comments.order_by(Comment.timestamp.asc()).paginate(
        page,
        per_page=current_app.config['MINIBLOG_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items

    return render_template(
        'post.html',
        posts=[_post],
        form=form,
        comments=comments,
        pagination=pagination)


@main.route('/edit/<int:_id>', methods=['GET', 'POST'])
@login_required
def edit(_id):
    _post = Post.query.get_or_404(_id)

    if current_user != _post.author and \
       not current_user.can(Permission.ADMINISTER):
        abort(403)

    form = PostForm()

    if form.validate_on_submit():
        _post.body = form.body.data
        db.session.add(_post)
        flash('The post has been updated.')
        return redirect(url_for('.post', id=_post.id))

    form.body.data = _post.body
    return render_template('edit_post.html', form=form)
