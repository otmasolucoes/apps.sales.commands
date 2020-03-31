from otma.apps.core.communications.api import BaseController
from otma.apps.sales.commands.models import Group, Product, Command, Order, Additional
from otma.apps.sales.commands.service import CommunicationController
from django.utils import timezone
from datetime import datetime
import math


class CommandController(BaseController):
    model = Command
    extra_fields = []
    extra_names = {}

    def load(self, request):
        return super().filter(request, self.model, queryset=Command.objects.all(), extra_fields=self.extra_fields, is_response=True)

    def commands_by_table(self, request, table):
        return super().filter(request, self.model, queryset=Command.objects.filter(table=table), extra_fields=self.extra_fields, is_response=True)

    def close_commands_by_id(self, request, id):
        self.start_process(request)
        command = Command.objects.filter(pk=int(id))
        if command.count() > 0:
            command = command[0]
            table = command.table
            self.create_integration_file(request, command, table)
            command.exit = datetime.now(tz=timezone.utc)
        command.save()
        response_dict = {}
        response_dict['result'] = True
        response_dict['message'] = "Operação realizada com sucesso."
        return self.response(response_dict)

    def close_commands_by_table(self, request, table, id):
        self.start_process(request)
        command = Command.objects.filter(pk=int(id))
        if command.count() > 0:
            command = command[0]
            command.status = 'CLOSED'
            self.create_integration_file(request, command, table)
            command.exit = datetime.now(tz=timezone.utc)
        command.save()
        response_dict = {}
        response_dict['result'] = True
        response_dict['message'] = "Operação realizada com sucesso."
        return self.response(response_dict)

    def create_integration_file(self, request, command, table):
        controller = OrderController()
        orders = controller.orders_by_command(request, command.id, is_response=False)
        total_result = 0
        for order in orders['object']:
            items = MenuProductController().load_by_id(request, order['product'], is_response=False)
            for item in items['object']:
                total_result += int(order["quantity"])*item["price"]
                total = f'TOTAL||||||{total_result}|'
                data = f'{command.official_document}|{command.number}|{table}|{command.waiter}|{item["code"]}|{order["quantity"]}|{item["price"]}|\n'
                manager = CommunicationController()
                create_file = manager.write_txt_file(data=data, file_name=str(command.id) , out_folder_path='/home/cleiton/clientes/gigabyte/controller', mode='a')
        create_file = manager.write_txt_file(data=total, file_name=str(command.id) , out_folder_path='/home/cleiton/clientes/gigabyte/controller', mode='a', delete=True)


class MenuGroupController(BaseController):
    model = Group
    extra_fields = []
    extra_names = {}

    def all_groups(self, request):
        return super().filter(request, self.model, queryset=Group.objects.all(), extra_fields=self.extra_fields, is_response=True)

    def load_groups(self, request):
        response_group = super().filter(request, self.model, queryset=Group.objects.all(), extra_fields=self.extra_fields, is_response=False)
        count_groups = 0
        for object in response_group['object']:
            response_products = MenuProductController().load_products(request, group=object['id'], is_response=False)
            response_group['object'][count_groups]['products'] = response_products['object']
            count_groups += 1
        print(response_group)
        return self.response(response_group)


class OrderController(BaseController):
    model = Order
    extra_fields = []
    extra_names = {}

    def load_orders(self, request):
        return super().filter(request, self.model, queryset=Order.objects.all(), extra_fields=self.extra_fields, is_response=True)

    def orders_by_command(self, request, id, is_response=True):
        return super().filter(request, self.model, queryset=Order.objects.filter(command=int(id)), extra_fields=self.extra_fields, is_response=is_response)

    def change_orders_status(self, request, id, status):
        self.start_process(request)
        orders = Order.objects.filter(pk=int(id))
        if orders.count() > 0:
            order = orders[0]
            order.status = status
        order.save()
        response_dict = {}
        response_dict['result'] = True
        response_dict['message'] = "Operação realizada com sucesso."
        return self.response(response_dict)

    def close_orders_by_id(self, request, id):
        self.start_process(request)
        orders = Order.objects.filter(pk=int(id))
        if orders.count() > 0:
            order = orders[0]
            order.status = 'READY'
            order.exit = datetime.now(tz=timezone.utc)
        order.save()
        response_dict = {}
        response_dict['result'] = True
        response_dict['message'] = "Operação realizada com sucesso."
        return self.response(response_dict)

    def cancel_orders_by_id(self, request, id):
        self.start_process(request)
        orders = Order.objects.filter(pk=int(id))
        if orders.count() > 0:
            order = orders[0]
            order.status = 'CANCELED'
        order.save()
        response_dict = {}
        response_dict['result'] = True
        response_dict['message'] = "Operação realizada com sucesso."
        return self.response(response_dict)


