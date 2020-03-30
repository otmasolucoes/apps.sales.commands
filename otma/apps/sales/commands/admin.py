from otma.apps.sales.commands.models import Group, Command, Product, Order, Additional
from django.contrib import admin


@admin.register(Group)
class GroupsAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'name', 'description', 'image')
    ordering = ('id',)


@admin.register(Command)
class CommandsAdmin(admin.ModelAdmin):
    list_display = ('id', 'official_document', 'branch', 'waiter', 'number', 'enter', 'exit', 'table', 'status')
    ordering = ('id',)


@admin.register(Product)
class ProductsAdmin(admin.ModelAdmin):
    list_display = ('id', 'group', 'code', 'name', 'description', 'price', 'image')
    ordering = ('id',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'command', 'product', 'enter', 'exit', 'quantity', 'note', 'status')
    ordering = ('id',)


@admin.register(Additional)
class AdditionalAdmin(admin.ModelAdmin):
    list_display = ('id', 'command', 'product', 'order')
    ordering = ('id',)
