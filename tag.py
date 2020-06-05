import pipe
from db import conn
from multiprocessing import Process


def activate(tid):
    addr = tid2addr(tid)

    db = conn()
    c = db.cursor()
    c.execute('UPDATE tag SET is_active = 1 WHERE addr = ?', (addr, ))
    db.commit()
    db.close()

    handshake(addr)


def deactivate(tid):
    addr = tid2addr(tid)

    db = conn()
    c = db.cursor()
    c.execute('UPDATE tag SET is_active = 0 WHERE addr = ?', (addr, ))
    db.commit()
    db.close()


def detect_new_tag_tid():
    data = pipe.call('1')
    if data is None:
        return None
    return data.upper()


TAG_ADDR_OFFSET = 0x20
TAG_ADDR_MAX = 0x50


def tid2addr(tid):
    # 一般以16进制八位字符串给出
    tid = int('0x{}'.format(tid), 16)

    # 转换为地址，不存在则为0xFF
    db = conn()
    c = db.cursor()
    rs = c.execute('SELECT addr FROM tag WHERE tid = ?', (tid, )).fetchone()
    db.close()

    return rs[0]


def insert_new_tag(tid):
    # 一般以16进制八位字符串给出
    tid = int('0x{}'.format(tid), 16)

    # 首先获取所有地址集合，计算集合的MEX值作为新地址
    db = conn()
    c = db.cursor()
    rs = c.execute('SELECT addr FROM tag').fetchall()
    a = set()
    for row in rs:
        a.add(row[0])
    addr = -1
    for i in range(TAG_ADDR_OFFSET, TAG_ADDR_MAX + 1):
        if i not in a:
            addr = i
            break
    db.close()

    # 然后插入
    db = conn()
    c = db.cursor()
    c.execute('INSERT INTO tag (tid, addr, is_active) VALUES (?, ?, 0)', (tid, addr)).fetchall()
    db.commit()
    db.close()

    # 更改新标签地址
    pipe.call('3 {}'.format(addr))

    # 发出确认声音
    Process(target=handshake, args=(addr, )).start()

    return True


def handshake(addr):
    pipe.call('2 {}'.format(addr))


def get_tags_info():
    db = conn()
    c = db.cursor()
    rs = c.execute('SELECT tid, is_active, is_online FROM tag')
    rows = rs.fetchall()
    db.close()

    # 获取所有标签
    tags = []
    for row in rows:
        tmp = {
            'tid': '{0:08X}'.format(row[0]),
            'is_active': row[1],
            'is_online': row[2],
            'last_online': None,
            'position_ok': False,
        }

        db = conn()
        c = db.cursor()
        rs = c.execute(
            'SELECT record_time FROM record WHERE tid = ? ORDER BY record_time DESC LIMIT 1',
            (row[0],))
        cur_row = rs.fetchone()
        if cur_row is not None:
            tmp['last_online'] = cur_row[0]
        db.close()

        db = conn()
        c = db.cursor()
        rs = c.execute('SELECT x, y, record_time FROM record WHERE tid = ? AND position_ok = 1 ORDER BY record_time '
                       'DESC LIMIT 1', (row[0], ))
        pos = rs.fetchone()
        if pos is not None:
            tmp['position_ok'] = True
            tmp['x'] = pos[0]
            tmp['y'] = pos[1]
            tmp['last_distance_measure_time'] = pos[2]
        db.close()

        tags.append(tmp)

    return tags


def get_track(tid):
    tid = int('0x{}'.format(tid), 16)
    db = conn()
    c = db.cursor()
    rs = c.execute('SELECT x, y, record_time FROM record '
                   'WHERE tid = ? AND position_ok = 1 '
                   'ORDER BY record_time DESC '
                   'LIMIT 50',
                   (tid, ))
    result = []
    for row in reversed(rs.fetchall()):
        result.append({
            'x': row[0],
            'y': row[1],
            'record_time': row[2]
        })

    db.close()

    return result