class MenuProductController(BaseController):
    model = Product
    extra_fields = []
    extra_names = {}

    def load_products(self, request, group=None, is_response=True):
        if group:
            return super().filter(request, self.model, queryset=Product.objects.filter(group_id=int(group)), extra_fields=self.extra_fields, is_response=is_response)
        else:
            return super().filter(request, self.model, queryset=Product.objects.all(), extra_fields=self.extra_fields, is_response=is_response)

    def load_by_id(self, request, id, is_response=True):
        return super().filter(request, self.model, queryset=Product.objects.filter(pk=int(id)), extra_fields=self.extra_fields, is_response=is_response)

    def filter_apply(self, request, is_response=True):
        print('OLHA AI')
        queryset = Product.objects.all()
        verifier = VerifierRequest(request, queryset)
        queryset, total_registers, total_filtered, package, package_size = verifier.verify_filters(['type', 'code', 'name', 'price'])
        response = {}
        if total_filtered > 0:
            response['result'] = True
            response['message'] = "Registros carregados com sucesso!"
            response['object'] = {}
            response['object']['total_registers'] = total_registers
            response['object']['total_filtered'] = total_filtered
            response['object']['package'] = package
            response['object']['package_size'] = package_size
            response['object']['total_packages'] = math.ceil(total_filtered/package_size)
            response['object']['elements'] = super().filter(request, Product, queryset=queryset, extra_fields=self.extra_fields, is_response=False)['object']
        else:
            response['result'] = True
            response['object'] = None
            response['message'] = "Nenhum registro encontrado!"

        if is_response:
            return self.response(response)
        else:
            return response


class VerifierRequest:
    request = None
    queryset = None
    def __init__(self,request, queryset):
        self.request = request
        self.queryset = queryset

    def apply_filter(self, query):
        return self.queryset.filter(**query)

    def get_field(self, field):
        if (field in self.request.GET and self.request.GET[field]):
            return self.request.GET[field]
        return None

    def verify_search(self):
        search_value = self.get_field('search')
        if search_value is not None:
            search_by = self.get_field('search_by')
            if search_by is not None:
                if self.get_field('search_type') == 'INITIALS':
                    return self.apply_filter({search_by + "__istartswith": search_value})
                else:
                    return self.apply_filter({search_by+"__icontains": search_value})
        return self.queryset

    def verify_filters(self, filter_list):
        total_registers = self.queryset.count()
        for filter in filter_list:
            self.queryset = self.verify_filter(filter)

        self.queryset = self.verify_search()
        total_filtered = self.queryset.count()

        self.queryset = self.verify_order()
        self.queryset, package, package_size = self.verify_package()
        return self.queryset, total_registers, total_filtered, package, package_size

    def verify_filter(self, field):
        filter = self.get_field(field)
        if filter is not None:
            return self.apply_filter({field: filter})
        return self.queryset

    def verify_order(self):
        order = self.get_field('order')
        if order is not None:
            self.queryset = self.queryset.order_by(order)
        return self.queryset

    def verify_package(self):
        default_package = 1
        size_package = 200
        package = self.get_field('package') or default_package
        if package is not None:
            package = int(package)
            itens_per_page = self.get_field('itens_per_page') or size_package
            itens_per_page = int(itens_per_page)
            self.queryset = self.queryset[itens_per_page * (package - 1):itens_per_page * package]
        return self.queryset, package, size_package
