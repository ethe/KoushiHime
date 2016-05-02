# -*- coding:utf-8 -*-

import os
from koushihime import create_app, db
from koushihime.main.models import WaitingList
from flask.ext.script import Manager, Shell, Server
from flask.ext.migrate import Migrate, MigrateCommand


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
    WaitingList.query.delete()
    print "Done"


if __name__ == '__main__':
    manager.run()
