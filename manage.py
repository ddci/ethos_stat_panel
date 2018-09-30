#!/usr/bin/env python
import csv
import os
import subprocess

from config import Config

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Shell, Server
from redis import Redis
from rq import Connection, Queue, Worker
from celery import Celery

from application import create_app, db
from application.models import Role, User, LocationFieldPanel

from receiver import create_app as create_app_receiver

if os.path.exists('config.env'):
    print('Importing environment from .env file')
    for line in open('config.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[str(var[0])] = str(var[1].replace("\"", ""))


def make_app(app_type):
    if app_type == 'web':
        return create_app(os.getenv('FLASK_CONFIG') or 'default')
    elif app_type == 'receiver':
        return create_app_receiver(os.getenv('FLASK_CONFIG') or 'default')


# app = create_app(os.getenv('FLASK_CONFIG') or 'default')
#
# app_receiver = create_app_receiver(os.getenv('FLASK_CONFIG') or 'default')

manager = Manager(make_app)
migrate = Migrate(make_app, db)

manager.add_option('-a', '--app_type', dest='app_type', required=True)


# celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'], backend=app.config['CELERY_RESULT_BACKEND'],
#                 include=['application.celery.tasks'])
# celery.conf.update(app.config)


def make_shell_context():
    return dict(app=make_app, db=db, User=User, Role=Role)


manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

server = Server(host="0.0.0.0", port=8080)
manager.add_command("runserver", server)


def setup_general():
    """Runs the set-up needed for both local development and production.
       Also sets up first admin user."""
    Role.insert_roles()
    admin_query = Role.query.filter_by(name='Administrator')
    if admin_query.first() is not None:
        if User.query.filter_by(username=Config.ADMIN_USERNAME).first() is None:
            user = User(
                password=Config.ADMIN_PASSWORD,
                username=Config.ADMIN_USERNAME,
                is_otp_seen=True)
            db.session.add(user)
            db.session.commit()
            if os.path.exists("token/DELETE_ME.txt"):
                os.remove("token/DELETE_ME.txt")
            with open("token/DELETE_ME.txt", "w") as token_file:
                token_file.write(user.otp_secret)
            print('Added administrator {}'.format(user.full_name()))


@manager.command
def test():
    """Run the unit tests."""
    import unittest

    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


@manager.command
def recreate_db():
    """
    Recreates a local database. You probably should not use this on
    production.
    """
    db.drop_all()
    db.create_all()
    db.session.commit()


@manager.option(
    '-n',
    '--number-users',
    default=10,
    type=int,
    help='Number of each model type to create',
    dest='number_users')
def add_fake_data(number_users):
    """
    Adds fake data to the database.
    """
    User.generate_fake(count=number_users)


@manager.command
def setup_dev():
    """Runs the set-up needed for local development."""
    setup_general()


@manager.command
def setup_prod():
    """Runs the set-up needed for production."""
    setup_general()


# @manager.command
# def run_worker():
#     """Initializes a slim rq task queue."""
#     listen = ['default']
#     conn = Redis(
#         host=app.config['RQ_DEFAULT_HOST'],
#         port=app.config['RQ_DEFAULT_PORT'],
#         db=0,
#         password=app.config['RQ_DEFAULT_PASSWORD'])
#
#     with Connection(conn):
#         worker = Worker(map(Queue, listen))
#         worker.work()


@manager.command
def format():
    """Runs the yapf and isort formatters over the project."""
    isort = 'isort -rc *.py app/'
    yapf = 'yapf -r -i *.py app/'

    print('Running {}'.format(isort))
    subprocess.call(isort, shell=True)

    print('Running {}'.format(yapf))
    subprocess.call(yapf, shell=True)


@manager.option(
    '-f',
    '--filename',
    default='miner_names.csv',
    type=str,
    help='Import cvs into db',
    dest='filename')
def import_cvs(filename):
    reader = csv.DictReader(open(filename, 'r'))
    dict_list = []
    for _line in reader:
        dict_list.append(_line)
    for v in dict_list:
        worker = v.get('worker')
        number = v.get('number')

        loc = LocationFieldPanel(
            hostname=worker,
            number=number
        )
        if LocationFieldPanel.query.filter_by(hostname=worker).first() is None:
            # session.query(User).filter_by(id=123).update({"name": u"Bob Marley"})
            db.session.add(loc)
            db.session.commit()
        else:
            loc = LocationFieldPanel.query.filter_by(hostname=worker).first()
            loc.hostname = str(worker)
            loc.number = str(number)
            db.session.add(loc)
            db.session.commit()

        print('Added cvs worker {} number {} into db'.format(loc.hostname, loc.number))


@manager.option(
    '-f',
    '--filename',
    default='miner_names.csv',
    type=str,
    help='Export cvs from db',
    dest='filename')
def export_cvs(filename):
    myData = [["worker", "number"]]

    all_rigs = LocationFieldPanel.query.all()
    for rig in all_rigs:
        myData.append([rig.hostname, rig.number])

    myFile = open(filename, 'w')
    with myFile:
        writer = csv.writer(myFile)
        writer.writerows(myData)

    print("Writing complete")
    pass


if __name__ == '__main__':
    manager.run()
