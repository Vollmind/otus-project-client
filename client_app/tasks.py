import requests
from background_task import background
from background_task.models import Task

from client.settings import SERVER_PORT
from client_app.helper import get_setting, save_setting

_seconds_between_checks = 5


@background(schedule=_seconds_between_checks)
def ping_server():
    server = get_setting('server')
    token = get_setting('token')
    if server and token:
        response = requests.get(f'http://{server}:{SERVER_PORT}/ping', headers={'Authorization': f'TOKEN {token}'})
        if response.status_code == 200:
            save_setting('is_online', '1')
    else:
        save_setting('is_online', '0')


def start_ping():
    Task.objects.filter(verbose_name='ping').delete()
    ping_server(repeat=_seconds_between_checks, verbose_name='ping')
