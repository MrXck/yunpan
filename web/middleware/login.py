from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin


class Login(MiddlewareMixin):
    # 请求来了 自动调用下面这个方法
    def process_request(self, request):
        path = ['/login', '/register']
        if request.path.startswith('/static'):
            return None
        if request.session.get('user'):
            return None
        if request.path not in path:
            return redirect(reverse('login'))
