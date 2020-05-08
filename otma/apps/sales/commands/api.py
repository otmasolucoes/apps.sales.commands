from conf import profile
from otma.apps.core.communications.api import BaseController
from otma.apps.sales.commands.models import Table, Group, Product, Command, Order, Complement
from otma.apps.sales.commands.service import CommunicationController
from django.shortcuts import render, HttpResponse
from django.utils import timezone
from datetime import datetime, timedelta
import random
import math


def format_datetime(value):
    from datetime import timezone, datetime, timedelta
    if value is not None:
        datetime_with_timezone = value.astimezone(timezone.utc).strftime('%d/%m/%Y %H:%M:%S')
        print("VEJA DATA:",datetime_with_timezone)
        return datetime_with_timezone
        #return value.strftime("%d/%m/%Y, %H:%M:%S")
    else:
        return None

class CommandController(BaseController):
    model = Command
    extra_fields = ['orders']
    extra_names = {}

    def load(self, request):
        return super().filter(request, self.model, queryset=Command.objects.all(), extra_fields=self.extra_fields, is_response=True)

    def open(self, request):
        self.start_process(request)
        command = Command()
        command.table_id = request.POST['table_id']
        #command.status = "OPEN"
        print("VEJA O REQUEST USER: ",request.user)
        command.attendant = request.user
        #command.client_document = models.CharField(_('Número de documento'), max_length=20, null=True, blank=True, unique=False, error_messages=settings.ERRORS_MESSAGES)
        command.branch = "1"
        #command.checkin_time =
        #command.checkout_time = None
        #command.permanence_time = None
        #command.peoples = None
        command.total = 0.0
        command.save()
        command.code = command.id
        return self.response(self.execute(command, command.save))

    def close(self, request):
        self.start_process(request)
        command = Command.objects.filter(pk=request.POST['command_id'])
        if command.count() > 0:
            command = command[0]
            command.checkout_time = datetime.now()
            command.permanence_time = command.checkout_time - command.checkin_time
            command.status = "CLOSED"
            self.create_integration_file(request, command, table)

        #command.attendant = request.user
        # command.client_document = models.CharField(_('Número de documento'), max_length=20, null=True, blank=True, unique=False, error_messages=settings.ERRORS_MESSAGES)
        #command.branch = "1"
        # command.checkin_time =
        # command.checkout_time = None
        # command.permanence_time = None
        # command.peoples = None
        #command.total = 0.0
        command.save()
        return self.response(self.execute(command, command.save))

    def load_open_commands(self, request, table=None, is_response=False):
        return self.load_command(request, table, "OPEN", is_response)

    def load_command(self, request, table, status, is_response=True):
        if table is not None:
            commands = super().filter(request, self.model, queryset=Command.objects.filter(table=table).filter(status=status), extra_fields=self.extra_fields, is_response=is_response)
            count = 0
            for item in commands['object']:
                orders = OrderController().orders_by_command(request, item['id'], is_response=is_response)
                commands['object'][count]['orders'] = orders['object']
                count = count + 1

            if is_response:
                return self.response(commands)
            else:
                return commands
        else:
            return super().filter(request, self.model, queryset=Command.objects.filter(status=status), extra_fields=self.extra_fields, is_response=is_response)

    def commands_by_table(self, request, table):
        return super().filter(request, self.model, queryset=Command.objects.filter(table=table), extra_fields=self.extra_fields, is_response=True)

    def close_commands_by_id(self, request, id):
        self.start_process(request)
        command = Command.objects.filter(pk=int(id))
        if command.count() > 0:
            command = command[0]
            command.status = 'CLOSED'
            table = command.table
            command.checkout_time = datetime.now(tz=timezone.utc)
            self.create_integration_file(request, command, table.code)
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
            command.checkout_time = datetime.now(tz=timezone.utc)
            self.create_integration_file(request, command, table)
        command.save()
        response_dict = {}
        response_dict['result'] = True
        response_dict['message'] = "Operação realizada com sucesso."
        return self.response(response_dict)

    def create_integration_file(self, request, command, table):
        controller = OrderController()
        manager = CommunicationController()
        orders = controller.orders_by_command(request, command.id, is_response=False)
        total = self.calcula_total(request, orders)
        first_line = f'{table}|{command.attendant}|{total}|{command.client_document}|\n'
        create_file = manager.write_txt_file(data=first_line, file_name='comanda' + str(command.id), out_folder_path=profile.MELINUX_INTEGRATION_PATH, mode='a')
        for order in orders['object']:
            items = MenuProductController().load_by_id(request, order['product'], is_response=False)
            for item in items['object']:
                data = f'{item["code"]}|{order["quantity"]}|{item["price"]}|\n'
                create_file = manager.write_txt_file(data=data, file_name='comanda' + str(command.id), out_folder_path=profile.MELINUX_INTEGRATION_PATH, mode='a')
        create_file = manager.write_txt_file(data='', file_name='comanda' + str(command.id), out_folder_path=profile.MELINUX_INTEGRATION_PATH, mode='a', delete=True)

    def calcula_total(self, request, orders):
        total_result = 0
        for order in orders['object']:
            items = MenuProductController().load_by_id(request, order['product'], is_response=False)
            for item in items['object']:
                total_result += float(order["quantity"]) * float(item["price"])
        return "{0:.2f}".format(total_result)


