# -*- coding: utf-8 -*-

import aiomysql
import logging

from utils.apis import StandardError


__pool = None


async def create_connection(loop, **kwargs):
    """Create MySql connect pool

    Args:
        loop: (asyncio event loop) Event loop
        host: (str -> 'localhost') The host of MySql instance
        port: (int -> 3306) The port of MySql instance
        user: (str) The username of the database
        password: (str) The password of the user
        db: (str) The database to store data
        charset: (str -> 'utf8') The charset of the database
        autocommit: (bool -> True) Whether enable auto commit
        maxsize: (int -> 16) Minimum sizes of the pool
        minsize: (int -> 1) Maximum sizes of the pool
    """
    logging.info('Creating database connection pool...')
    global __pool
    __pool = await aiomysql.create_pool(
        host=kwargs.get('host', 'localhost'),
        port=kwargs.get('port', 3306),
        user=kwargs['user'],
        password=kwargs['password'],
        db=kwargs['db'],
        charset=kwargs.get('charset', 'utf8'),
        autocommit=kwargs.get('autocommit', True),
        maxsize=kwargs.get('maxsize', 16),
        minsize=kwargs.get('minsize', 1),
        loop=loop
    )


def close():
    """Close MySql connect pool
    """
    global __pool
    logging.info('Close database connection pool')
    __pool.close()
    __pool = None


async def execute(sql, args=None):
    """Execute SQL to MySql

    Args:
        sql: (str) The sql string, use '?' to link an argument
        args: (list/tuple -> ()) The unsafe argument corresponded each '?'

    Returns:
        - int: The primary id of the insert's primary key
        - int: The number of the lines affected
    """
    args = args or ()
    async with __pool.acquire() as conn:
        cursor = await conn.cursor()
        logging.debug(f'Execute SQL: {sql} -> {args}')
        await cursor.execute(sql.replace('?', '%s'), args)
        affect = cursor.rowcount
        primary_id = cursor.lastrowid    # get the primary_id when insert auto_increment key
        logging.debug(f'Affect: {affect} lines')
        await cursor.close()
        conn.close()
    return primary_id, affect


async def select(sql, args=None, size=None):
    """Select the data from MySql

    Args:
        sql: (str) The sql string, use '?' to link an argument
        args: (list/tuple -> ()) The unsafe argument corresponded each '?'
        size: (int -> None) The maximum fetch size

    Returus:
        list of models: The rows selected
    """
    args = args or ()
    async with __pool.acquire() as conn:
        cursor = await conn.cursor(aiomysql.DictCursor)
        await cursor.execute(sql.replace('?', '%s'), args)
        if size:
            result = await cursor.fetchmany(size)
        else:
            result = await cursor.fetchall()
        await cursor.close()
        conn.close()
    return result


class Field(object):
    """
    SQL value type object
    """
    def __init__(self, name, column_type, primary_key, default):
        """Init class Field

        Args:
            name: (str) The column name
            column_type: (str) The sql value type
            primary_key: (bool) Whether the column is the primary key
            default:
                (function) Generate the default value from the function
                (<column_type>-like) Use the default value
        """
        self.name = name
        self.column_type = column_type
        self.primary_key = primary_key
        self.default = default

    def __str__(self):
        return f'<{self.__class__.__name__}, {self.column_type}:{self.name}>'

    __repr__ = __str__


class StringField(Field):
    def __init__(self, name=None, primary_key=False, default=None, ddl='varchar(128)'):
        super().__init__(name, ddl, primary_key, default)


class BooleanField(Field):
    def __init__(self, name=None, default=False):
        super().__init__(name, 'boolean', False, default)


class IntegerField(Field):
    def __init__(self, name=None, primary_key=False, default=0):
        super().__init__(name, 'bigint', primary_key, default)


class FloatField(Field):
    def __init__(self, name=None, primary_key=False, default=0.0):
        super().__init__(name, 'real', primary_key, default)


class TextField(Field):
    def __init__(self, name=None, default=None):
        super().__init__(name, 'text', False, default)


class BlobField(Field):
    def __init__(self, name=None, default=None):
        super().__init__(name, 'blob', False, default)


class ModelMetaclass(type):
    def __new__(mcs, name, bases, attrs):
        if name == 'Model':
            # do nothing
            return type.__new__(mcs, name, bases, attrs)

        table = attrs.get('__table__', None) or name
        mapping = dict()   # column name => Field class
        fields = []        # The list of column names
        primary = None     # Primary key

        logging.info(f'Found model: {name} (table: {table})')

        for (k, v) in attrs.items():
            if isinstance(v, Field):
                logging.info(f'  Found mapping: {k} ==> {v}')
                mapping[k] = v
                if v.primary_key:
                    if primary:
                        raise StandardError(f'Duplicate primary key for field: {k}')
                    primary = k
                else:
                    fields.append(k)
        if not primary:
            raise StandardError('Primary key not found')

        # remove the table columns from attributes
        for k in mapping.keys():
            attrs.pop(k)

        attrs['__mapping__'] = mapping
        attrs['__table__'] = table
        attrs['__primary__'] = primary
        attrs['__fields__'] = fields
        attrs['__model_name__'] = name

        escaped = [f'`{f}`' for f in fields]
        dot_holder = ', '.join(['?'] * len(escaped))
        escaped_holder = ', '.join(escaped)
        set_holder = ', '.join([f'`{mapping.get(f).name or f}`=?' for f in fields])
        attrs['__sql__'] = dict()
        attrs['__sql__']['select'] = f'SELECT `{primary}`, {escaped_holder} FROM {table}'
        attrs['__sql__']['insert'] = f'INSERT INTO `{table}` ({escaped_holder}) VALUES ({dot_holder})'
        attrs['__sql__']['update'] = f'UPDATE `{table}` SET {set_holder} WHERE `{primary}`=?'
        attrs['__sql__']['delete'] = f'DELETE FROM `{table}` WHERE `{primary}`=?'
        attrs['__sql__']['random'] = f'SELECT * FROM `{table}` AS t1 JOIN (SELECT ROUND(RAND() * ((SELECT MAX(id) FROM `{table}`)-(SELECT MIN(id) FROM `{table}`))+(SELECT MIN(id) FROM `{table}`)) AS id) AS t2 WHERE t1.id >= t2.id ORDER BY t1.id'

        return type.__new__(mcs, name, bases, attrs)


