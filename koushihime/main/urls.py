# -*- coding:utf-8 -*-

from koushihime.main import main
from views import Index, Update, UserInfo, UserList, EditProfile, OperationLog


main.add_url_rule('/', view_func=Index.as_view('index'))
main.add_url_rule('/update/<int:page>', view_func=Update.as_view('update'))
main.add_url_rule('/update', view_func=Update.as_view('update'),
                             defauts={'page': 1})
main.add_url_rule('/mupdate', view_func=Update.as_view('mupdate'))
main.add_url_rule('/user/<username>', view_func=UserInfo.as_view('user'))
main.add_url_rule('/userlist', view_func=UserList.as_view('userlist'))
main.add_url_rule('/edit_profile/<username>', view_func=EditProfile.as_view('editprofile'))
main.add_url_rule('/edit_profile', view_func=EditProfile.as_view('editprofile'),
                                   defauts={'username': None})
main.add_url_rule('/log/<int:page>', view_func=OperationLog.as_view('operationlog'))
main.add_url_rule('/log', view_func=Update.as_view('update'),
                          defauts={'page': 1})
