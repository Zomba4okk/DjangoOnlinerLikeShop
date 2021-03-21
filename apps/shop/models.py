from django.db import models


ORDER_STATUS_INCOMPLETE = 'incomplete'
ORDER_STATUS_PAID = 'paid'
ORDER_STATUS_CLOSED = 'closed'
ORDER_STATUS_CHOICES = (
    (ORDER_STATUS_INCOMPLETE, 'Incomplete'),
    (ORDER_STATUS_PAID, 'Paid'),
    (ORDER_STATUS_CLOSED, 'Closed'),
)


class Category(models.Model):
    class Meta:
        verbose_name_plural = 'categories'

    name = models.CharField(max_length=64)
    parent = models.ForeignKey(to='self', on_delete=models.CASCADE,
                               null=True, blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(to=Category, on_delete=models.SET_NULL,
                                 null=True, blank=True)
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=256)
    characteristics = models.CharField(max_length=256)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


class Cart(models.Model):
    user = models.OneToOneField(to='user.User', on_delete=models.CASCADE)
    products = models.ManyToManyField(to=Product, through='CartProductM2M')


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

    cart = models.ForeignKey(to=Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)
    product_count = models.IntegerField()


class OrderProductM2M(models.Model):
    class Meta:
        unique_together = (('order', 'product'),)
        verbose_name = 'product'

    order = models.ForeignKey(to=Order, on_delete=models.CASCADE)
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)
    product_count = models.IntegerField()
