"""file URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from web.views import account, file, move, share, upload, index

urlpatterns = [
    url(r'^login', account.login, name='login'),
    url(r'^register', account.register, name='register'),
    url(r'^file', file.file, name='file'),
    url(r'^download/(\d+)', file.download, name='download'),
    url(r'^create', file.create, name='create'),
    url(r'^move', move.move, name='move'),
    url(r'^dirlist', move.dirlist, name='dirlist'),
    url(r'^download_files', file.download_files, name='download_files'),
    url(r'^upload_merge', upload.upload_merge, name='upload_merge'),
    url(r'^upload_already', upload.upload_already, name='upload_already'),
    url(r'^upload_chunk', upload.upload_chunk, name='upload_chunk'),
    url(r'^upload', upload.upload, name='upload'),
    url(r'^delete', file.delete, name='delete'),
    url(r'^search', file.search, name='search'),
    url(r'^rename', file.rename, name='rename'),
    url(r'^share_files/(\d+)', share.share_files, name='share_files'),
    url(r'^share', share.share, name='share'),
    url(r'^get_share/(\d+)', share.get_share, name='get_share'),
    url(r'^get_share_files', share.get_share_files, name='get_share_files'),
    url(r'^logout', account.logout, name='logout'),
    url(r'^restore_files', file.restore_files, name='restore_files'),
    url(r'^drag_move', move.drag_move, name='drag_move'),
    url(r'^', index.index, name='index'),
]
