import re

from web import models


def is_repetition(obj, user_id):
    repl = re.search('[(](\d+)[)][.]', obj.filename)
    if repl:
        obj.filename = re.sub('[(](\d+)[)][.]', f'({int(repl.group(1)) + 1}).', obj.filename, 1)
    else:
        split_str = obj.filename.rsplit(".", 1)
        obj.filename = f'{split_str[0]}(1).{split_str[1]}'
    file_obj = models.File.objects.filter(user_id=user_id, filename=obj.filename, parent_id=obj.parent_id, is_delete=0).first()
    if file_obj:
        is_repetition(obj, user_id)
