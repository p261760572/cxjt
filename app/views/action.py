# coding=utf-8
import datetime
import json
import os
from io import BytesIO

import flask_login
from flask import Blueprint, jsonify, request, session, send_file, abort, make_response
from flask import send_from_directory

from app import db, app
from app import utils, errors
from app.forms import LoginForm, ChangePwdForm
from app.models import Userinfo, ElecInfo
from app.wesys.fun import FunManager
from . import logger

action = Blueprint('action', __name__, url_prefix='/action')

fun = FunManager()


@action.route('/user/captcha')
def captcha():
    text, image = utils.generate_captcha((100, 38), 20)
    image_bytes = BytesIO()
    image.save(image_bytes, 'JPEG')
    image_bytes.seek(0)

    session['vcode'] = text
    session['vcode:count'] = 0

    return send_file(image_bytes, mimetype='image/jpeg', cache_timeout=0)


@action.route('/user/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        session['vcode:count'] += 1
        if session['vcode:count'] >= 5 or form.captcha.data != session['vcode']:
            return jsonify(errors.error_handler(errors.ERROR_INVALID_VCODE))

        user = Userinfo.query.with_for_update().filter_by(login_name=form.login_name.data).first()
        if user is None:
            user = Userinfo.query.with_for_update().filter_by(mobile=form.login_name.data).first()
            if user is None:
                logger.info(form.login_name.data + '用户不存在')
                return jsonify(errors.error_handler(errors.ERROR_USER_AUTH))

        #if len(user.login_pwd) == 32:
        #    ciphertext = hashlib.md5(utils.tobytes(user.login_pwd + form.captcha.data)).hexdigest()
        #    logger.info(ciphertext)
        #    if ciphertext != form.login_pwd.data:
        #        logger.info(form.login_name.data + '登录密码错误')
        #        return jsonify(errors.error_handler(errors.ERROR_USER_AUTH))
        #else:
        ciphertext = utils.encrypt_password(utils.decrypt_password(form.login_pwd.data), user.salt)
        logger.info(ciphertext)
        if ciphertext != user.login_pwd:
            logger.info(form.login_name.data + '登录密码错误')
            return jsonify(errors.error_handler(errors.ERROR_USER_AUTH))

        user.try_login_times = user.try_login_times + 1
        db.session.flush()
        db.session.commit()

        # 存储会话
        flask_login.login_user(user)

        return jsonify({
            'errcode': 0,
            'data': {
                'userid': user.userid
            }
        })
    else:
        for field in form:
            if field.errors:
                logger.info(field)
                for error in field.errors:
                    logger.info(error)

        return jsonify(errors.error_handler(errors.ERROR_INVALID_FORM_DATA))


@action.route('/user/logout', methods=['GET', 'POST'])
def logout():
    flask_login.logout_user()
    return jsonify({
        'errcode': 0
    })


@action.route('/user/password/change', methods=['GET', 'POST'])
@flask_login.login_required
def change_pwd():
    form = ChangePwdForm()
    if form.validate_on_submit():
        # 验证码
        session['vcode:count'] += 1
        if session['vcode:count'] >= 5 or form.captcha.data != session['vcode']:
            return jsonify(errors.error_handler(errors.ERROR_INVALID_VCODE))

        # 用户
        user = Userinfo.query.with_for_update().get(flask_login.current_user.userid)
        if user is None:
            return jsonify(errors.error_handler(errors.ERROR_INVALID_SESSION))

        #ciphertext = hashlib.md5(utils.tobytes(user.login_pwd + form.captcha.data)).hexdigest()
        #logger.info(ciphertext)
        #if ciphertext != form.login_pwd.data:
        #    logger.info(form.login_name.data + '原密码错误')
        #    return jsonify(errors.error_handler(errors.ERROR_USER_AUTH))

        ciphertext = utils.encrypt_password(utils.decrypt_password(form.login_pwd.data), user.salt)
        logger.info(ciphertext)
        if ciphertext != user.login_pwd:
            logger.info(user.login_name + '原密码错误')
            return jsonify(errors.error_handler(errors.ERROR_PASSWORD))

        user.login_pwd = utils.encrypt_password(utils.decrypt_password(form.new_login_pwd.data), user.salt)
        db.session.commit()

        return jsonify({'errcode': 0})
    else:
        for field in form:
            if field.errors:
                logger.info(field)
                logger.info(field.errors)
                for error in field.errors:
                    logger.info(error)

    return jsonify(errors.error_handler(errors.ERROR_INVALID_FORM_DATA))


ALLOWED_EXTENSIONS = ['.pdf', '.png', '.jpg', '.jpeg', '.gif', '.txt', '.xls', '.xlsx']


def allowed_file(filename):
    return os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS


@action.route('/upload', methods=['POST'])
@flask_login.login_required
def upload_file():
    logger.debug('/action/upload')
    # logger.debug(request.data)

    now = datetime.datetime.now()
    year = now.strftime("%Y")
    mon = now.strftime("%m")
    day = now.strftime("%d")

    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            abort(400)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            abort(400)

        logger.debug(str(file))
        logger.debug(str(file.filename))

        if file:  # and allowed_file(file.filename):
            try:
                serverid = utils.genereate_uuid().replace('+', '-').replace('/', '_')
                filename = serverid + os.path.splitext(file.filename)[1].lower()
                file_path = os.path.join(year, mon, day)
                pathname = os.path.join(app.config['UPLOAD_FOLDER'], file_path)
                if not os.path.exists(pathname):
                    os.makedirs(pathname)

                pathname = os.path.join(pathname, filename)
                print(pathname)
                os.mknod(pathname, mode=0o644)
                file.save(pathname)

                elec_info = ElecInfo(serverid, file.filename, os.path.join(file_path, filename),
                                     flask_login.current_user.login_name)
                db.session.add(elec_info)
                db.session.commit()

                # return jsonify({
                #     'errcode': 0,
                #     'serverid': elec_info.serverid
                # })
                # ie不支持 application/json
                response_data = {
                    'errcode': 0,
                    'serverid': elec_info.serverid
                }
                logger.debug(json.dumps(response_data, ensure_ascii=False))
                response = make_response(json.dumps(response_data, ensure_ascii=False))
                response.headers['Content-Type'] = 'text/plain'
                return response
            except PermissionError as e:
                logger.error(str(e))
                abort(504)
            except FileExistsError as e:
                logger.error(str(e))
                abort(504)
        else:
            abort(400)

    return jsonify(errors.error_handler(errors.ERROR_UPLOAD_FILE))


@action.route('/uploads/<serverid>')
@flask_login.login_required
def uploaded_file(serverid):
    elec_info = ElecInfo.query.filter_by(serverid=serverid).first()
    if elec_info is None:
        return abort(404)
    return send_from_directory(app.config['UPLOAD_FOLDER'], elec_info.file_path)


@action.route('/exports/<path:url>')
@flask_login.login_required
def exported_file(url):
    return send_from_directory(app.config['EXPORT_FOLDER'], url, as_attachment=True)


@action.route('/<path:url>', methods=['GET', 'POST'])
@flask_login.login_required
def do_action(url):
    request_data = request.json
    if request_data is None:
        request_data = {}
    response_data = fun.process('/action/' + url, request.remote_addr, session, request_data)
    logger.debug(json.dumps(response_data, ensure_ascii=False))
    return jsonify(response_data)
