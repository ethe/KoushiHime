# -*- coding:utf-8 -*-

from flask import render_template


def configure_errorhandlers(app):
    """Configures the error handlers."""

    @app.errorhandler(403)
    def forbidden_page(error):
        return render_template("error/forbidden_page.html"), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("error/page_not_found.html"), 404

    @app.errorhandler(500)
    def server_error_page(error):
        return render_template("error/server_error.html"), 500
