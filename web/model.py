# -*- coding: utf-8 -*-

import time

from web.orm import Model, StringField, BooleanField, FloatField, TextField, BlobField, IntegerField


class User(Model):
    __table__ = 'users'
    uid = IntegerField('uid', primary_key=True)
    name = StringField('name', ddl='varchar(64)')
    email = StringField('email', ddl='varchar(64)')
    password = StringField('password', ddl='char(64)')
    image = StringField('image', ddl='varchar(256)')
    created_at = IntegerField('created_at', default=time.time)
    admin = BooleanField('admin')


# SQL Table
"""
CREATE TABLE users (
    `uid` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(64) NOT NULL,
    `email` VARCHAR(64) NOT NULL,
    `password` CHAR(64) NOT NULL,
    `image` VARCHAR(256) NOT NULL,
    `created_at` BIGINT NOT NULL,
    `admin` INT NOT NULL,

    UNIQUE KEY `name` (`name`),
    UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1000;
"""
