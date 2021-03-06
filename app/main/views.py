from flask import render_template, redirect, url_for, flash
from flask import abort, request, current_app
from flask_login import login_required, current_user

from . import main
from .. import db
from .forms import EditProfileForm, EditProfileAdminForm, PostForm, CommentForm
from ..models import User, Role, Post, Permission, Comment
from ..decorators import admin_required

# This implementation is for test and exercise. Leave it alone.
# @main.route('/', methods=['GET', 'POST'])
# def index():
#     form = NameForm()

#     if form.validate_on_submit():
#         user = User.query.filter_by(username=form.name.data).first()

#         if user is None:
#             user = User(username=form.name.data)
#             db.session.add(user)
#             session['known'] = False
#             app = current_app._get_current_object()

#             if app.config['FLASKY_ADMIN']:
#                 send_email(
#                     app.config['FLASKY_ADMIN'],
#                     'New User',
#                     'mail/new_user',
#                     user=user)
#         else:
#             session['known'] = True

#         old_name = session.get('name')

#         if old_name is not None and old_name != form.name.data:
#             flash('Looks like you have changed your name!')

#         session['name'] = form.name.data
#         form.name.data = ''
#         return redirect(url_for('.index'))

#     return render_template(
#         'index.html',
#         current_time=datetime.utcnow(),
#         name=session.get('name'),
#         form=form,
#         known=session.get('known', False))


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        abort(404)

    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user.html', user=user, posts=posts)


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


@main.route('/edit_profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)

    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))

    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me

    return render_template('edit_profile.html', form=form)


@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()

    if current_user.can(
            Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post = Post(
            body=form.body.data, author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('.index'))

    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page,
        per_page=current_app.config['MINIBLOG_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template(
        'index.html', form=form, posts=posts, pagination=pagination)


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()

    if form.validate_on_submit():
        comment = Comment(
            body=form.body.data,
            post=post,
            author=current_user._get_current_object())
        db.session.add(comment)
        flash('评论发表成功啦～')
        return redirect(url_for('.post', id=post.id, page=-1))

    page = request.args.get('page', 1, type=int)

    if -1 == page:
        page = (post.comments.count() - 1
                ) / current_app.config['MINIBLOG_COMMENTS_PER_PAGE'] + 1

    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page,
        per_page=current_app.config['MINIBLOG_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items

    return render_template(
        'post.html',
        posts=[post],
        form=form,
        comments=comments,
        pagination=pagination)


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)

    if current_user != post.author and \
       not current_user.can(Permission.ADMINISTER):
        abort(403)

    form = PostForm()

    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        flash('The post has been updated.')
        return redirect(url_for('.post', id=post.id))

    form.body.data = post.body
    return render_template('edit_post.html', form=form)
