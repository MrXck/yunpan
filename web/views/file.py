import os
import zipfile
import json

from utils.download import download_file, dabao

from django.conf import settings
from django.http import JsonResponse, FileResponse

from utils.is_repetition import is_repetition
from web import models


def file(request):
    user_id = request.session['user']
    bread = []
    data = json.loads(request.body.decode('utf-8'))
    file_id = data['file_id']
    status = data['status']
    if file_id == 0:
        file_list = models.File.objects.filter(user_id=user_id, parent__isnull=True, status=status, is_delete=0).order_by('-filetype')
    else:
        file_obj = models.File.objects.get(pk=file_id)
        if file_obj is not None:
            bread.insert(0, [file_obj.id, file_obj.filename])
            while file_obj.parent is not None:
                bread.insert(0, [file_obj.parent.id, file_obj.parent.filename])
                file_obj = file_obj.parent
        file_list = models.File.objects.filter(user_id=user_id, parent_id=file_id, status=status, is_delete=0).order_by('-filetype')
    return JsonResponse({'code': 0, 'data': list(file_list.values()), 'bread': list(bread)})


def download(request, file_id):
    user_id = request.session['user']
    file_obj = models.File.objects.get(pk=file_id, user_id=user_id)
    if not file_obj:
        return JsonResponse({'code': 1, 'message': settings.DOWNLOAD_ERROR})
    return download_file(file_obj)


def create(request):
    user_id = request.session['user']
    data = json.loads(request.body.decode('utf-8'))
    file_id = data['file_id']
    dir_name = data['dir_name']
    if file_id == 0:
        file_id = None
    dir_obj = models.File.objects.filter(parent_id=file_id, user_id=user_id, filename=dir_name, filetype=1, status=1)
    if dir_obj:
        return JsonResponse({'code': 1, 'message': settings.CREATE_ERROR})
    models.File(
        filename=dir_name,
        file_hash_name='1',
        filetype=1,
        filepath='1',
        file_hash='1',
        status=1,
        parent_id=file_id,
        user_id=user_id,
    ).save()
    return JsonResponse({'code': 0, 'message': settings.CREATE_SUCCESS})


def delete(request):
    user_id = request.session['user']
    data = json.loads(request.body.decode('utf-8'))
    operation_list = data.get('operationList')
    if len(operation_list) < 1:
        return JsonResponse({'code': 1, 'message': settings.DELETE_ERROR})
    try:
        file_obj_list = models.File.objects.filter(user_id=user_id, pk__in=operation_list, is_delete=0)
        for i in file_obj_list:
            delete_child(i, user_id)
    except ValueError:
        return JsonResponse({'code': 1, 'message': settings.DELETE_ERROR})
    return JsonResponse({'code': 0, 'message': settings.DELETE_SUCCESS})


def search(request):
    user_id = request.session['user']
    data = json.loads(request.body.decode('utf-8'))
    query = data['query']
    file_list = models.File.objects.filter(user_id=user_id, status=1, filename__contains=query, is_delete=0).order_by('-filetype')
    return JsonResponse({'code': 0, 'data': list(file_list.values())})


def rename(request):
    user_id = request.session['user']
    parent_id = request.GET.get('parent_id')
    rename = request.GET.get('rename')
    operationList = request.GET.getlist('operationList')
    if not rename or not operationList or len(operationList) != 1:
        return JsonResponse({'code': 1, 'message': settings.RENAME_ERROR})
    if parent_id == '0':
        parent_id = None
    dir_obj = models.File.objects.filter(user_id=user_id, parent_id=parent_id, filetype=1, status=1, is_delete=0)
    file_obj = models.File.objects.filter(user_id=user_id, parent_id=parent_id, filetype=0, status=1, is_delete=0)
    flag = True
    for obj in file_obj:
        if rename == obj.filename:
            flag = False
            break
    if flag:
        models.File.objects.filter(pk__in=operationList, filetype=0, user_id=user_id, parent_id=parent_id, status=1, is_delete=0).update(filename=rename)
    else:
        return JsonResponse({'code': 1, 'message': settings.RENAME_FILE_ERROR})
    flag = True
    for obj in dir_obj:
        if rename == obj.filename:
            flag = False
            break
    if flag:
        models.File.objects.filter(pk__in=operationList, filetype=1, user_id=user_id, parent_id=parent_id, status=1, is_delete=0).update(filename=rename)
    else:
        return JsonResponse({'code': 1, 'message': settings.RENAME_DIR_ERROR})
    return JsonResponse({'code': 0, 'message': settings.RENAME_SUCCESS})


def delete_child(file_obj, user_id):
    if file_obj.filetype == 1:
        file_obj_list = models.File.objects.filter(user_id=user_id, parent_id=file_obj.id, is_delete=0)
        if file_obj.status == 0:
            for i in file_obj_list:
                delete_child(i, user_id)
            # file_obj.delete()  # 修改成逻辑删除
            file_obj.is_delete = 1
            file_obj.save()
        else:
            file_obj.status = 0
            file_obj.save()
            for i in file_obj_list:
                delete_child(i, user_id)
    else:
        if file_obj.status == 0:
            # os.remove(file_obj.filepath.replace('\u202a', ''))  # 要支持分享就不能真删
            # file_obj.delete()  # 修改成逻辑删除
            file_obj.is_delete = 1
            file_obj.save()
        else:
            file_obj.status = 0
            file_obj.save()


def restore_files(request):
    user_id = request.session['user']
    file_list = request.GET.get('operationList').split(',')
    if not file_list:
        return JsonResponse({'code': 1, 'message': settings.RESTORE_ERROR})
    file_obj_list = models.File.objects.filter(user_id=user_id, pk__in=file_list, status=0, is_delete=0)
    restore_child(file_obj_list, user_id)
    return JsonResponse({'code': 0, 'message': settings.RESTORE_SUCCESS})


def restore_child(li, user_id):
    for obj in li:
        file_obj_list = models.File.objects.filter(user_id=user_id, parent_id=obj.parent_id, filename=obj.filename, is_delete=0)
        if file_obj_list:
            is_repetition(obj, user_id)
        obj.status = 1
        obj.save()
        file_list = models.File.objects.filter(user_id=user_id, parent_id=obj.id, status=0, is_delete=0)
        if file_list:
            restore_child(file_list, user_id)


def download_files(request):
    user_id = request.session['user']
    file_list = request.GET.get('operationList').split(',')
    if not file_list:
        return JsonResponse({'code': 1, 'message': settings.DOWNLOAD_ERROR})
    file_obj_list = models.File.objects.filter(user_id=user_id, status=1, pk__in=file_list)
    file_name = f'1.zip'
    zip_path = os.path.join(os.path.dirname(settings.BASE_DIR), file_name)
    zip_file = zipfile.ZipFile(zip_path, 'w')
    for i in file_obj_list:
        dabao(i, zip_file, user_id)
    zip_file.close()
    f = open(zip_path, 'rb')
    response = FileResponse(f)
    response['content_type'] = "application/octet-stream"
    response['Content-Disposition'] = f'attachment; filename='
    return response
