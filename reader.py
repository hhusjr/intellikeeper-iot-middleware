import pipe
from db import conn
import time
import measure
import numpy as np
import requests
import json
from settings import URL_DEAD_TAGS, BASE_ID, KEY_DEAD_TAGS


def fetch_readers():
    db = conn()
    c = db.cursor()
    rs = c.execute('SELECT id, addr, pos_x, pos_y FROM reader').fetchall()
    result = []
    for row in rs:
        result.append({
            'id': row[0],
            'addr': row[1],
            'pos_x': row[2],
            'pos_y': row[3]
        })
    db.close()
    return result


def handshake_to_all():
    readers = fetch_readers()
    for reader in readers:
        pipe.call('0 {} {}'.format(reader['id'], reader['addr']))


def read_tags(reader_id, reader_addr, tag_addrs=None):
    if tag_addrs is None:
        tag_addrs = []

    # 将数字转换为字符串
    tag_addrs = [str(tag_addr) for tag_addr in tag_addrs]

    result = pipe.call('4 {} {} {} {}'.format(reader_id, reader_addr, len(tag_addrs), ' '.join(tag_addrs)))
    if result is None:
        return None

    return [int(x) for x in result.split()[1:]]


def perform_duty():
    # 循环获取距离数据
    while True:
        time.sleep(1.5)

        # 获取待查tag列表
        tags = []
        db = conn()
        c = db.cursor()
        rs = c.execute('SELECT tid, addr FROM tag')
        for item in rs.fetchall():
            tags.append({
                'tid': item[0],
                'addr': item[1]
            })
        db.close()

        # 获取阅读器
        readers = []
        db = conn()
        c = db.cursor()
        rs = c.execute('SELECT id, addr, pos_x, pos_y FROM reader')
        for item in rs.fetchall():
            readers.append({
                'id': item[0],
                'addr': item[1],
                'pos_x': item[2],
                'pos_y': item[3]
            })
        db.close()

        info = {tag['tid']: [] for tag in tags}
        available_tags = set()

        # 用每个阅读器分别扫描所有TAG
        for reader in readers:
            read_data = read_tags(reader['id'], reader['addr'], [tag['addr'] for tag in tags])
            if read_data is None:
                continue

            if len(read_data) != len(tags):
                continue

            for i in range(len(read_data)):
                if read_data[i] > 200:
                    continue
                available_tags.add(tags[i]['tid'])
                info[tags[i]['tid']].append((reader['pos_x'], reader['pos_y'], measure.get_distance(read_data[i])))

            time.sleep(0.5)

        # 扫描结束后，计算坐标
        for available_tag in available_tags:
            db = conn()
            c = db.cursor()
            try:
                ax = measure.get_axis(info[available_tag])
                print(ax[0], ax[1])
                c.execute('INSERT INTO record (tid, x, y, position_ok, record_time) VALUES (?, ?, ?, ?, ?)',
                          (available_tag, ax[0], ax[1], 1, int(time.time())))
            except np.linalg.LinAlgError as e:
                print(e)
                c.execute('INSERT INTO record (tid, x, y, position_ok, record_time) VALUES (?, ?, ?, ?, ?)',
                          (available_tag, -1, -1, 0, int(time.time())))
            db.commit()
            db.close()

        print('loop ok')


def periodic_check():
    while True:
        time.sleep(10)

        # 首先获取服务器端基站是否激活，如果没激活则待检查集合为空
        db = conn()
        c = db.cursor()
        rs = c.execute('SELECT v FROM config WHERE k = "active" LIMIT 1')
        base_active = rs.fetchone()[0]
        db.close()

        # 获取所有需要被检查的TAG，以及所有TAG
        tags_need_check = set()
        tags = []
        db = conn()
        c = db.cursor()
        rs = c.execute('SELECT tid, is_active, is_online FROM tag')
        for item in rs.fetchall():
            # 只有当基站和TAG都被激活，并且TAG在线的情况下，才需要被检查
            if base_active and item[1] and item[2]:
                tags_need_check.add(item[0])
            # 添加进tags
            tags.append(item[0])
        db.close()

        # 获取所有当前在线的TAG
        db = conn()
        c = db.cursor()
        cur = int(time.time())
        rs = c.execute('SELECT tid FROM record WHERE record_time >= ?', (cur - 10, ))
        available_tags = set(x[0] for x in rs.fetchall())
        db.close()

        # 逐个设置TAG是否online
        db = conn()
        c = db.cursor()
        for tag in tags:
            is_online = 1 if tag in available_tags else 0
            c.execute('UPDATE tag SET is_online = ? WHERE tid = ?', (is_online, tag))
        db.commit()
        db.close()

        # 计算所有TAG与可用TAG的差集
        dead_tags = tags_need_check - available_tags

        # 如果差集不为空，向推送给服务器
        if len(dead_tags) == 0:
            continue
        requests.post(URL_DEAD_TAGS, {
            'dead_tags': json.dumps(list('{0:08X}'.format(tag).upper() for tag in dead_tags)),
            'base_id': BASE_ID,
            'key': KEY_DEAD_TAGS
        })


def get_readers_pos():
    db = conn()
    c = db.cursor()
    rs = c.execute('SELECT pos_x, pos_y FROM reader')
    tmp = []
    for row in rs.fetchall():
        tmp.append({
            'x': row[0],
            'y': row[1]
        })
    return tmp
