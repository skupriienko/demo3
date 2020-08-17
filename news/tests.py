import os.path
from django.conf import settings

from rest_framework.test import APITestCase

from news.models import News

class NewsCreateTestCase(APITestCase):
    def test_create_news(self):
        initial_news_count = News.objects.count()
        news_attrs = {
            'title': 'New News',
            'author_name': 'Awesome news',
            'price': '123.45',
        }
        response = self.client.post('/api/v1/news/new', news_attrs)
        if response.status_code != 201:
            print(response.data)
        self.assertEqual(
            News.objects.count(),
            initial_news_count + 1,
        )
        for attr, expected_value in news_attrs.items():
            self.assertEqual(response.data[attr], expected_value)
        self.assertEqual(response.data['is_on_sale'], False)
        self.assertEqual(
            response.data['current_price'],
            float(news_attrs['price']),
        )

class NewsDestroyTestCase(APITestCase):
    def test_delete_news(self):
        initial_news_count = News.objects.count()
        news_id = News.objects.first().id
        self.client.delete('/api/v1/news/{}/'.format(news_id))
        self.assertEqual(
            News.objects.count(),
            initial_news_count - 1,
        )
        self.assertRaises(
            News.DoesNotExist,
            News.objects.get, id=news_id,
        )

class NewsListTestCase(APITestCase):
    def test_list_news(self):
        news_s_count = News.objects.count()
        response = self.client.get('/api/v1/news/')
        self.assertIsNone(response.data['next'])
        self.assertIsNone(response.data['previous'])
        self.assertEqual(response.data['count'], news_s_count)
        self.assertEqual(len(response.data['results']), news_s_count)

class NewsUpdateTestCase(APITestCase):
    def test_update_news(self):
        news = News.objects.first()
        response = self.client.patch(
            '/api/v1/news/{}/'.format(news.id),
            {
                'title': 'New News',
                'author_name': 'Awesome news',
                'price': 123.45,
            },
            format='json',
        )
        updated = News.objects.get(id=news.id)
        self.assertEqual(updated.title, 'New News')

    def test_upload_news_photo(self):
        news = News.objects.first()
        original_photo = news.link
        photo_path = os.path.join(settings.MEDIA_ROOT, 'news', 'vitamin-iron.jpg')
        with open(photo_path, 'rb') as photo_data:
            response = self.client.patch('/api/v1/news/{}/'.format(news.id), {
                'link': photo_data,
            }, format='multipart')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.data['link'], original_photo)
        try:
            updated = News.objects.get(id=news.id)
            expected_photo = os.path.join(settings.MEDIA_ROOT, 'news', 'vitamin-iron')
            self.assertTrue(updated.link.path.startswith(expected_photo))
        finally:
            os.remove(updated.link.path)
