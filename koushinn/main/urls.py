# -*- coding:utf-8 -*-

from koushinn.main import main
from views import Index, Update


main.add_url_rule('/', view_func=Index.as_view('index'))
main.add_url_rule('/update/<int:page>', view_func=Update.as_view('update'))
main.add_url_rule('/mupdate', view_func=Update.as_view('mupdate'))
