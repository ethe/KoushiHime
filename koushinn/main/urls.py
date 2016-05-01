# -*- coding:utf-8 -*-

from koushinn.main import main
from views import Index, Update, UserInfo, UserList


main.add_url_rule('/', view_func=Index.as_view('index'))
main.add_url_rule('/update/<int:page>', view_func=Update.as_view('update'))
main.add_url_rule('/mupdate', view_func=Update.as_view('mupdate'))
main.add_url_rule('/user/<int:user_id>', view_func=UserInfo.as_view('user'))
main.add_url_rule('/userlist', view_func=UserList.as_view('userlist'))
