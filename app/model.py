from . import r
from werkzeug.security import generate_password_hash,check_password_hash
class User(object):
    def AddUser(self,username,password,role):
        r.hset('user',username,password)
        r.hset('role',username,role)
    def RemUser(self,username):
        r.hdel('user',username)
        r.hdel('role',username)
    def ChangeRole(self,username,role):
        r.hset('role',username,role)
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    @password.setter
    def password(self,password):
        self.password_hash=generate_password_hash(password)
    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)
