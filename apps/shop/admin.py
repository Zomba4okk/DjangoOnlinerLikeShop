from django.contrib import admin

from .forms import (
    OrderForm,
)
from .models import (
    Category,
    Order,
    OrderProductM2M,
    Product,
)


class OrderProductM2MInline(admin.TabularInline):
    model = OrderProductM2M
    extra = 1


class OrderAdmin(admin.ModelAdmin):
    model = Order
    form = OrderForm
    inlines = (OrderProductM2MInline,)
    readonly_fields = ('status',)


admin.site.register(Category)
admin.site.register(Order, OrderAdmin)
admin.site.register(Product)
