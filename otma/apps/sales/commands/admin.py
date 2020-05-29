from otma.apps.sales.commands.models import Group, Table, Command, Product, Order, Complement
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
        base_template = """
            <a href='/admin/commands/product/{}/change/'>
            <table border='0' style='margin:0px;width:100%;'>
                <tr style='height:50px;'>
                    <td style='padding:0px;width:60px;height:100%;border-bottom: 0px;'>
                        <img src='{}' style='width:60px;height:50px;'>
                    </td>
                    <td style='border-bottom: 0px;'><b>{}.{}. {} <span style='font-size:10px;position:relative;top:-1px;'>({})</span></b><br><span style='font-weight:normal;'>{}</span></td>
                    <td style='width:70px;text-align:center;vertical-align:middle;border-bottom:0px; '>R$ {}</td>
                </tr>
            </table>
            </a>
        """.format(obj.id ,obj.image.url, obj.group.code, obj.code, obj.name, obj.group.name,description, obj.price)
        return format_html(base_template)

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'area', 'status', 'total', 'capacity')
    ordering = ('id',)

@admin.register(Command)
class CommandsAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'table', 'status', 'attendant', 'client_document', 'branch', 'checkin_time', 'checkout_time', 'permanence_time', 'peoples', 'total')
    ordering = ('id',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'command', 'product', 'image', 'name', 'price', 'quantity', 'total', 'status', 'checkin_time', 'expected_duration', 'expected_time', 'checkout_time', 'waiting_time','implement_time', 'closed_time', 'duration_time', 'barcode', 'observations')
    ordering = ('id',)


@admin.register(Complement)
class ComplementAdmin(admin.ModelAdmin):
    list_display = ('id', 'command', 'product', 'order')
    ordering = ('id',)
