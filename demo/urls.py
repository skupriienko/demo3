from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.conf.urls import include, url
from django.contrib import admin

import news.views
import news.api_views
from news.views import add_like, add_dislike


urlpatterns = [
    path('api/v1/news/', news.api_views.NewsList.as_view()),
    path('api/v1/news/new', news.api_views.NewsCreate.as_view()),
    path('api/v1/news/<int:id>/', news.api_views.NewsRetrieveUpdateDestroy.as_view()),
    path('api/v1/news/<int:id>/stats', news.api_views.NewsStats.as_view()),

    path('admin/', admin.site.urls),
    path('news/<int:id>/', news.views.show, name='show-news'),
    path('cart/', news.views.cart, name='shopping-cart'),
    path('', news.views.index, name='news-list'),

    path(r'^(?P<slug>S+)/addlike/$', add_like, name='add_like'),
    path(r'^(?P<slug>S+)/adddislike/$', add_dislike, name='add_dislike'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
