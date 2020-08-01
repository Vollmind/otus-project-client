from django.urls import path

from client_app import views

urlpatterns = [
    path('', views.main_page_view, name='main_page'),
    path('storage', views.StorageView.as_view(), name='storage'),
    path('storage/add', views.add_storage, name='add_storage'),
    path('storage/<int:storage_id>/delete', views.delete_storage, name='delete_storage'),
    path('storage/<int:storage_id>/hide_show', views.hide_show_storage, name='hide_show_storage'),
    path('storage/refresh', views.refresh_storage_files, name='refresh_storage_files'),
    path('login', views.login, name='login'),

    path('local', views.LocalFiles.as_view(), name='local_files'),
    path('local/<int:file_id>/hide_show', views.hide_show_file, name='hide_show_file'),
    path('local/<int:file_id>/download', views.download_file, name='download_file'),

    path('search', views.search_file, name='search_file'),
    path('outer', views.search_outer_files, name='outer_files')
]
