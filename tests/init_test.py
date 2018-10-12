# -*- coding: utf-8 -*-

import web.coroweb as coroweb
from aiohttp import web
import web.orm as orm
import config

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


async def init_test(loop):
    """Initialize test environment
    """
    patch_config()
    await init(loop)
