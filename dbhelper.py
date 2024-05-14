import sqlite3

database = "student_db.db"


def connect():
    return sqlite3.connect(database)


def getprocess(sql):
    conn = connect()
    cursor = conn.cursor()
    cursor.row_factory = sqlite3.Row
    cursor.execute(sql)
    row = cursor.fetchall()
    conn.close()
    return row

def fetchone(sql):
    conn = connect()
    cursor = conn.cursor()
    cursor.row_factory = sqlite3.Row
    cursor.execute(sql)
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def doprocess(sql):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    return True if cursor.rowcount > 0 else False


def getrecord(table, **kwargs):
    username = kwargs.get("username")
    sql = f"SELECT * FROM {table} WHERE username = '{username}'"
    return getprocess(sql)


def getall(table):
    sql = f"SELECT * FROM {table}"
    return getprocess(sql)


def addrecord(table, **kwargs):
    keys = list(kwargs.keys())
    values = list(kwargs.values())
    flds = "`,`".join(keys)
    data = "','".join(values)
    sql = f"INSERT INTO {table} (`{flds}`) VALUES ('{data}')"
    return doprocess(sql)
    
def get_user_data_by_name(name):
    try:
        sql = f"SELECT * FROM users WHERE name = '{name}'"
        result = fetchone(sql)
        return result
    except Exception as e:
        print(f"Error in get_user_data_by_name: {e}")
        return None

def deleterecord(table, **kwargs):
    sql: str = ""
    for key, value in kwargs.items():
        sql = f"DELETE FROM `{table}` WHERE `{key}`='{value}'"
    return doprocess(sql)


def updaterecord(table, **kwargs):
    keys: list = list(kwargs.keys())
    vals: list = list(kwargs.values())
    flds: list = []
    for i in range(1, len(keys)):
        flds.append(f"`{keys[i]}`='{vals[i]}'")
    dta: str = ",".join(flds)
    sql: str = f"UPDATE `{table}` SET {dta} WHERE `{keys[0]}`='{vals[0]}'"
    return doprocess(sql)
