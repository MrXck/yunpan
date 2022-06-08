from django.http import FileResponse

from web import models


def download_file(file_obj):
    f = open(file_obj.filepath.replace('\u202a', ''), 'rb')
    response = FileResponse(f)
    response['content_type'] = "application/octet-stream"
    response['Content-Disposition'] = f'attachment; filename={file_obj.filename}'
    return response


def dabao(file_obj, zip_file, user_id):
    if file_obj.filetype == 1:
        file_obj_list = models.File.objects.filter(parent=file_obj, user_id=user_id)
        for i in file_obj_list:
            dabao(i, zip_file, user_id=user_id)
    else:
        zip_file.write(file_obj.filepath.replace('\u202a', ''), arcname=file_obj.filename)
