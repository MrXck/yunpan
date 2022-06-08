from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse

import json
from web.forms.account import LoginForm, RegisterForm


def login(request):
    if request.method == 'GET':
        return render(request, 'account/account.html')
    else:
        form = LoginForm(json.loads(request.body.decode('utf-8')))
        if form.is_valid():
            request.session['user'] = form.cleaned_data['user_obj'].id
            return JsonResponse({'code': 0, 'to': reverse('index')})
        error_list = [form.errors[i][0] for i in form.errors]
        return JsonResponse({'code': 1, 'errors': error_list})


def register(request):
    if request.method == 'GET':
        return render(request, 'account/account.html')
    else:
        form = RegisterForm(json.loads(request.body.decode('utf-8')))
        if form.is_valid():
            form.save()
            return JsonResponse({'code': 0, 'to': reverse('login')})
        error_list = [form.errors[i][0] for i in form.errors]
        return JsonResponse({'code': 1, 'errors': error_list})


def logout(request):
    del request.session['user']
    return redirect(reverse('login'))
