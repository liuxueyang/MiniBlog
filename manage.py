#!/usr/bin/env python

import os
from app import create_app, db
from app.models import User, Role, Post
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
from werkzeug.security import generate_password_hash

app = create_app(os.getenv('MINIBLOG_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Post=Post)


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


@manager.command
def clear_users():
    """Clear user database"""
    users = User.query.all()

    for u in users:
        db.session.delete(u)

    db.session.commit()


@manager.command
def add_admin():
    """Add Administrator to Database"""
    admin_role = Role.query.filter_by(name='Administrator').first()
    if admin_role:
        admin_user = User(
            email=os.getenv('MINIBLOGY_ADMIN'),
            username='Admin',
            confirmed=True)
        admin_user.password_hash = generate_password_hash(
            os.getenv('MINIBLOGY_ADMIN_PASSWORD'))
        db.session.add(admin_user)
        db.session.commit()


@manager.command()
def insert_roles():
    """Add Roles to database"""
    Role.insert_roles()


if __name__ == '__main__':
    manager.run()
