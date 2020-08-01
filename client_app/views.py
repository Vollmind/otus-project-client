import hashlib
import mimetypes
import os

import requests
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import redirect, render
from django.views import generic
from rest_framework.decorators import api_view
from rest_framework.response import Response

from client.settings import SERVER_PORT, CLIENT_PORT
from client_app.forms import StorageForm, LoginForm
from client_app.helper import save_setting, get_setting
from client_app.models import Storage, File, Settings
from client_app.serializers import OuterFileSerializer


def get_login_info():
    return {
        'login': get_setting('login'),
        'is_online': get_setting('is_online')
    }


def main_page_view(request):
    return render(
        request,
        'client_app/main_page.html',
        get_login_info()
    )


class ListViewWithLoginInfo(generic.ListView):
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update(get_login_info())
        return context


class StorageView(ListViewWithLoginInfo):
    queryset = Storage.objects.all()
    ordering = ['date']

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['add_form'] = StorageForm()
        return context


def hide_show_storage(request, storage_id):
    storage = Storage.objects.filter(id=storage_id).get()
    storage.hidden = not storage.hidden
    storage.save()
    return redirect('storage')


def add_storage(request):
    if request.method == 'POST':
        form = StorageForm(request.POST)
        if form.is_valid():
            form.save()
    return redirect('storage')


def delete_storage(request, storage_id):
    storage = Storage.objects.filter(id=storage_id).get()
    storage.delete()
    return redirect('storage')


def get_all_files(path):
    result = []
    for elem in os.listdir(path):
        full_path = os.path.join(path, elem)
        if os.path.isdir(full_path):
            result += get_all_files(full_path)
        else:
            result.append(full_path)
    return result


def refresh_storage_files(request):
    for storage in Storage.objects.all():
        for file in get_all_files(storage.path):
            file_obj, _ = File.objects.get_or_create(path=file, storage=storage)
            file_obj.name = os.path.basename(file)
            file_obj.size = os.path.getsize(file)
            with open(file, 'rb') as opened_file:
                file_obj.file_hash = hashlib.sha256(opened_file.read()).hexdigest()
            file_obj.save()
    for file in File.objects.all():
        if not os.path.exists(file.path):
            file.delete()
    return redirect('storage')


def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            save_setting('login', form.cleaned_data['login'])
            save_setting('password', form.cleaned_data['password'])
            save_setting('server', form.cleaned_data['server'])
            try:
                response = requests.post(
                    f'http://{form.cleaned_data["server"]}:{SERVER_PORT}/auth',
                    data={
                        'username': form.cleaned_data['login'],
                        'password': form.cleaned_data['password'],
                    }
                )
                if response.status_code == 200:
                    save_setting('token', response.json()['token'])
                else:
                    return render(
                        request,
                        'client_app/login.html',
                        {
                            'form': form,
                            'error_text': f'Wrong answer from {form.cleaned_data["server"]} : {response.status_code}'
                        }
                    )
                return redirect('storage')
            except requests.exceptions.ConnectionError:
                return render(
                    request,
                    'client_app/login.html',
                    {
                        'form': form,
                        'error_text': f'Cannot connect to {form.cleaned_data["server"]}'
                    }
                )
    else:
        form = LoginForm(initial={'server': get_setting('server'), 'login': get_setting('login')})
    return render(
        request,
        'client_app/login.html',
        {
            'form': form,
        }
    )


# Inner storage
class LocalFiles(ListViewWithLoginInfo):
    queryset = File.objects.all()
    template_name = 'client_app/local_files.html'
    paginate_by = 10

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        return context

    def get_queryset(self):
        filtering = self.request.GET['search'] if 'search' in self.request.GET else ''
        self.queryset = (
            File
            .objects
            .filter(name__contains=filtering)
        )
        return super().get_queryset()


def hide_show_file(request, file_id):
    file = File.objects.filter(id=file_id).get()
    file.hidden = not file.hidden
    file.save()
    return redirect('local_files')


def download_file(request, file_id):
    file = File.objects.get(id=file_id)
    mime_type, _ = mimetypes.guess_type(file.path)

    fl = open(file.path, 'r')
    response = HttpResponse(fl, content_type=mime_type)
    response['Content-Disposition'] = f"attachment; filename={file.name}"
    return response


# Outer storage
def get_outer_storage_file_info(search_str):
    # get online users
    server = get_setting('server')
    token = get_setting('token')
    my_user = get_setting('login')
    if not server or not token:
        return [], 'Try to log in first'
    response = requests.get(f'http://{server}:{SERVER_PORT}/online', headers={'Authorization': f'TOKEN {token}'})
    if response.status_code != 200:
        return [], f'Error connecting to server: {response.status_code}'
    if not response.json() or 'available' not in response.json():
        return [], f'Server returned empty response.'
    found_files = []
    for client in response.json()['available']:
        if client['user'] == my_user:
            continue
        client_response = requests.get(
            f'http://{client["address"]}:{CLIENT_PORT}/search',
            params={'search_str': search_str}
        )
        # ignore errors - if something happened - well, good luck next time
        if client_response.status_code == 200:
            for file in client_response.json()['files']:
                found_file = OuterFileSerializer(data=file)
                if found_file.is_valid():
                    result_dict = found_file.data
                    result_dict['url'] = client['address']
                    found_files.append(result_dict)
    if not found_files:
        return [], 'No files found!'
    return found_files, ''


@api_view(['GET'])
def search_file(request):
    if 'search_str' not in request.GET:
        return HttpResponseServerError('Cannot find parameter "search_str"')
    return_files = []
    for file in File.objects.filter(name__contains=request.GET['search_str']):
        return_files.append(OuterFileSerializer(file).data)
    return Response({
        'files': return_files
    })


def search_outer_files(request):
    if 'search_str' not in request.GET:
        return render(
            request,
            'client_app/outer_files.html',
            {'files_list': [], 'error_text': ''}
        )
    files_list, error = get_outer_storage_file_info(request.GET['search_str'])
    return render(
        request,
        'client_app/outer_files.html',
        {'files_list': files_list, 'error_text': error}
    )


@api_view(['GET'])
def get_file_to_outer(request):
    if 'name' not in request.GET or 'file_hash' not in request.GET:
        return HttpResponseServerError('Required fields "name" and "file_hash" are empty')

    file = File.objects.get_object_or_404(name=request.GET['name'], file_hash=request.GET['file_hash'])
    fl = open(file.path, 'rb')
    response = HttpResponse(fl)
    return response


def load_file_from_outer(ip, name, file_hash):
    response = requests.get(
        f'http://{ip}:{CLIENT_PORT}/getfile',
        params={'name': name, 'hash': file_hash},
        stream=True
    )
    if response.status_code != 200:
        return b'', f'Error while downloading file: {response.status_code}'
    return response.raw, ''


def load_file_and_store(request):
    raw_resp, _ = load_file_from_outer(request.GET['ip'], request.GET['name'], request.GET['file_hash'])
    with open(request.GET['name'], 'wb') as f:
        file_part = raw_resp.read(1024)
        while file_part:
            f.write(file_part)
            file_part = raw_resp.read(1024)
    return redirect('local_files')


def load_file_and_return(request):
    raw_resp, _ = load_file_from_outer(request.GET['ip'], request.GET['name'], request.GET['file_hash'])
    mime_type, _ = mimetypes.guess_type(request.GET['name'])

    response = HttpResponse(raw_resp, content_type=mime_type)
    response['Content-Disposition'] = f"attachment; filename={request.GET['name']}"
    return response
