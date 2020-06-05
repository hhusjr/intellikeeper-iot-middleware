from db import conn


def is_active():
    db = conn()
    c = db.cursor()
    rs = c.execute('SELECT v FROM config WHERE k = "active" LIMIT 1')
    res = rs.fetchone()[0] == 'true'
    db.close()
    return res


def activate():
    if is_active():
        return False

    db = conn()
    c = db.cursor()
    c.execute('UPDATE config SET v = "true" WHERE k = "active" LIMIT 1')
    db.commit()
    db.close()

    return True


def deactivate():
    if not is_active():
        return False

    db = conn()
    c = db.cursor()
    c.execute('UPDATE config SET v = "false" WHERE k = "active" LIMIT 1')
    db.commit()
    db.close()

    return True
