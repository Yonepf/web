from django.shortcuts import render, redirect
from django.contrib import auth, messages
from django.urls import reverse
from django.http import HttpResponseRedirect
from .forms import UserLoginForm, UserRegistrationForm, \
    ProfileForm
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from orders.models import Order, OrderItem
import pandas as pd
from main.models import *
from django.http import HttpResponse
import csv
import io


def login(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = auth.authenticate(username=username,
                                     password=password)
            if user:
                auth.login(request, user)
                return HttpResponseRedirect(reverse('main:product_list'))
    else:
        form = UserLoginForm()
    return render(request, 'users/login.html', {'form': form})


def registration(request):
    if request.method == 'POST':
        form = UserRegistrationForm(data=request.POST)
        if form.is_valid():
            form.save()
            user = form.instance
            auth.login(request, user)
            messages.success(
                request, f'{user.username}, Регистрация подтверждена'
            )
            return HttpResponseRedirect(reverse('users:login'))
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html')


@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(data=request.POST, instance=request.user,
                           files=request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль был изменён')
            return HttpResponseRedirect(reverse('users:profile'))
    else:
        form = ProfileForm(instance=request.user)

    orders = Order.objects.filter(user=request.user).prefetch_related(
        Prefetch(
            'items',
            queryset=OrderItem.objects.select_related('product'),
        )
    ).order_by('-id')
    return render(request, 'users/profile.html',
                  {'form': form,
                   'orders': orders})


def logout(request):
    auth.logout(request)
    return redirect(reverse('main:product_list'))


def export_to_excel(request):
    # Получаем данные из модели
    data = Product.objects.all().values('name', 'category', 'description')

    # Создаем DataFrame из данных
    df = pd.DataFrame(data)

    # Создаем HTTP-ответ с заголовками для скачивания файла
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="data.xlsx"'

    # Записываем DataFrame в Excel
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')

    return response


def export_to_csv(request):
    # Создаем объект StringIO для записи данных
    buffer = io.StringIO()

    # Создаем объект writer для записи в CSV
    writer = csv.writer(buffer)
    # Записываем заголовки
    writer.writerow(['name', 'category', 'description'])

    # Получаем данные из модели и записываем их в CSV
    for obj in Product.objects.all():
        writer.writerow([obj.name, obj.category, obj.description])

    # Получаем содержимое из StringIO и кодируем его в UTF-8
    csv_content = buffer.getvalue().encode('utf-8')
    buffer.close()

    # Создаем HTTP-ответ с заголовками для скачивания файла
    response = HttpResponse(csv_content, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="data.csv"'

    return response