class TableController(BaseController):
    model = Table
    extra_fields = []
    extra_names = {}

    def load(self, request):
        response_tables = super().filter(request, self.model, queryset=self.model.objects.all().order_by('id'), extra_fields=self.extra_fields, is_response=False)
        count = 0
        for table in response_tables['object']:
            response_commands = CommandController().load_open_commands(request, table=table['id'], is_response=False)
            response_tables['object'][count]['commands'] = response_commands['object']
            count += 1
        return self.response(response_tables)

    def open(self, request):
        self.start_process(request)
        table = Table.objects.filter(pk=int(request.POST['table_id']))
        if table.count() > 0:
            table = table[0]
            table.status = "ACTIVE"
            response = self.execute(table, table.save, extra_fields=['commands'])
        else:
            response = self.error({'table':'Falha na operação, mesa não cadastrada!'})
        return self.response(response)

    def close(self, request):
        self.start_process(request)
        table = Table.objects.filter(pk=int(request.POST['table_id']))
        if table.count() > 0:
            table = table[0]
            table.status = "CLOSED"
            response = self.execute(table, table.save)
        else:
            response = self.error({'table': 'Falha na operação, mesa não cadastrada!'})
        return self.response(response)


class MenuGroupController(BaseController):
    model = Group
    extra_fields = []
    extra_names = {}

    def load_tables(self, request):
        return super().filter(request, Table, queryset=Table.objects.all(), extra_fields=self.extra_fields, is_response=True)

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
    extra_fields = ['show_options']
    extra_names = {}

    def get_prevision_duration(self):
        # we specify the input and the format...
        #t = datetime.strptime("05:20:25", "%H:%M:%S")
        # ...and use datetime's hour, min and sec properties to build a timedelta
        hours = random.randint(0,2)
        minutes = random.randint(0,59)
        seconds = random.randint(0, 59)
        duration = timedelta(hours=hours, minutes=minutes, seconds=seconds)
        return duration


    def save(self, request):
        self.start_process(request)
        order = Order()
        order.command_id = int(request.POST['command_id'])
        order.product_id = int(request.POST['product_id'])
        order.product_name = request.POST['product_name']
        order.product_image = request.POST['product_image']
        order.product_price = request.POST['product_price']
        order.quantity = request.POST['quantity']
        order.total = float(request.POST['product_price'])*float(request.POST['quantity'])
        order.save()

        order.expected_duration = self.get_prevision_duration()
        order.expected_time = order.checkin_time + order.expected_duration
        #checkout_time = models.DateTimeField(_('Saída de pedido'), null=True, blank=True)
        #waiting_time = models.DurationField(null=True, blank=True)
        #implement_time = models.DurationField(null=True, blank=True)
        #duration_time = models.DurationField(null=True, blank=True)
        #status = models.CharField(_('Status'), max_length=20, default='WAITING', choices=STATUS_OF_ORDER, null=True, blank=True, error_messages=settings.ERRORS_MESSAGES)
        order.observations = request.POST['observations']
        response = self.execute(order, order.save)
        order.command.total = order.command.total + order.total
        order.command.save()
        #self.print(request, order.id)
        return self.response(response)

    def load_orders(self, request):
        return super().filter(request, self.model, queryset=Order.objects.all(), extra_fields=self.extra_fields, is_response=True)

    def orders_by_command(self, request, id, is_response=True):
        return super().filter(request, self.model, queryset=Order.objects.filter(command=int(id)).order_by('-id'), extra_fields=self.extra_fields, is_response=is_response)

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

    def prepare_order(self, order):
        import math
        import os

        barcode = order.barcode
        if barcode is None:
            barcode = order.create_barcode()
        else:
            if not os.path.isfile("media/barcodes/" + order.barcode):
                barcode = order.create_barcode()

        complements = Complement.objects.filter(order=order)

        main_content_height_space = 55
        complements_height_space = 8 * complements.count()

        observation_height_space = 0
        if order.observations is not None:
            observation_height_space = math.ceil(len(order.observations) / 40) * 8

        barcode_height_space = 48
        total_height = main_content_height_space + complements_height_space + observation_height_space + barcode_height_space

        response = {
            'id': order.id, 'command': order.command_id, 'product': order.product_id, 'product_name': order.product_name,
            'product_image': order.product_image, 'product_price': order.product_price, 'quantity': order.quantity,
            'total': order.total, 'status': order.status, 'barcode': order.barcode,
            'checkin_time': order.checkin_time, 'checkin_time_hours': order.checkin_time,
            'checkout_time': format_datetime(order.checkout_time), 'waiting_time': order.waiting_time,
            'implement_time': order.implement_time, 'closed_time': format_datetime(order.closed_time),
            'duration_time': order.duration_time, 'expected_time': order.expected_time,
            'expected_duration': order.expected_duration, 'complements': complements,
            'observations': order.observations, 'total_height': total_height,
        }
        return response

    def view(self, request, id=None):
        self.start_process(request)
        from django_xhtml2pdf.utils import generate_pdf

        id = id or request.POST['order_id']
        order = Order.objects.filter(pk=int(id))
        if order.count() > 0:
            response_order = self.prepare_order(order[0])
            respone_content = HttpResponse(content_type='application/pdf')
            result = generate_pdf('order_pdf.html', file_object=respone_content, context={'order': response_order})
            return result
        return self.response({"result":False,"object":None,"message":"Object not found"})

    def print(self, request, id=None):
        self.start_process(request)
        from conf import profile
        import requests

        order_id = id or request.POST["order_id"]
        order = Order.objects.filter(pk=int(order_id))
        if order.count() > 0:
            route = "http://" + request.get_host() + "/api/sales/commands/order/" + str(order_id) + "/"
            filename = 'media/orders/' + str(order_id) + '.pdf'
            response = requests.get(route, params={"order_id":int(order_id)})
            with open(filename, 'wb') as file:
                file.write(response.content)

            #printer_controller = PrinterController()
            #printers = printer_controller.scan()
            #printer_controller.print(printers[0],filename)
            printer = PrinterController()
            print('O PDF FOI GERADO PREPARANDO PARA IMPRIMIR...', pdf_path)
            printer.print(profile.PRINTER_CONFIG, pdf_path, title="test_python")
            print('IMPRIMIDO COM SUCESSO!!!')

            print("SERA QUE IMPRIMIU?")

            return self.response({"result": True, "object": None, "message": "Order was printed"})
        return self.response({"result": False, "object": None, "message": "Object not found"})


