from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect

from news.models import News, ShoppingCart

def index(request):
    context = {
        'news_s': News.objects.all(),
    }
    return render(request, 'news/news_list.html', context)

def show(request, id):
    context = {
        'news': News.objects.get(id=id),
    }
    return render(request, 'news/news.html', context)

def cart(request):
    context = {
        'items': [],
        'subtotal': 1.0,
        'tax_rate': int(ShoppingCart.TAX_RATE * 100.0),
        'tax_total': 2.0,
        'total': 3.0,
    }
    return render(request, 'news/cart.html', context)

def add_like(request, slug):
    try:
        news = get_object_or_404(News, slug=slug)
        news.likes += 1
        news.save()
    except ObjectDoesNotExist:
        return Http404
    return redirect(request.GET.get('next', '/'))


def add_dislike(request, slug):
    try:
        news = get_object_or_404(News, slug=slug)
        news.dislikes += 1
        news.save()
    except ObjectDoesNotExist:
        return Http404
    return redirect(request.GET.get('next', '/'))
