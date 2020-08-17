from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView, CreateAPIView, \
    RetrieveUpdateDestroyAPIView, GenericAPIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from news.serializers import NewsSerializer, NewsStatSerializer
from news.models import News

class NewsPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 100

class NewsList(ListAPIView):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filter_fields = ('id',)
    search_fields = ('title', 'author_name')
    pagination_class = NewsPagination

    def get_queryset(self):
        on_sale = self.request.query_params.get('on_sale', None)
        if on_sale is None:
            return super().get_queryset()
        queryset = News.objects.all()
        if on_sale.lower() == 'true':
            from django.utils import timezone
            now = timezone.now()
            return queryset.filter(
                sale_start__lte=now,
                sale_end__gte=now,
            )
        return queryset

class NewsCreate(CreateAPIView):
    serializer_class = NewsSerializer

    def create(self, request, *args, **kwargs):
        try:
            price = request.data.get('price')
            if price is not None and float(price) <= 0.0:
                raise ValidationError({ 'price': 'Must be above $0.00' })
        except ValueError:
            raise ValidationError({ 'price': 'A valid number is required' })
        return super().create(request, *args, **kwargs)

class NewsRetrieveUpdateDestroy(RetrieveUpdateDestroyAPIView):
    queryset = News.objects.all()
    lookup_field = 'id'
    serializer_class = NewsSerializer

    def delete(self, request, *args, **kwargs):
        news_id = request.data.get('id')
        response = super().delete(request, *args, **kwargs)
        if response.status_code == 204:
            from django.core.cache import cache
            cache.delete('news_data_{}'.format(news_id))
        return response

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        if response.status_code == 200:
            from django.core.cache import cache
            news = response.data
            cache.set('news_data_{}'.format(news['id']), {
                'title': news['title'],
                'author_name': news['author_name'],
                'price': news['price'],
            })
        return response

class NewsStats(GenericAPIView):
    lookup_field = 'id'
    serializer_class = NewsStatSerializer
    queryset = News.objects.all()

    def get(self, request, format=None, id=None):
        obj = self.get_object()
        serializer = NewsStatSerializer({
            'stats': {
                '2019-01-01': [5, 10, 15],
                '2019-01-02': [20, 1, 1],
            }
        })
        return Response(serializer.data)
