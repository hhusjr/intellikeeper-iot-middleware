import subprocess
import os

MAIN_FILE_PATH = '/tmp/intellikeeper-base/cmake-build-debug/intellikeeper_base'
OUT_FILE_PATH = '/home/pi/data/.base.output'


def call(data):
    if os.path.exists(OUT_FILE_PATH):
        os.remove(OUT_FILE_PATH)

    proc = subprocess.Popen([MAIN_FILE_PATH],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE)

    proc.stdin.write(bytes(data, encoding='utf-8'))

    proc.communicate()

    if not os.path.exists(OUT_FILE_PATH):
        return None

    with open(OUT_FILE_PATH, 'r') as f:
        content = f.read()

    return content
