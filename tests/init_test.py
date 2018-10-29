# -*- coding: utf-8 -*-

import web.coroweb as coroweb
from aiohttp import web
import web.orm as orm
import config
import shutil
import os

patched_config = {
    'debug': False,
    'web': {
        'host': 'localhost',
        'port': 35327
    },
    'db': {
        'host': 'localhost',
        'port': 3306,
        'user': 'monadoj_test',
        'password': 'MONADOJ TEST',
        'db': 'monadoj_test'
    },
    'session': {
        'max_age': 90000,
        'secret': 'SECRET KEY'
    },
    'secret': {
        'password_salt': 'PASSWORD SALT'
    },
    'judge': {
        'testcases_path': 'test_temp/testcases'
    }
}

runner = None


async def init_database_content():
    """Initialize MySql database data (create empty tables)
    """
    await orm.execute('DROP TABLE IF EXISTS `users`')
    await orm.execute('''
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
    ''')

    await orm.execute('DROP TABLE IF EXISTS `problems`')
    await orm.execute('''
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
    ''')

    await orm.execute('DROP TABLE IF EXISTS `submissions`')
    await orm.execute('''
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
    ''')


async def init(loop):
    """Start web service for test
    """
    global runner
    await orm.create_connection(loop, **config.configs.db)
    await init_database_content()
    runner = web.AppRunner(coroweb.app, access_log_format='%a "%r" %s %bB %Dus')
    await runner.setup()
    site = web.TCPSite(runner, config.configs.web.host, config.configs.web.port)
    await site.start()


async def close_test():
    """Close web service
    """
    global runner
    if runner is not None:
        await runner.cleanup()
    orm.close()


def patch_config():
    """Mock default settings
    """
    config.configs = config.to_dict(patched_config)


def make_test_dir():
    if os.path.exists('test_temp'):
        shutil.rmtree('test_temp')
    os.mkdir('test_temp')
    os.mkdir('test_temp/testcases')


async def init_test(loop):
    """Initialize test environment
    """
    make_test_dir()
    await init(loop)

patch_config()
