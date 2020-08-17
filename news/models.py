
from django.utils import timezone
from django.db import models


class News(models.Model):
    DISCOUNT_RATE = 0.10

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    author_name = models.CharField(max_length=50)
    price = models.FloatField()
    creation_date = models.DateTimeField(blank=True, null=True, default=None)
    sale_end = models.DateTimeField(blank=True, null=True, default=None)
    link = models.URLField(max_length=200, null=True)
    likes = models.IntegerField(verbose_name='Like', default=0)
    dislikes = models.IntegerField(verbose_name='Dislike', default=0)

    def is_on_sale(self):
        now = timezone.now()
        if self.creation_date:
            if self.sale_end:
                return self.creation_date <= now <= self.sale_end
            return self.creation_date <= now
        return False

    def get_rounded_price(self):
        return round(self.price, 2)

    def current_price(self):
        if self.is_on_sale():
            discounted_price = self.price * (1 - self.DISCOUNT_RATE)
            return round(discounted_price, 2)
        return self.get_rounded_price()

    def __repr__(self):
        return '<News object ({}) "{}">'.format(self.id, self.title)

class ShoppingCart(models.Model):
    TAX_RATE = 0.13
  
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    address = models.CharField(max_length=200)

    def subtotal(self):
        amount = 0.0
        for item in self.shopping_cart_items:
            amount += item.quantity * item.news.get_price()
        return round(amount, 2)

    def taxes(self):
        return round(self.TAX_RATE * self.subtotal(), 2)

    def total(self):
        return round(self.subtotal() * self.taxes(), 2)
 
    def __repr__(self):
        title = self.title or '[Guest]'
        address = self.address or '[No Address]'
        return '<ShoppingCart object ({}) "{}" "{}">'.format(self.id, title, address)

class ShoppingCartItem(models.Model):
    shopping_cart = models.ForeignKey(ShoppingCart, related_name='items', related_query_name='item', on_delete=models.CASCADE)
    news = models.ForeignKey(News, related_name='+', on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def total(self):
        return round(self.quantity * self.news.current_price())

    def __repr__(self):
        return '<ShoppingCartItem object ({}) {}x "{}">'.format(self.id, self.quantity, self.news.title)


