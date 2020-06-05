import reader
import activator
import tag
from multiprocessing import Process


def handle_handshake(request):
    return {
        'status': 'hello'
    }


def handle_activate(request):
    if not activator.activate():
        return {
            'success': False
        }
    Process(target=reader.handshake_to_all).start()
    return {
        'success': True
    }


def handle_deactivate(request):
    return {
        'success': activator.deactivate()
    }


def handle_new_tag(request):
    new_id = tag.detect_new_tag_tid()
    if new_id is not None:
        tag.insert_new_tag(new_id)

    return {
        'new_tag_tid': new_id
    }


def handle_find_tag(request):
    addr = tag.tid2addr(request['tid'])
    tag.handshake(addr)

    return {
        'success': True
    }


def handle_activate_tag(request):
    tag.activate(request['tid'])

    return {
        'success': True
    }


def handle_deactivate_tag(request):
    tag.deactivate(request['tid'])

    return {
        'success': True
    }


def handle_get_tags_info(request):
    return tag.get_tags_info()


def handle_get_readers_pos(request):
    return reader.get_readers_pos()


def handle_get_track(request):
    return tag.get_track(request['tid'])


handler_mapping = {
    'handshake': handle_handshake,
    'activate': handle_activate,
    'deactivate': handle_deactivate,
    'new_tag': handle_new_tag,
    'find_tag': handle_find_tag,
    'activate_tag': handle_activate_tag,
    'deactivate_tag': handle_deactivate_tag,
    'get_tags_info': handle_get_tags_info,
    'get_readers_pos': handle_get_readers_pos,
    'get_track': handle_get_track
}
