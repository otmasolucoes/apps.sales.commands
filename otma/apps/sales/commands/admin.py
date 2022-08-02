from otma.apps.sales.commands.models import Group, Table, Command, Product, Order, Item, Complement
from django.utils.html import format_html
from django.contrib import admin


@admin.register(Group)
class GroupsAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'name', 'description', 'image')
    ordering = ('id',)


@admin.register(Product)
class ProductsAdmin(admin.ModelAdmin):
    list_display = ('name_preview', )
    ordering = ('group',)

    def name_preview(self, obj):
        description = obj.description or ""
        base_template = f"""
            <a href='/admin/commands/product/{obj.id}/change/'>
            <table border='0' style='margin:0px;width:100%;'>
                <tr style='height:50px;'>
                    <td style='padding:0px;width:60px;height:100%;border-bottom: 0px;'>
                        <img src='{obj.image}' style='width:60px;height:50px;'>
                    </td>
                    <td style='border-bottom: 0px;'><b>{obj.group.code}.{obj.code}. {obj.name} <span style='font-size:10px;position:relative;top:-1px;'>({obj.group.name})</span></b><br><span style='font-weight:normal;'>{description}</span></td>
                    <td style='width:70px;text-align:center;vertical-align:middle;border-bottom:0px; '>R$ {obj.price}</td>
                </tr>
            </table>
            </a>
        """
        return format_html(base_template)

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'area', 'status', 'total', 'capacity')
    ordering = ('id',)

@admin.register(Command)
class CommandsAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'table', 'status', 'attendant', 'client_document', 'branch', 'checkin_time',
                    'checkout_time', 'permanence_time', 'peoples', 'total')
    ordering = ('id',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'command', 'status', 'checkin_time', 'total', 'checkout_time', 'barcode')
    ordering = ('id',)


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'status', 'image', 'name', 'price', 'quantity', 'expected_duration',
                    'expected_time', 'waiting_time','implement_time', 'closed_time', 'duration_time', 'description',
                    'was_sent', 'observations')
    ordering = ('id',)


@admin.register(Complement)
class ComplementAdmin(admin.ModelAdmin):
    list_display = ('id', 'command', 'product', 'order')
    ordering = ('id',)
