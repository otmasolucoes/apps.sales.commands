from otma.apps.sales.commands.models import Group, Table, Command, Product, Order, Additional
from django.contrib import admin


@admin.register(Group)
class GroupsAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'name', 'description', 'image')
    ordering = ('id',)


@admin.register(Product)
class ProductsAdmin(admin.ModelAdmin):
    list_display = ('id', 'group', 'code', 'name', 'description', 'price', 'image', 'have_promotion')
    ordering = ('id',)

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'area', 'status', 'capacity')
    ordering = ('id',)

@admin.register(Command)
class CommandsAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'table', 'status', 'attendant', 'client_document', 'branch', 'checkin_time', 'checkout_time', 'permanence_time', 'peoples', 'total')
    ordering = ('id',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'command', 'product', 'product_image', 'product_name', 'product_price', 'quantity', 'total', 'status', 'checkin_time', 'expected_duration', 'expected_time', 'checkout_time', 'waiting_time','implement_time', 'closed_time', 'duration_time', 'barcode', 'observations')
    ordering = ('id',)


@admin.register(Additional)
class AdditionalAdmin(admin.ModelAdmin):
    list_display = ('id', 'command', 'product', 'order')
    ordering = ('id',)
