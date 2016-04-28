import os
basedir=os.path.abspath(os.path.dirname(__file__))
class Config(object):
    def __init__(self):
        super(Config,self).__init__()
        self.GetConfig()
    config={}
    def GetConfig(self):
        for key in self.config:
            setattr(self,key,self.config[key])
class MU_MainConfig(Config):
    def __init__(self):
        super(MU_MainConfig,self).__init__()
        self.GetConfig()
    config={
    'APP_KEY':'563928974',
    'APP_SECRET':'',
    'PUSHEDPREFIX':'PUSHED-',
    'EDITEDPREFIX':'EDITED-',
    'EXPIRETIME':'72*3600',
    'THREEDAYS':259200,
    'Code':'7581b56419b5ea52abc39c0f282716e6',
    }
class MU_FlaskConfig(Config):
    def __init__(self):
        super(MU_FlaskConfig,self).__init__()
        self.GetConfig()
    @staticmethod
    def init_app(app):
        pass
MU_MainConfig=MU_MainConfig()
MU_FlaskConfig=MU_FlaskConfig()