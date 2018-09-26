# coding=utf-8

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    login_name = StringField('用户名', validators=[DataRequired()])
    login_pwd = PasswordField('密码', validators=[DataRequired()])
    captcha = StringField('验证码', validators=[DataRequired()])


class MLoginForm(FlaskForm):
    mobile = StringField('手机号', validators=[DataRequired()])
    login_pwd = PasswordField('登录密码', validators=[DataRequired()])

class MMobilecodeForm(FlaskForm):
    mobile = StringField('手机号', validators=[DataRequired()])
    vcode = StringField('验证码', validators=[DataRequired()])

class MRegisterForm(FlaskForm):
    mobile = StringField('手机号', validators=[DataRequired()])
    vcode = StringField('验证码', validators=[DataRequired()])
    # mobilecode = StringField('短信验证码', validators=[DataRequired()])
    login_pwd = PasswordField('登录密码', validators=[DataRequired()])
    referral_id = StringField('推荐码')
    nickname = StringField('姓名')


class MResetPwdForm(FlaskForm):
    mobile = StringField('手机号', validators=[DataRequired()])
    vcode = StringField('验证码', validators=[DataRequired()])
    mobilecode = StringField('短信验证码', validators=[DataRequired()])
    login_pwd = PasswordField('新密码', validators=[DataRequired()])


class MChangePwdForm(FlaskForm):
    login_pwd = PasswordField('原密码', validators=[DataRequired()])
    new_login_pwd = PasswordField('新密码', validators=[DataRequired()])
    new_login_pwd2 = PasswordField('确认新密码', validators=[DataRequired()])
    vcode = StringField('验证码', validators=[DataRequired()])


class ChangePwdForm(FlaskForm):
    login_pwd = PasswordField('原密码', validators=[DataRequired()])
    new_login_pwd = PasswordField('新密码', validators=[DataRequired()])
    new_login_pwd2 = PasswordField('确认新密码', validators=[DataRequired()])
    captcha = StringField('验证码', validators=[DataRequired()])