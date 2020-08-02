from django.urls import path
from django.contrib.auth import views as auth_views

from client_app import views

urlpatterns = [
    path('', views.main_page_view, name='main_page'),
    path('storage', views.StorageView.as_view(), name='storage'),
    path('storage/add', views.add_storage, name='add_storage'),
    path('storage/<int:storage_id>/delete', views.delete_storage, name='delete_storage'),
    path('storage/<int:storage_id>/hide_show', views.hide_show_storage, name='hide_show_storage'),
    path('storage/refresh', views.refresh_storage_files, name='refresh_storage_files'),
    path('login', views.login_on_server, name='login'),

    path('local', views.LocalFiles.as_view(), name='local_files'),
    path('local/<int:file_id>/hide_show', views.hide_show_file, name='hide_show_file'),
    path('local/<int:file_id>/download', views.download_file, name='download_file'),

    path('search', views.search_file, name='search_file'),
    path('outer', views.search_outer_files, name='outer_files'),
    path('getfile', views.get_file_to_outer, name='getfile'),
    path('outer/load', views.load_file_and_store, name='load_outer'),
    path('outer/get', views.load_file_and_return, name='get_outer'),

    path('auth', views.OurLoginView.as_view(template_name = 'client_app/auth.html'), name='auth'),
    path('logout', auth_views.LogoutView.as_view(next_page='/auth'), name='logout'),
    path(
        'changepass',
        views.OurChangePassView.as_view(
            template_name='client_app/change_password.html',
            success_url='logout'
        ),
        name='changepass'
    ),
]
