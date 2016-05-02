# -*- coding:utf-8 -*-

from koushihime.main import main
from views import Index, Update, UserInfo, UserList, EditProfile, OperationLog, ManualUpdate, KeywordBan


update_view = Update.as_view('update')
edit_profile_view = EditProfile.as_view('editprofile')
operation_log_view = OperationLog.as_view('operationlog')
ban_keyword_view = KeywordBan.as_view('ban')


main.add_url_rule('/', view_func=Index.as_view('index'))

main.add_url_rule('/update/<int:page>', view_func=update_view)
main.add_url_rule('/update', view_func=update_view,
                             defaults={'page': 1})

main.add_url_rule('/mupdate', view_func=ManualUpdate.as_view('mupdate'))

main.add_url_rule('/user/<username>', view_func=UserInfo.as_view('user'))

main.add_url_rule('/userlist', view_func=UserList.as_view('userlist'))

main.add_url_rule('/edit_profile/<username>', view_func=edit_profile_view)
main.add_url_rule('/edit_profile', view_func=edit_profile_view,
                                   defaults={'username': None})

main.add_url_rule('/log/<int:page>', view_func=operation_log_view)
main.add_url_rule('/log', view_func=operation_log_view,
                          defaults={'page': 1})

main.add_url_rule('/ban/<int:page>', view_func=ban_keyword_view)
main.add_url_rule('/ban', view_func=ban_keyword_view,
                          defaults={'page': 1})
