import json

from django.conf import settings
from django.db.models import Q
from django.http import JsonResponse


from web import models


def move(request):
    user_id = request.session['user']
    dic = json.loads(request.body.decode('utf-8'))
    parent_id = dic.get('parent_id')
    if parent_id == 0:
        parent_id = None
    file_list = models.File.objects.filter(~Q(id=parent_id), user_id=user_id, pk__in=dic.get('operationList'), is_delete=0)
    parent_obj = models.File.objects.filter(pk=parent_id, is_delete=0).first()
    for i in file_list:
        if i.parent is None and parent_obj:
            while parent_obj.parent is not None:
                if parent_obj.parent_id == i.id:
                    return JsonResponse({'code': 1, 'message': settings.MOVE_TO_SELF_ERROR})
                parent_obj = parent_obj.parent
        while i.parent is not None:
            if i.parent_id == parent_id:
                return JsonResponse({'code': 1, 'message': settings.MOVE_TO_SELF_ERROR})
            i = i.parent
    file_list.update(parent_id=parent_id)
    return JsonResponse({'code': 0, 'message': settings.MOVE_SUCCESS})


def drag_move(request):
    operationList = request.GET.getlist('operationList')
    if not operationList:
        return JsonResponse({'code': 1, 'message': settings.MOVE_ERROR})
    parent_id = request.GET.get('parent_id')
    user_id = request.session['user']
    try:
        operationList = operationList[0].split(',')
    except:
        operationList = operationList
    if parent_id in operationList:
        return JsonResponse({'code': 1, 'message': settings.MOVE_TO_SELF_ERROR})
    models.File.objects.filter(pk__in=operationList, user_id=user_id, is_delete=0).update(parent_id=parent_id)
    return JsonResponse({'code': 0, 'message': settings.MOVE_SUCCESS})


def dirlist(request):
    bread = []
    user_id = request.session['user']
    data = json.loads(request.body.decode('utf-8'))
    parent_id = data['parent_id']
    if parent_id == 0:
        file_list = models.File.objects.filter(user_id=user_id, parent__isnull=True, filetype=1, status=1, is_delete=0)
    else:
        file_obj = models.File.objects.get(pk=parent_id)
        bread.insert(0, [file_obj.id, file_obj.filename])
        while file_obj.parent is not None:
            bread.insert(0, [file_obj.parent.id, file_obj.parent.filename])
            file_obj = file_obj.parent
        file_list = models.File.objects.filter(user_id=user_id, parent_id=parent_id, filetype=1, status=1, is_delete=0)
    return JsonResponse({'code': 0, 'data': list(file_list.values()), 'bread': list(bread)})
