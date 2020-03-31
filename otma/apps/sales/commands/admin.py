from otma.apps.sales.commands.models import Group, Command, Product, Order, Additional
from django.contrib import admin


@admin.register(Group)
class GroupsAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'name', 'description', 'image')
    ordering = ('id',)


@admin.register(Product)
class ProductsAdmin(admin.ModelAdmin):
    list_display = ('id', 'group', 'code', 'name', 'description', 'price', 'image', 'have_promotion')
    ordering = ('id',)


@admin.register(Command)
class CommandsAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'table', 'status', 'attendant', 'client_document', 'branch', 'checkin_time', 'checkout_time', 'permanence_time', 'peoples', 'value')
    ordering = ('id',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'command', 'product', 'status', 'checkin_time', 'checkout_time','waiting_time','implement_time','duration_time', 'quantity', 'observations')
    ordering = ('id',)


@admin.register(Additional)
class AdditionalAdmin(admin.ModelAdmin):
    list_display = ('id', 'command', 'product', 'order')
    ordering = ('id',)
