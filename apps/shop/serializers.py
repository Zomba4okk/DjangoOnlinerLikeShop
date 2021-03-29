from rest_framework import serializers

from .models import (
    CartProductM2M,
    Category,
    Order,
    OrderProductM2M,
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


class CartProductCountSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartProductM2M
        fields = ('product', 'product_count')

    # Causes a massive query number optimazation issue.
    # Even if it recieves qs with products prefetched,
    # it still queries db for each individual product.
    # idk how to fix it
    product = serializers.SlugRelatedField(
        slug_field='id', read_only=False, queryset=Product.objects.all()
    )

    def validate(self, attrs):
        attrs = super().validate(attrs)

        if attrs['product_count'] < 0:
            raise serializers.ValidationError(
                'product_count must not be >= 0'
            )

        return attrs


class OrderProductCountSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderProductM2M
        fields = ('product', 'product_count')

    # Causes a massive query number optimazation issue.
    # Even if it recieves qs with products prefetched,
    # it still queries db for each individual product.
    # idk how to fix it
    product = serializers.SlugRelatedField(
        slug_field='id', read_only=False, queryset=Product.objects.all()
    )

    def validate(self, attrs):
        attrs = super().validate(attrs)

        if attrs['product_count'] < 0:
            raise serializers.ValidationError(
                'product_count must not be >= 0'
            )

        return attrs


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('id', 'status', 'products')

    products = OrderProductCountSerializer(
        many=True, source='orderproductm2m_set'
    )
