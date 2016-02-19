import os
from app import create_app
from flask.ext.script import Manager,Shell
from app.model import User
import app.cron
app=create_app()
manager=Manager(app)
def init_context():
    return dict(app=app)
    manager.add_command('shell',Shell(make_context=init_context))
@manager.command
def test():
    """Run the Unit tests"""
    print 'Prepare To Test'
    import unittest
    tests=unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
if __name__=='__main__':
    manager.run()
