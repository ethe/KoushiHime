# -*- coding:utf-8 -*-

import os
import sys
import pickle
from flask.ext.script import Manager, Shell, Server
from flask.ext.migrate import Migrate, MigrateCommand
from koushihime import create_app, db
from koushihime.auth.models import Role, User


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return {"app": app}
manager.add_command("shell", Shell(make_context=make_shell_context))


manager.add_command('db', MigrateCommand)


server = Server(host="0.0.0.0", port=5000, use_reloader=True)
manager.add_command("runserver", server)


@manager.command
def init():
    "Initialize environment and database"

    print 'Initialize environment\n'
    pickle.dump({}, open('./environment', 'w'))
    print 'Done'
    print '\nInitialize db'
    os.system("python manage.py db init")
    print '\nPrepare to migrate db'
    os.system("python manage.py db migrate")
    print '\nUpgrade db'
    os.system("python manage.py db upgrade")
    print '\nInitialize roles'
    Role.init_roles()
    print '\nAll clear'


@manager.command
def reset():
    "Reset app, remove database and reset environment"

    sys.stdout.write("Do you want to clean the database? [Y/n]  ")
    result = None
    while result not in ["Y", "n", ""]:
        result = raw_input()
    if result == "Y":
        os.system("rm -r migrations && rm *.sqlite")
        print "All clear"
    else:
        pickle.dump({}, open('./environment', 'w'))
        print "Reset environment done"


@manager.option('-p', '--password', dest='password', help="Administrator's password", required=True)
@manager.option('-e', '--email', dest='email', help="Administrator's email", required=True)
def admin(email, password):
    "Initialize administrator acount"

    User(email=email, password=password, role_id=1, username="admin").save()
    print "Done"


@manager.option('-v', '--value', dest='value', help="Environment value", required=True)
@manager.option('-k', '--key', dest='key', help="Environment key", required=True)
def env(key, value):
    "Set Environment"

    from koushihime.utils import Env
    app_env = Env()
    app_env.set(key, value)
    print "Done"


if __name__ == '__main__':
    manager.run()
