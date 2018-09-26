# coding=utf-8
from flask import request, jsonify

from app import app, login_manager, errors
from app.models import Userinfo

logger = app.logger


@app.before_request
def before_request():
    logger.debug(request.url)


@app.after_request
def after_request(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    return response


@app.teardown_appcontext
def teardown_appcontext(exception):
    logger.debug('teardown_appcontext')


@login_manager.user_loader
def user_loader(userid):
    return Userinfo.query.get(userid)


@login_manager.unauthorized_handler
def unauthorized_handler():
    # return 'Unauthorized'
    return jsonify(errors.error_handler(errors.ERROR_INVALID_SESSION))


from app.views.action import action

app.register_blueprint(action)