class MenuProductController(BaseController):
    model = Product
    extra_fields = []
    extra_names = {}

    def load_products(self, request, group=None, is_response=True):
        if group:
            return super().filter(request, self.model, queryset=Product.objects.filter(group_id=int(group)).order_by('id'), extra_fields=self.extra_fields, is_response=is_response)
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

    def __init__(self, request, queryset):
        self.request = request
        self.queryset = queryset

    def apply_filter(self, query):
        return self.queryset.filter(**query)

    def get_field(self, field):
        if field in self.request.GET and self.request.GET[field]:
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


class DatabaseController(BaseController):

    def __init__(self):
        self.filename = None
        self.extension = None
        self.model = None
        self.dependency_model = None

    def load(self, request):
        self.start_process(request)
        try:
            self.extension = request.GET['extension']
        except:
            pass
        if 'filename' in request.GET:
            self.filename = request.GET['filename']
            if self.filename == 'products':
                self.model = Product
                self.dependency_model = Group
            elif self.filename == 'groups':
                self.model = Group
        communication = CommunicationController()
        load = communication.field_search(model=self.model, filename=self.filename, extension=self.extension, dependency=self.dependency_model)
        response_dict = {}
        if load:
            response_dict['result'] = True
            response_dict['message'] = "Operação realizada com sucesso."
        else:
            response_dict['result'] = False
            response_dict['message'] = "Algo deu errado."
        return self.response(response_dict)

    def update(self, request):
        self.start_process(request)
        self.model = Product
        if 'extension' in request.GET:
            self.extension = request.GET['extension']
        communication = CommunicationController()
        load = communication.field_search(model=self.model)
        response_dict = {}
        if load:
            response_dict['result'] = True
            response_dict['message'] = "Operação realizada com sucesso."
        else:
            response_dict['result'] = False
            response_dict['message'] = "Algo deu errado."
        return self.response(response_dict)
