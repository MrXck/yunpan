import datetime
import json

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.conf import settings

from utils.is_repetition import is_repetition
from utils.share import get_check_code
from web import models


def share(request):
    user_id = request.session['user']
    dic = json.loads(request.body.decode('utf-8'))
    password = get_check_code(4)
    share_obj = models.Share.objects.create(
        creator_id=user_id,
        period=dic.get('period'),
        password=password
    )
    share_obj.files.add(*dic.get('operationList'))
    url = f"{request.scheme}://{request.get_host()}{reverse('get_share', args=(share_obj.id, ))}"
    return JsonResponse({'code': 0, 'url': url, 'password': password})


def get_share(request, share_id):
    now = datetime.datetime.now()
    share_obj = models.Share.objects.filter(pk=share_id).first()
    if not share_obj or share_obj.create_time + datetime.timedelta(minutes=share_obj.period) < now:
        return render(request, 'error.html')
    if request.method == 'GET':
        return render(request, 'share.html')
    url = f"{request.scheme}://{request.get_host()}{reverse('share_files', args=(share_id,))}"
    session_share_id = request.session.get('share_id')
    if str(session_share_id) == str(share_id):
        return JsonResponse({'code': 0, 'url': url})
    share_obj = models.Share.objects.filter(pk=share_id).first()
    dic = json.loads(request.body.decode('utf-8'))
    password = dic.get('password')
    if password == share_obj.password:
        request.session['share_id'] = share_id
        return JsonResponse({'code': 0, 'url': url})
    else:
        return JsonResponse({'code': 1, 'error': settings.SHARE_PASSWORD_ERROR})


def share_files(request, share_id):
    session_share_id = request.session.get('share_id')
    if str(session_share_id) != str(share_id):
        return redirect(reverse('get_share', args=(share_id, )))
    if request.method == 'GET':
        return render(request, 'share_file.html')
    bread = []
    data = json.loads(request.body.decode('utf-8'))
    file_id = data['file_id']
    if file_id == 0:
        share_obj = models.Share.objects.filter(pk=share_id).first()
        file_list = share_obj.files.all()
    else:
        file_obj = models.File.objects.get(pk=file_id)
        if file_obj is not None:
            bread.insert(0, [file_obj.id, file_obj.filename])
            while file_obj.parent is not None:
                bread.insert(0, [file_obj.parent.id, file_obj.parent.filename])
                file_obj = file_obj.parent
        file_list = models.File.objects.filter(parent_id=file_id).order_by('-filetype')
    return JsonResponse({'code': 0, 'data': list(file_list.values()), 'bread': list(bread)})


def get_share_files(request):
    user_id = request.session['user']
    dic = json.loads(request.body.decode('utf-8'))
    parent_id = dic.get('parent_id')
    if parent_id == 0:
        parent_id = None
    file_list = models.File.objects.filter(pk__in=dic.get('operationList'))
    li = []
    for file_obj in file_list:
        obj = models.File(
            filename=file_obj.filename,
            file_hash_name=file_obj.file_hash_name,
            filetype=file_obj.filetype,
            filepath=file_obj.filepath,
            file_hash=file_obj.file_hash,
            status=1,
            parent_id=parent_id,
            user_id=user_id,
        )
        file_obj_list = models.File.objects.filter(user_id=user_id, parent_id=obj.parent_id, filename=obj.filename)
        if file_obj_list:
            is_repetition(obj, user_id)
        li.append(obj)
    models.File.objects.bulk_create(li, batch_size=200)
    return JsonResponse({'code': 0})
