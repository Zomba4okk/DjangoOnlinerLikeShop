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
    name = models.CharField(max_length=64)
    parent = models.ForeignKey(to='self', on_delete=models.CASCADE)


class Product(models.Model):
    category = models.ForeignKey(to=Category, on_delete=models.SET_NULL,
                                 null=True)
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=256)
    characteristics = models.CharField(max_length=256)
    price = models.DecimalField(max_digits=10, decimal_places=2)


class Cart(models.Model):
    user = models.OneToOneField(to='user.User', on_delete=models.CASCADE)
    products = models.ManyToManyField(to=Product, through='Cart_Product_m2m')


class Order(models.Model):
    user = models.ForeignKey(to='user.User', on_delete=models.SET_NULL,
                             null=True, related_name='orders')
    products = models.ManyToManyField(to=Product, through='Order_Product_m2m')
    status = models.CharField(max_length=16, choices=ORDER_STATUS_CHOICES)


class Cart_Product_m2m(models.Model):
    cart = models.ForeignKey(to=Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)
    product_count = models.IntegerField()


class Order_Product_m2m(models.Model):
    order = models.ForeignKey(to=Order, on_delete=models.CASCADE)
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)
    product_count = models.IntegerField()