class Model(dict, metaclass=ModelMetaclass):
    """
    SQL table model
    """
    def __init__(self, **kw):
        super(Model, self).__init__(**kw)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(f'`{self.__model_name__}` object has no attribute `{key}`')

    def __setattr__(self, key, value):
        self[key] = value

    def get_value(self, key):
        return getattr(self, key, None)

    def get_value_or_default(self, key):
        value = getattr(self, key, None)
        if value is None:
            field = self.__mapping__[key]
            if field.default is not None:
                value = field.default() if callable(field.default) else field.default
                logging.debug(f'Using default value for {key}: {str(value)}')
                setattr(self, key, value)
        return value

    @classmethod
    async def find_all(cls, where=None, args=None, **kw):
        """Find the table rows

        Args:
            where: (str)
                SQL WHERE string, will be appebded after `WHERE`, each '?' correspond an argument
                for example: 'id=?', 'id=? and name=?', 'admin=0'
            args: (list -> None) The argument of the where string
            order_by: (str) SQL ORDER BY string, will be appended after `ORDER BY`
            limit: (int / tuple(int,int)) SQL LIMIT argument, will be appended after `LIMIT`

        Returns:
            list of cls: The rows found
        """
        sql = [cls.__sql__['select']]
        if where is not None:
            sql.append('WHERE')
            sql.append(where)
        args = args or []
        order_by = kw.get('order_by', None)
        if order_by is not None:
            sql.append('ORDER BY')
            sql.append(order_by)
        limit = kw.get('limit', None)
        if limit is not None:
            sql.append('LIMIT')
            if isinstance(limit, int):
                sql.append('?')
                args.append(limit)
            elif isinstance(limit, tuple) and len(limit) == 2:
                sql.append('?, ?')
                args.extend(limit)
            else:
                raise ValueError(f'Invalid limit value: {str(limit)}')
        result = await select(' '.join(sql), args)
        return [cls(**r) for r in result]

    @classmethod
    async def count_item(cls, field, where=None, args=None):
        """Count the number of the rows (not include NULL column)

        Args:
            field: (str) '*' or column name
            where: (str) SQL WHERE string, will be appebded after `WHERE`, each '?' correspond an argument
            args: (list/tuple -> None) The argument of the where string

        Returns:
            - int: The number of the rows
              None
        """
        sql = [f'SELECT count({field}) _num_ FROM `{cls.__table__}`']
        if where is not None:
            sql.append('WHERE')
            sql.append(where)
        result = await select(' '.join(sql), args)
        if len(result) == 0:
            return None
        return result[0]['_num_']

    @classmethod
    async def find(cls, pk):
        """Fetch one item by primary key

        Args:
            pk: (<type of primary key>) The primary key

        Returns:
            - cls: The row found
              None: if the row not found
        """
        result = await select(f'{cls.__sql__["select"]} WHERE `{cls.__primary__}`=?', (pk, ), 1)
        if len(result) == 0:
            return None
        return cls(**result[0])

    @classmethod
    async def random(cls):
        """Fetch a random row from the table

        Returns:
            - cls: The random row
              None: No row selected (if no rows in the table)
        """
        rows = await select(cls.__sql__['random'], [], 1)
        if len(rows) == 0:
            return None
        return cls(**rows[0])

    async def save(self):
        """Add a row to MySql
        """
        args = list(map(self.get_value_or_default, self.__fields__))
        primary_id, rows = await execute(self.__sql__['insert'], args)
        self[self.__primary__] = primary_id
        if rows != 1:
            logging.warning(f'Failed to insert record: affected rows: f{rows}')

    async def update(self):
        """Save the Model to MySql
        """
        args = list(map(self.get_value, self.__fields__))
        args.append(self.get_value(self.__primary__))
        _, rows = await execute(self.__sql__['update'], args)
        if rows != 1:
            logging.warning(f'Failed to update by primary key: affected rows: {rows}')

    async def remove(self):
        """Delete the row from MySql (by primary key)
        """
        args = [self.get_value(self.__primary__)]
        _, rows = await execute(self.__sql__['delete'], args)
        if rows != 1:
            logging.warning(f'Failed to remove by primary key: affected rows: {rows}')
