# -*- coding:utf-8 -*-

from koushinn.auth import auth
from views import Login, Logout


auth.add_url_rule('/login', view_func=Login.as_view('login'))
auth.add_url_rule('/logout', view_func=Logout.as_view('logout'))
