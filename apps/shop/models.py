from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from mptt import models as mpttmodels

from tinymce import HTMLField


ORDER_STATUS_INCOMPLETE = 'incomplete'
ORDER_STATUS_PAID = 'paid'
ORDER_STATUS_CLOSED = 'closed'
ORDER_STATUS_CHOICES = (
    (ORDER_STATUS_INCOMPLETE, 'Incomplete'),
    (ORDER_STATUS_PAID, 'Paid'),
    (ORDER_STATUS_CLOSED, 'Closed'),
)


class Category(mpttmodels.MPTTModel):
    class Meta:
        verbose_name_plural = 'categories'

    name = models.CharField(max_length=64)
    parent = mpttmodels.TreeForeignKey(to='self', on_delete=models.CASCADE,
                                       null=True, blank=True,
                                       related_name='children')

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(to=Category, on_delete=models.SET_NULL,
                                 null=True, blank=True)
    name = models.CharField(max_length=64)
    description = HTMLField('description')
    price = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=(MinValueValidator(Decimal('0.01')),)
    )

    def __str__(self):
        return f'{self.id}:{self.name}'


class Cart(models.Model):
    user = models.OneToOneField(to='user.User', on_delete=models.CASCADE,
                                related_name='cart')
    products = models.ManyToManyField(to=Product, through='CartProductM2M')

    def __str__(self):
        return f"{self.user.email}'s cart"


class Order(models.Model):
    user = models.ForeignKey(to='user.User', on_delete=models.SET_NULL,
                             null=True, related_name='orders')
    products = models.ManyToManyField(to=Product, through='OrderProductM2M')
    status = models.CharField(max_length=16, choices=ORDER_STATUS_CHOICES,
                              default=ORDER_STATUS_INCOMPLETE)

    def __str__(self):
        return self.user.email


class CartProductM2M(models.Model):
    class Meta:
        unique_together = (('cart', 'product'),)
        verbose_name = 'product'

    cart = models.ForeignKey(to=Cart, on_delete=models.CASCADE,
                             related_name='product_relations')
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE,
                                related_name='cart_relations')
    product_count = models.IntegerField(validators=(MinValueValidator(1),))

    def __str__(self):
        return f'{self.cart} - {self.product} - {self.product_count}'


class OrderProductM2M(models.Model):
    class Meta:
        unique_together = (('order', 'product'),)
        verbose_name = 'product'

    order = models.ForeignKey(to=Order, on_delete=models.CASCADE,
                              related_name='product_relations')
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE,
                                related_name='order_relations')
    product_count = models.IntegerField()
