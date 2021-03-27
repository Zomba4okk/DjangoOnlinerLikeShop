from rest_framework import serializers

from .models import (
    CartProductM2M,
    Category,
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


class ProductCountSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartProductM2M
        fields = ('product', 'product_count')

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
