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
    product_name = serializers.CharField(source='product.name', read_only=True)

    def validate(self, attrs):
        attrs = super().validate(attrs)

        if attrs['product_count'] == 0:
            raise serializers.ValidationError(
                'product_count must not be == 0'
            )

        return attrs


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('order_id', 'user_id', 'user_email', 'status', 'products')

    order_id = serializers.IntegerField(source='id')
    user_id = serializers.IntegerField(source='user.id')
    user_email = serializers.CharField(source='user.email')

    products = ProductCountSerializer(
        many=True, source='product_relations'
    )
