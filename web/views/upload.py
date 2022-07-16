import os
import uuid

from django.http import JsonResponse
from django.conf import settings

from web import models


def upload_merge(request):
    dir_path = os.path.dirname(settings.BASE_DIR)
    file_hash_name = request.GET.get('HASH')
    file_hash = request.GET.get('file_hash')
    file_name = request.GET.get('filename')
    parent_id = request.GET.get('parent_id')
    if parent_id == '0':
        parent_id = None
    user_id = request.session['user']
    uuid_name = str(uuid.uuid4())
    file_hash_path = os.path.join(dir_path, file_hash_name)
    file_path = os.path.join(dir_path, uuid_name + '.' + file_name.split('.')[-1])
    file_list = os.listdir(file_hash_path)
    count = int(request.GET.get('count'))
    suffix = '.' + file_list[0].split('.')[-1]
    with open(file_path, 'wb') as f:
        for i in range(1, count + 1):
            merge_filename = f'{file_hash_name}_{i}{suffix}'
            merge_filepath = f'{os.path.join(file_hash_path, merge_filename)}'
            with open(merge_filepath, 'rb') as f1:
                for j in f1:
                    f.write(j)
            os.remove(merge_filepath)
    os.rmdir(file_hash_path)
    models.File(
        filename=file_name,
        file_hash_name=uuid_name,
        filetype=0,
        filepath=file_path,
        file_hash=file_hash,
        status=1,
        parent_id=parent_id,
        user_id=user_id,
    ).save()
    return JsonResponse({'code': 0, 'message': settings.UPLOAD_SUCCESS})


def upload_already(request):
    parent_id = request.GET.get('parent_id')
    filename = request.GET.get('filename')
    file_hash = request.GET.get('file_hash')
    user_id = request.session['user']
    if parent_id == '0':
        parent_id = None
    if models.File.objects.filter(user_id=user_id, parent_id=parent_id, filetype=0, filename=filename, status=1, is_delete=0):
        return JsonResponse({'code': 1, 'message': settings.UPLOAD_ERROR})
    file_obj_list = models.File.objects.filter(filetype=0, file_hash=file_hash)
    if file_obj_list:
        file_obj = file_obj_list.first()
        models.File(
            filename=file_obj.filename,
            file_hash_name=file_obj.file_hash_name,
            filetype=0,
            filepath=file_obj.filepath,
            file_hash=file_obj.file_hash,
            status=1,
            parent_id=parent_id,
            user_id=user_id,
        ).save()
        return JsonResponse({'code': 2, 'message': settings.UPLOAD_SUCCESS})
    if not request.GET.get('HASH'):
        return JsonResponse({'code': 0})
    dir_path = os.path.dirname(settings.BASE_DIR)
    hash_dir = os.path.join(dir_path, request.GET.get('HASH'))
    file_list = []
    if os.path.exists(hash_dir):
        file_list = os.listdir(hash_dir)
    return JsonResponse({'code': 0, 'fileList': file_list})


def upload_chunk(request):
    dir_path = os.path.dirname(settings.BASE_DIR)
    for i in request.FILES:
        hash_dir = os.path.join(dir_path, i.split('_')[0])
        if not os.path.exists(hash_dir):
            try:
                os.mkdir(hash_dir)
            except FileExistsError:
                pass
        file_path = os.path.join(hash_dir, i)
        with open(file_path, 'wb') as f:
            for j in request.FILES.get(i):
                f.write(j)
    return JsonResponse({'code': 0})


def upload(request):
    dir_path = os.path.dirname(settings.BASE_DIR)
    parent_id = request.GET.get('parent_id')
    file_hash = request.GET.get('file_hash')
    HASH = str(uuid.uuid4())
    if parent_id == '0':
        parent_id = None
    user_id = request.session['user']
    for i in request.FILES:
        suffix = '.' + i.split('.')[-1]
        path = os.path.join(dir_path, HASH + suffix)
        if models.File.objects.filter(filename=i, parent_id=parent_id, filetype=0, user_id=user_id, is_delete=0):
            return JsonResponse({'code': 1, 'message': settings.UPLOAD_ERROR})
        models.File(
            filename=i,
            file_hash_name=HASH,
            filetype=0,
            filepath=path,
            file_hash=file_hash,
            status=1,
            parent_id=parent_id,
            user_id=user_id,
        ).save()
        with open(path, 'wb') as f:
            for j in request.FILES.get(i):
                f.write(j)
    return JsonResponse({'code': 0, 'message': settings.UPLOAD_SUCCESS})
