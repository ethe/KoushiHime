# -*- coding:utf-8 -*-

from moegirl.auth import auth
from views import Login, Logout, Block


auth.add_url_rule('/login', view_func=Login.as_view('login'))
auth.add_url_rule('/logout', view_func=Logout.as_view('logout'))
auth.add_url_rule('/blocked', view_func=Block.as_view('block'))
