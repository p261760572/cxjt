# coding=utf-8
import base64
import hashlib
import os
import random
import string
import uuid

from flask_login import UserMixin
from six import text_type
from sqlalchemy import func
from sqlalchemy import text

from app import db
from app import utils


class Userinfo(db.Model, UserMixin):
    __table__name = 'userinfo'
    userid = db.Column(db.Integer, db.Sequence('seq_userid'), primary_key=True)
    login_name = db.Column(db.String(32), unique=True)
    mobile = db.Column(db.String(11), unique=True)
    login_pwd = db.Column(db.String(256))
    user_level = db.Column(db.String(1), default='0')
    nickname = db.Column(db.String(64))
    actual_name = db.Column(db.String(64))
    inst_id = db.Column(db.String(8))
    referral_code = db.Column(db.String(11))
    try_login_times = db.Column(db.Integer)
    province = db.Column(db.String(2))
    status = db.Column(db.String(1))
    city = db.Column(db.String(2))
    district = db.Column(db.String(2))
    department = db.Column(db.String(64))
    id_card_no = db.Column(db.String(19))
    salt = db.Column(db.String(32))

    def __init__(self, login_name, mobile, login_pwd, inst_id, referral_code, nickname):
        self.login_name = login_name  # or utils.genereate_random_string(20, 20)
        self.mobile = mobile
        self.nickname = nickname
        self.salt = utils.genereate_random_string(8, 32)
        self.login_pwd = utils.encrypt_password(utils.decrypt_password(login_pwd), self.salt)
        self.inst_id = inst_id
        self.referral_code = referral_code
        self.try_login_times = 0

    def __repr__(self):
        return '<Userinfo %r>' % self.login_name

    @property
    def is_active(self):
        return self.status == '1'

    def get_id(self):
        return text_type(self.userid)


class Mobilecode(db.Model):
    __table__name = 'mobilecode'
    mobile = db.Column(db.String(11))
    mobilecode = db.Column(db.String(6))
    rec_id = db.Column(db.Integer, db.Sequence('seq_rec_id'), primary_key=True)
    oper_in = db.Column(db.String(1))
    proc_st = db.Column(db.String(1))
    created_time = db.Column(db.DateTime)
    expired_time = db.Column(db.DateTime)
    ip = db.Column(db.String(15))

    def __init__(self, mobile, oper_in, ip):
        self.mobile = mobile
        self.mobilecode = ''
        self.oper_in = oper_in
        self.proc_st = '1'
        self.ip = ip


class ElecInfo(db.Model):
    __table__name = 'elec_info'
    serverid = db.Column(db.String(128))
    filename = db.Column(db.String(1024))
    file_path = db.Column(db.String(1024))
    rec_id = db.Column(db.Integer, db.Sequence('seq_rec_id'), primary_key=True)
    oper_in = db.Column(db.String(1))
    proc_st = db.Column(db.String(1))
    created_by = db.Column(db.String(32))
    created_time = db.Column(db.DateTime, default=func.now())

    def __init__(self, serverid, filename, file_path, created_by):
        self.serverid = serverid
        self.filename = filename
        self.file_path = file_path
        self.oper_in = '0'
        self.proc_st = '0'
        self.created_by = created_by


'''
class FunConfig(db.Model):
    __tablename__ = 'fun_config'
    url = db.Column(db.String(256), primary_key=True)
    module_name = db.Column(db.String(128))
    param_list = db.Column(db.String(512))
    exec_type = db.Column(db.String(1))
    order_no = db.Column(db.Integer, primary_key=True)
    test = db.Column(db.String(128))
    comments = db.Column(db.String(200))
    input = db.Column(db.String(32))
#     test_input = db.Column(db.String(128))
 
    def __init__(self):
        pass
    
    
class FunInfo(db.Model):
    __table__name = 'fun_info'
    fun_id = db.Column(db.Integer, primary_key=True)
    fun_name = db.Column(db.String(64))
    url = db.Column(db.String(128))
    op = db.Column(db.String(1))
    log_flag = db.Column(db.String(1))
    
    def __init__(self):
        pass
        
    
class SqlInfo(db.Model):
    __table__name = 'sql_info'
    sql_id = db.Column(db.String(128), primary_key=True)
    sql_name = db.Column(db.String(512))
    sql_stmt = db.Column(db.String(4000))
    
    def __init__(self):
        self.stmt  = json.loads(self.sql_stmt)
        

class DataRule(db.Model):
    __tablename__ = 'data_rule'
    data_rule_id = db.Column(db.Integer, primary_key=True)
    res_code = db.Column(db.String(32))
    data_rule = db.Column(db.String(4000))
    rule_name = db.Column(db.String(128))
    op = db.Column(db.String(1))
    
    def __init__(self):
        self.rule  = json.loads(self.data_rule)
'''
