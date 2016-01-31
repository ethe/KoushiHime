import os
basedir=os.path.abspath(os.path.dirname(__file__))
class MU_MainConfig(object):
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
    
    def GetConfig(self):
        for key in self.config:
            setattr(self,key,self.config[key])
MU_MainConfig=MU_MainConfig()
