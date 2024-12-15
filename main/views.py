from django.contrib.admin.templatetags.admin_list import pagination
from django.contrib.auth import authenticate, login
from django.core.paginator import Paginator

from main.forms import UserCreationForm
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404

from main.models import Product, Category
from cart.forms import CartAddProductForm

def popular_list(request):
    products = Product.objects.filter(available=True)[:3]
    return render(request, 'index/index.html', {'products': products})


def product_detail(request, slug):
    product = get_object_or_404(Product,
                                slug=slug,
                                available=True)
    cart_product_form = CartAddProductForm
    return render(request, 'product/detail.html',
                  {'product': product, 'cart_product_form': cart_product_form},)


def product_list(request, category_slug=None):
    page = request.GET.get('page', 1)
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    paginator = Paginator(products, 8)
    current_page = paginator.page(int(page))
    if category_slug:
        category = get_object_or_404(Category,
                                     slug=category_slug)
        paginator = Paginator(products.filter(category=category), 8)
        current_page = paginator.page(int(page))
    return render(request,
                  'product/list.html',
                  {'category': category,
                   'categories': categories,
                   'products': current_page,
                   'slug_url': category_slug})


class Register(View):
    template_name = 'registration/register.html'

    def get(self, request):
        context = {
            'form': UserCreationForm(),
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = UserCreationForm(request.POST)

        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('home')
        context = {
            'form': form,
        }
        return render(request, self.template_name, context)
