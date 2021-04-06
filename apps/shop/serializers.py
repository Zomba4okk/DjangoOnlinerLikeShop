from rest_framework import serializers

from .models import (
    Category,
    Order,
    Product,
)


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'parent')


class ProductCountSerializer(serializers.Serializer):

    product_id = serializers.IntegerField()
    product_count = serializers.IntegerField()


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('order_id', 'user_id', 'status', 'products')

    order_id = serializers.IntegerField(source='id')
    user_id = serializers.IntegerField(source='user.id')

    products = ProductCountSerializer(
        many=True, source='product_relations'
    )
