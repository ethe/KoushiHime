# -*- coding:utf-8 -*-

from moegirl.main import main
from views import Index, Update


main.add_url_rule('/', view_func=Index.as_view('index'))
main.add_url_rule('/update', view_func=Update.as_view('update'))
