import MySQLdb
from datetime import datetime

MYSQL_DATABASE_HOST = None
MYSQL_DATABASE_USER = None
MYSQL_DATABASE_PASSWORD = None
MYSQL_DATABASE_DB = None

FIELD_TYPE = {
    0: 'DECIMAL',
    1: 'TINY',
    2: 'SHORT',
    3: 'LONG',
    4: 'FLOAT',
    5: 'DOUBLE',
    6: 'NULL',
    7: 'TIMESTAMP',
    8: 'LONGLONG',
    9: 'INT24',
    10: 'DATE',
    11: 'TIME',
    12: 'DATETIME',
    13: 'YEAR',
    14: 'NEWDATE',
    15: 'VARCHAR',
    16: 'BIT',
    246: 'NEWDECIMAL',
    247: 'INTERVAL',
    248: 'SET',
    249: 'TINY_BLOB',
    250: 'MEDIUM_BLOB',
    251: 'LONG_BLOB',
    252: 'BLOB',
    253: 'VAR_STRING',
    254: 'STRING',
    255: 'GEOMETRY'
}


def execute(sql, *args, **kwargs):
    result = list()
    db = MySQLdb.Connect(MYSQL_DATABASE_HOST, MYSQL_DATABASE_USER, MYSQL_DATABASE_PASSWORD, MYSQL_DATABASE_DB)
    cursor = db.cursor()
    cursor.execute(sql)
    field_descriptions = cursor.description
    for row in cursor.fetchall():
        row_result = dict()
        for cell in row:
            field_description = field_descriptions[row.index(cell)]
            if field_description[1] == 1:
                row_result[field_description[0]] = not not cell
            else:
                row_result[field_description[0]] = cell
        result.append(row_result)
    db.close()
    return result


def execute_fetch_one(sql, *args, **kwargs):
    row_result = dict()
    db = MySQLdb.Connect(MYSQL_DATABASE_HOST, MYSQL_DATABASE_USER, MYSQL_DATABASE_PASSWORD, MYSQL_DATABASE_DB)
    cursor = db.cursor()
    cursor.execute(sql)
    field_descriptions = cursor.description
    row = cursor.fetchone()
    for cell in row:
        field_description = field_descriptions[row.index(cell)]
        if field_description[1] == 1:
            row_result[field_description[0]] = not not cell
        else:
            row_result[field_description[0]] = cell
    return row_result


def execute_update(sql, *args, **kwargs):
    db = MySQLdb.Connect(MYSQL_DATABASE_HOST, MYSQL_DATABASE_USER, MYSQL_DATABASE_PASSWORD, MYSQL_DATABASE_DB)
    cursor = db.cursor()
    result = cursor.execute(sql)
    db.commit()
    db.rollback()
    db.close()
    return result


class NoTableError(Exception):
    pass


def gen_condition(k, v):
    condition = None

    if type(v) == str or type(v) == unicode:
        condition = "%s='%s'" % (k, str(v))
    if type(v) == int or type(v) == long:
        condition = "%s=%d" % (k, v)
    if type(v) == datetime:
        condition = "%s='%s'" % (k, v.strftime("%Y-%m-%d %H:%M:%S") if v else None)
    if type(v) == bool:
        condition = "%s=%d" % (k, 1 if v else 0)
    if v is None:
        condition = "%s IS NULL" % (k, )
    return condition


def gen_update_condition(k, v):
    condition = None

    if type(v) == str or type(v) == unicode:
        condition = "%s='%s'" % (k, str(v))
    if type(v) == int or type(v) == long:
        condition = "%s=%d" % (k, v)
    if type(v) == datetime:
        condition = "%s='%s'" % (k, v.strftime("%Y-%m-%d %H:%M:%S") if v else None)
    if type(v) == bool:
        condition = "%s=%d" % (k, 1 if v else 0)
    if v is None:
        condition = "%s=null" % (k, )
    return condition


def gen_insert_val(v):
    val = None
    if type(v) == str or type(v) == unicode:
        val = "'%s'" % (str(v))
    if type(v) == int:
        val = "%d" % v
    if type(v) == datetime:
        val = "'%s'" % datetime(v).isoformat()
    if type(v) == bool:
        val = "%r" % v
    return val


class Model:
    def __init__(self, **kwargs):
        self.__dict__ = kwargs

    @property
    def m_id(self):
        return self.__dict__.get(self.Meta.primary)

    def save(self):
        if hasattr(self, self.Meta.primary):
            sql = "UPDATE %s SET %s WHERE %s=%d" % (self.Meta.table,
                                                    ", ".join([gen_update_condition(k, self.__dict__.get(k)) for k in
                                                               self.__dict__.keys()]),
                                                    self.Meta.primary,
                                                    self.__dict__[self.Meta.primary])
            result = execute_update(sql)
            if result:
                self.__dict__ = self.__class__.find_one(**self.__dict__).__dict__
            return self
        else:
            cols = ", ".join(self.__dict__.keys())
            vals = ", ".join([gen_insert_val(self.__dict__[k]) for k in self.__dict__.keys()])
            sql = "INSERT INTO {0:s} ({1:s}) values ({2:s})".format(self.Meta.table, cols, vals)
            result = execute_update(sql)
            if result:
                self.__dict__ = self.__class__.find_one(**self.__dict__).__dict__
            return self

    def delete(self):
        pass

    @classmethod
    def find_by_id(cls, one_id):
        meta = cls.Meta
        table = meta.table
        if table is None:
            raise NoTableError
        primary = meta.primary
        sql = "SELECT * FROM {0:s} AS t WHERE t.{1:s}={2:d}".format(table, primary, one_id)
        print(sql)
        result = execute(sql)
        if len(result) > 0:
            model = cls(**result[0])
            return model
        else:
            return None

    @classmethod
    def find_by_ids(cls, ids):
        pass

    @classmethod
    def find(cls, sql=None, **kwargs):
        pass

    @classmethod
    def find_one(cls, **kwargs):
        meta = cls.Meta
        table = meta.table
        if table is None:
            raise NoTableError
        sql = "SELECT * FROM %s AS t " % (table,)
        if len(kwargs) > 0:
            sql += "WHERE "
        condition_str = " AND ".join([gen_condition(k, kwargs[k]) for k in kwargs])
        sql += condition_str
        print(sql)
        result = execute(sql)
        if len(result) > 0:
            model = cls(**result[0])
            return model
        else:
            return None

    class Meta:
        table = None
        primary = "id"

