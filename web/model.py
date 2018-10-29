# -*- coding: utf-8 -*-

import time

from web.orm import Model, StringField, BooleanField, TextField, IntegerField
from constant import JUDGE_STATUS


class User(Model):
    __table__ = 'users'
    uid = IntegerField('uid', primary_key=True)
    name = StringField('name', ddl='varchar(64)')
    email = StringField('email', ddl='varchar(64)')
    password = StringField('password', ddl='char(128)')
    image = StringField('image', ddl='varchar(256)')
    created_at = IntegerField('created_at', default=time.time)
    admin = IntegerField('admin')


class Problem(Model):
    __table__ = 'problems'
    pid = IntegerField('uid', primary_key=True)
    name = StringField('name', ddl='varchar(64)')
    description = TextField('description')
    input_format = TextField('input_format')
    output_format = TextField('output_format')
    samples = TextField('samples')
    hint = TextField('hint')
    testcases = TextField('testcases')
    provider = StringField('provider', ddl='varchar(64)')
    tags = StringField('tags', ddl='varchar(256)', default='')
    visible = BooleanField('visible', default=True)


class ProblemList(Model):   # Read-only Model
    __table__ = 'problems'
    pid = IntegerField('uid', primary_key=True)
    name = StringField('name', ddl='varchar(64)')
    tags = StringField('tags', ddl='varchar(256)')
    visible = BooleanField('visible')


class Submission(Model):
    __table__ = 'submissions'
    rid = IntegerField('rid', primary_key=True)
    uid = IntegerField('uid', default=2)  # 2 is default user (nobody)
    pid = IntegerField('pid')
    user_name = StringField('user_name', ddl='varchar(64)')
    cid = IntegerField('cid', default=0)  # 0 does not belong to any contest
    time = IntegerField('time', default=time.time)
    code = TextField('code')
    score = IntegerField('score', default=0)
    status = IntegerField('status', default=JUDGE_STATUS.PENDING)
    mini = StringField('mini', ddl='varchar(128)')  # to show the result of each point
    result = TextField('result')  # JSON
    language = StringField('language', ddl='varchar(16)')


class SubmissionList(Model):   # Read-only Model
    __table__ = 'submissions'
    rid = IntegerField('rid', primary_key=True)
    uid = IntegerField('uid')
    pid = IntegerField('pid')
    user_name = StringField('user_name', ddl='varchar(64)')
    cid = IntegerField('cid')
    time = IntegerField('time')
    score = IntegerField('score')
    status = IntegerField('status')
    mini = StringField('mini', ddl='varchar(128)')  # to show the result of each point
    language = StringField('language', ddl='varchar(16)')


# SQL Table
"""
CREATE TABLE users (
    `uid` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(64) NOT NULL,
    `email` VARCHAR(64) NOT NULL,
    `password` CHAR(128) NOT NULL,
    `image` VARCHAR(256) NOT NULL,
    `created_at` BIGINT NOT NULL,
    `admin` INT NOT NULL,

    UNIQUE KEY `name` (`name`),
    UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1000;

CREATE TABLE problems (
    `pid` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(64) NOT NULL,
    `description` TEXT NOT NULL,
    `input_format` TEXT NOT NULL,
    `output_format` TEXT NOT NULL,
    `samples` TEXT NOT NULL,
    `hint` TEXT NOT NULL,
    `testcases` TEXT NOT NULL,
    `provider` VARCHAR(64) NOT NULL,
    `tags` VARCHAR(256) NOT NULL,
    `visible` BOOLEAN NOT NULL,

    KEY `name` (`name`),
    KEY `visible` (`visible`),
    KEY `tags` (`tags`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1000;

CREATE TABLE submissions (
    `rid` INT AUTO_INCREMENT PRIMARY KEY,
    `uid` INT NOT NULL,
    `pid` INT NOT NULL,
    `user_name` VARCHAR(64) NOT NULL,
    `cid` INT NOT NULL,
    `time` INT NOT NULL,
    `code` TEXT NOT NULL,
    `score` INT NOT NULL,
    `status` INT NOT NULL,
    `mini` VARCHAR(128) NOT NULL,
    `result` TEXT NOT NULL,
    `language` VARCHAR(16) NOT NULL,
    
    KEY `uid` (`uid`),
    KEY `pid` (`pid`),
    KEY `cid` (`cid`),
    KEY `score` (`score`),
    KEY `result` (`result`),
    KEY `language` (`language`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1000;
"""
