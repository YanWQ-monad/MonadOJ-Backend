# -*- coding: utf-8 -*-

import time

from web.orm import Model, StringField, BooleanField, TextField, IntegerField


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
"""
