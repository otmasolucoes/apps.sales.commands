import os
import math
import json
import random
import barcode
import requests
import subprocess
from conf import profile
from decimal import Decimal
from test_project.signals import sio
from otma.apps.core.communications.api import BaseController
from otma.apps.sales.commands.models import Table, Group, Product, Command, Order, Item, Complement
from otma.apps.sales.commands.service import CommunicationController
from django.shortcuts import render, HttpResponse
from django.utils import timezone
from datetime import datetime, timedelta
from django_xhtml2pdf.utils import generate_pdf
from barcode.writer import ImageWriter


def format_datetime(value):
    from datetime import timezone, datetime, timedelta
    if value is not None:
        datetime_with_timezone = value.astimezone(timezone.utc).strftime('%d/%m/%Y %H:%M:%S')
        return datetime_with_timezone
    else:
        return None


def run_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    result_dict = {"result": True if output.decode() != "" else True,
                   "object": None,
                   "message": output.decode().replace("\n", "")
                   if output.decode() != "" else error.decode().replace("\n", "")
                   }
    return result_dict


class TableController(BaseController):
    model = Table
    extra_fields = []
    extra_names = {}

    def load(self, request, extra_fields=None, is_response=True):
        response_tables = super().filter(request,
                                         self.model,
                                         queryset=self.model.objects.all().order_by('id'),
                                         extra_fields=extra_fields or self.extra_fields,
                                         is_response=False)
        for index, table in enumerate(response_tables['object']):
            response_commands = CommandController().load_open_commands(request,
                                                                       table=table['id'],
                                                                       is_response=False)
            response_tables['object'][index]['commands'] = response_commands['object']
        return self.response(response_tables)

    def open(self, request):
        self.start_process(request)
        table = Table.objects.filter(pk=int(request.POST['table_id']))
        if table.count() > 0:
            table = table[0]
            table.total = 0
            table.status = "ACTIVE"
            response = self.execute(table, table.save, extra_fields=['commands'])
        else:
            response = self.error({'table': 'Falha na operação, mesa não cadastrada!'})
        return self.response(response)

    def close_by_id(self, request, id):
        self.start_process(request)
        table = Table.objects.filter(pk=int(id))
        if table.count() > 0:
            table = table[0]
            table.status = "CLOSED"
            response = self.execute(table, table.save)
        else:
            response = self.error({'table': 'Falha na operação, mesa não cadastrada!'})
        return self.response(response)


class CommandController(BaseController):
    model = Command
    extra_fields = ['orders']
    extra_names = {}

    def load(self, request, extra_fields=None, is_response=True):
        return super().filter(request,
                              self.model,
                              queryset=Command.objects.all(),
                              extra_fields=extra_fields or self.extra_fields,
                              is_response=True)

    def open(self, request):
        self.start_process(request)
        command = Command()
        command.table_id = request.POST['table_id']
        # command.status = "OPEN"
        # print("VEJA O REQUEST USER: ", request.user)
        command.attendant = request.user
        # command.client_document = models.CharField(_('Número de documento'), max_length=20, null=True, blank=True,
        # unique=False, error_messages=settings.ERRORS_MESSAGES)
        command.branch = "1"
        # command.checkin_time =
        # command.checkout_time = None
        # command.permanence_time = None
        # command.peoples = None
        command.total = 0.0
        command.save()
        command.code = command.id
        response = self.execute(command, command.save)
        return self.response(response)

    def close_by_id(self, request, id):
        self.start_process(request)
        command = Command.objects.filter(pk=int(id))
        if command.count() > 0:
            command = command[0]
            command.checkout_time = datetime.now()
            command.permanence_time = command.checkout_time - command.checkin_time
            command.status = "CLOSED"
            command.total = 0.0
            self.create_integration_file(request, command, table)

        # command.attendant = request.user
        # command.client_document = models.CharField(_('Número de documento'), max_length=20, null=True, blank=True,
        # unique=False, error_messages=settings.ERRORS_MESSAGES)
        # command.branch = "1"
        # command.checkin_time =
        # command.checkout_time = None
        # command.permanence_time = None
        # command.peoples = None

        command.save()
        response = self.execute(command, command.save)
        return self.response(response)

    def load_open_commands(self, request, table=None, is_response=False):
        return self.load_command(request, table, "OPEN", is_response)

    def load_command(self, request, table, status, is_response=True):
        if table is not None:
            commands = super().filter(request,
                                      self.model,
                                      queryset=Command.objects.filter(table=table).filter(status=status),
                                      extra_fields=self.extra_fields,
                                      is_response=is_response)
            for index, command in enumerate(commands['object']):
                orders = OrderController().orders_by_command(request, command['id'], is_response=is_response)
                commands['object'][index]['orders'] = orders['object']

            if is_response:
                return self.response(commands)
            else:
                return commands
        else:
            return super().filter(request,
                                  self.model,
                                  queryset=Command.objects.filter(status=status),
                                  extra_fields=self.extra_fields,
                                  is_response=is_response)

    def commands_by_table(self, request, table, extra_fields=None, is_response=True):
        return super().filter(request,
                              self.model,
                              queryset=Command.objects.filter(table=table),
                              extra_fields=extra_fields or self.extra_fields,
                              is_response=True)

    def close_commands_by_id(self, request, id):
        self.start_process(request)
        command = Command.objects.filter(pk=int(id))
        if command.count() > 0:
            command = command[0]
            command.status = 'CLOSED'
            table = command.table
            table.status = 'CLOSED' if request.POST.get("is_last_command") == 'true' else "ACTIVE"
            command.checkout_time = datetime.now(tz=timezone.utc)
            self.create_integration_file(request, command, table.code)
            table.total -= command.total if table.total >= command.total else table.total
            table.save()
        command.save()
        response = self.execute(command, command.save)
        return self.response(response)

    def close_commands_by_table(self, request, table, id):
        self.start_process(request)
        command = Command.objects.filter(pk=int(id))
        if command.count() > 0:
            command = command[0]
            command.status = 'CLOSED'
            table = command.table
            table.status = 'CLOSED' if request.POST.get("is_last_command") == 'true' else "ACTIVE"
            command.checkout_time = datetime.now(tz=timezone.utc)
            self.create_integration_file(request, command, table)
        command.save()
        response = self.execute(command, command.save)
        return self.response(response)

    def create_integration_file(self, request, command, table):
        complements = None
        orders = OrderController().orders_by_command(request, command.id, is_response=False)
        total = self.calculate_total(request, orders)
        first_line = f'{table}|{command.attendant}|{total}|' \
                     f'{command.client_document if command.client_document else "00000000000"}|' \
                     f'{command.checkin_time.strftime("%Y-%m-%d %H:%M:%S")}|'
        create_file = CommunicationController().write_txt_file(data=first_line,
                                                               file_name='comanda' + str(command.id),
                                                               out_folder_path=profile.MELINUX_INTEGRATION_PATH,
                                                               mode='a')
        for order in orders['object']:
            items = MenuProductController().load_by_id(request, order['product'], is_response=False)
            complements = OrderController().complements_by_order(request, order["id"], is_response=False)
            # if len(complements["object"]) > 0 and order["product"] == complements["object"][0]["product"]:
            # items["object"] += complements["object"]
            for item in items['object']:
                data = f'{item["code"]}|{order["quantity"]}|{item["price"]}|'
                create_file = CommunicationController().write_txt_file(data=data,
                                                                       file_name='comanda' + str(command.id),
                                                                       out_folder_path=profile.MELINUX_INTEGRATION_PATH,
                                                                       mode='a')

        create_file = CommunicationController().write_txt_file(data='',
                                                               file_name='comanda' + str(command.id),
                                                               out_folder_path=profile.MELINUX_INTEGRATION_PATH,
                                                               mode='a', delete=True)

    def calculate_total(self, request, orders):
        total_result = 0
        for order in orders['object']:
            items = MenuProductController().load_by_id(request, order['product'], is_response=False)
            for item in items['object']:
                total_result += float(order["quantity"]) * float(item["price"])
        return "{0:.2f}".format(total_result)


class MenuGroupController(BaseController):
    model = Group
    extra_fields = []
    extra_names = {}

    def load_tables(self, request, extra_fields=None, is_response=True):
        return super().filter(request,
                              Table,
                              queryset=Table.objects.all(),
                              extra_fields=extra_fields or self.extra_fields,
                              is_response=True)

    def all_groups(self, request, extra_fields=None, is_response=True):
        return super().filter(request,
                              self.model,
                              queryset=Group.objects.all(),
                              extra_fields=extra_fields or self.extra_fields,
                              is_response=True)

    def load_groups(self, request, extra_fields=None, is_response=True):
        response_group = super().filter(request,
                                        self.model,
                                        queryset=Group.objects.all().order_by("code"),
                                        extra_fields=extra_fields or self.extra_fields,
                                        is_response=False)
        for index, object in enumerate(response_group['object']):
            response_products = MenuProductController().load_products(request, group=object['id'], is_response=False)
            response_group['object'][index]['products'] = response_products['object']
        return self.response(response_group)


class OrderController(BaseController):
    model = Order
    extra_fields = ['product__description', 'product__have_promotion', 'show_options']
    extra_names = {}

    def get_prevision_duration(self):
        # we specify the input and the format...
        # t = datetime.strptime("05:20:25", "%H:%M:%S")
        # ...and use datetime's hour, min and sec properties to build a timedelta
        hours = random.randint(0, 2)
        minutes = random.randint(0, 59)
        seconds = random.randint(0, 59)
        duration = timedelta(hours=hours, minutes=minutes, seconds=seconds)
        return duration

    def save(self, request):
        self.start_process(request)
        list_items_response = []
        list_items = json.loads(request.POST.get("items"))
        if request.POST.get('order_id'):
            order = Order.objects.filter(pk=int(request.POST['order_id']))
            if order.count() > 0:
                order = order[0]
        else:
            order = Order()
        order.command_id = int(request.POST['command_id'])
        order.save()
        if len(list_items) > 0:
            order_total = 0
            for data_item in list_items:
                item = Item()
                item.order = order
                item.product_id = int(data_item["id"])
                item.name = data_item['name']
                item.image = data_item['image']
                item.price = Decimal(data_item['price'])
                item.quantity = Decimal(data_item['quantity'])
                item.was_sent = True
                item.observations = data_item.get('observations')
                item.save()
                # item.expected_duration = self.get_prevision_duration()
                item.expected_duration = timedelta(hours=data_item["duration_time"]["hours"],
                                                   minutes=data_item["duration_time"]["minutes"],
                                                   seconds=data_item["duration_time"]["seconds"])
                item.expected_time = item.checkin_time + item.expected_duration

                complements_total = Decimal(request.POST['complements_total'])
                complements = data_item.get("complements")
                print("OLHA AÍ OS COMPLEMENTOS: ", json.dumps(complements, indent=4))

                if len(complements) > 0:
                    for data_complement in complements:
                        complement = Complement()
                        complement.order = order
                        complement.command = order.command
                        complement.product = order.product
                        complement.code = data_complement["code"]
                        complement.name = data_complement["name"]
                        complement.price = Decimal(data_complement["price"])
                        complement.quantity = data_complement["quant"]
                        complement.save()
                order_total += Decimal((item.price + complements_total) * item.quantity)

                items_response = self.execute(item, item.save)
                list_items_response.append(items_response["object"])

            order.total = order_total
            order.command.total = Decimal(order.command.total + order.total)
            order.command.table.total = Decimal(order.command.table.total + order.total)
            order.save()
            order.command.save()
            order.command.table.save()
            order_response = self.execute(order, order.save)
            order_response["object"]["items"] = list_items_response
        return self.response(order_response)

    def update(self, request):
        self.start_process(request)
        # print("OLHA O REQUEST: ", request.POST)
        print("OLHA O REQUEST: ", json.loads(json.dumps(request.POST)))
        print("OLHA O ORDERS: ", json.loads(request.POST.get("orders")))
        list_response = []
        list_orders = json.loads(request.POST.get("orders"))
        if len(list_orders) > 0:
            for data_order in list_orders:
                print(data_order)
                order = Order()
                order.command_id = int(request.POST['command_id'])
                order.product_id = int(data_order['id'])
                order.name = data_order['name']
                order.image = data_order['image']
                order.price = Decimal(data_order['price'])
                order.quantity = Decimal(data_order['quantity'])
                order.was_sent = True
                complements_total = Decimal(request.POST['complements_total'])
                print("OLHA O TOTAL DO PEDIDO: ", float((order.price + complements_total) * order.quantity))
                complements = data_order.get("complements")
                print("OLHA AÍ OS COMPLEMENTOS: ", json.dumps(complements, indent=4))
                order.total = Decimal((order.price + complements_total) * order.quantity)
                order.save()
                # order.expected_duration = self.get_prevision_duration()
                order.expected_duration = timedelta(hours=data_order["duration_time"]["hours"],
                                                    minutes=data_order["duration_time"]["minutes"],
                                                    seconds=data_order["duration_time"]["seconds"])
                order.expected_time = order.checkin_time + order.expected_duration
                order.observations = data_order.get('observations')
                order.save()
                print("OLHA O TOTAL DA COMANDA: CODE", order.command.code, " - ID: ", order.command.id,
                      order.command.total,
                      " PEDIDO: ", float(order.total), " NOVO TOTAL: ", float(order.command.total + order.total))
                order.command.total = order.command.total + order.total
                order.command.save()
                print("OLHA O TOTAL DA MESA: ", float(order.command.table.total + order.total))
                order.command.table.total = float(order.command.table.total + order.total)
                order.command.table.save()
                if len(complements) > 0:
                    for item in complements:
                        complement = Complement()
                        complement.order = order
                        complement.command = order.command
                        complement.product = order.product
                        complement.code = item["code"]
                        complement.name = item["name"]
                        complement.price = Decimal(item["price"])
                        complement.quantity = item["quant"]
                        complement.save()
                response = self.execute(order, order.save)
                list_response.append(response["object"])
            response["object"] = list_response
        return self.response(response)

    def load_orders(self, request, extra_fields=None, is_response=True):
        return super().filter(request,
                              self.model,
                              queryset=Order.objects.all(),
                              extra_fields=extra_fields or self.extra_fields,
                              is_response=True)

    def orders_by_command(self, request, id, extra_fields=None, is_response=True):
        orders = super().filter(request,
                                self.model,
                                queryset=Order.objects.filter(command=int(id)).order_by('-id'),
                                extra_fields=extra_fields or self.extra_fields,
                                is_response=is_response)
        list_items = []
        for index, order in enumerate(orders['object']):
            items = ItemController().items_by_order(request, order['id'], is_response=is_response)
            for i in items['object']:
                list_items.append(i)
        orders['object'] = list_items

        if is_response:
            return self.response(orders)
        else:
            return orders

    def complements_by_order(self, request, id, extra_fields=None, is_response=True):
        return super().filter(request,
                              Complement,
                              queryset=Complement.objects.filter(order=int(id)).order_by('-id'),
                              extra_fields=extra_fields or self.extra_fields,
                              is_response=is_response)

    def change_orders_status(self, request, id, status):
        self.start_process(request)
        orders = Order.objects.filter(pk=int(id))
        if orders.count() > 0:
            order = orders[0]
            order.status = status
        order.save()
        response = self.execute(order, order.save)
        return self.response(response)

    def change_status_item(self, request, id, status):
        self.start_process(request)
        items = Item.objects.filter(pk=int(id))
        if items.count() > 0:
            item = items[0]
            item.status = status
        item.save()

        response = self.execute(item, item.save)
        response["object"]["table"] = request.POST.get("table_id")
        response["object"]["table_index"] = request.POST.get("table_index")
        response["object"]["command_index"] = request.POST.get("command_index")
        response["object"]["item_index"] = request.POST.get("item_index")

        sio.emit('change_status', {'data': response})

        return self.response(response)

    def close_orders_by_id(self, request, id):
        self.start_process(request)
        orders = Order.objects.filter(pk=int(id))
        if orders.count() > 0:
            order = orders[0]
            order.status = 'READY'
            order.exit = datetime.now(tz=timezone.utc)
        order.save()
        response = self.execute(order, order.save)
        return self.response(response)

    def cancel_orders_by_id(self, request, id):
        self.start_process(request)
        orders = Order.objects.filter(pk=int(id))
        if orders.count() > 0:
            order = orders[0]
            order.status = 'CANCELED'
        order.save()
        response = self.execute(order, order.save)
        return self.response(response)

    def prepare_order(self, order):
        media_path = "media/barcodes/"
        if not os.path.exists(media_path):
            os.makedirs(media_path)
        barcode = order.barcode
        if barcode is None:
            barcode = order.create_barcode()
        else:
            if not os.path.isfile(os.path.join(media_path, order.barcode)):
                barcode = order.create_barcode()

        complements = Complement.objects.filter(order=order)
        complement_list = []
        if complements.count() > 0:
            for complement in complements:
                complements_result = {}
                complements_result["name"] = complement.name
                complements_result["quant"] = int(complement.quantity)
                complements_result["price"] = complement.price
                complement_list.append(complements_result)
        print("OLHA AÍ OS COMPLEMENTOS DESSE PEDIDO: ", complement_list)

        main_content_height_space = 47
        complements_height_space = 8 * complements.count()

        observation_height_space = 0
        if order.observations is not None:
            observation_height_space = math.ceil(len(order.observations) / 40) * 8
            print("VAI TER QUANTOS PX DE ALTURA: ", math.ceil(len(order.observations) / 40),
                  math.ceil(len(order.observations) / 40) * 7)

        barcode_height_space = 40
        total_height = main_content_height_space + complements_height_space + \
                       observation_height_space + barcode_height_space

        response = {
            'id': order.id, 'table': order.command.table.id,
            'command': order.command_id, 'product': order.product_id, 'name': order.name,
            'image': order.image, 'price': order.price, 'quantity': int(order.quantity),
            'total': order.total, 'status': order.status, 'barcode': order.barcode,
            'checkin_time': order.checkin_time, 'checkin_time_hours': order.checkin_time,
            'checkout_time': format_datetime(order.checkout_time), 'waiting_time': order.waiting_time,
            'implement_time': order.implement_time, 'closed_time': format_datetime(order.closed_time),
            'duration_time': order.duration_time, 'expected_time': order.expected_time,
            'expected_duration': order.expected_duration, 'complements': complement_list,
            'observations': order.observations, 'total_height': total_height,
        }
        return response

    def view(self, request, id):
        self.start_process(request)
        order = Order.objects.filter(pk=int(id))
        if order.count() > 0:
            response_order = self.prepare_order(order[0])
            response_order["base_page"] = 'commands.html'
            response_order["company_name"] = profile.COMPANY_NAME
            response_order["company_logo"] = profile.PATH_COMPANY_LOGO
            response_order["attendant_name"] = request.user.first_name
            return render(request, "order_pdf.html", context={"order": response_order})
        return self.response({"result": False, "object": None, "message": "Object not found"})

    def create_pdf(self, request, id):
        self.start_process(request)
        order = Order.objects.filter(pk=int(id))
        if order.count() > 0:
            response_order = self.prepare_order(order[0])
            response_order["company_name"] = profile.COMPANY_NAME
            response_order["attendant_name"] = request.GET.get("attendant_name")
            respone_content = HttpResponse(content_type='application/pdf')
            return generate_pdf('order_pdf.html',
                                file_object=respone_content,
                                context={'order': response_order})
        return self.response({"result": False, "object": None, "message": "Object not found"})

    def print(self, request):
        self.start_process(request)
        result_print = None
        media_path = "media/orders/"
        resquest_order = json.loads(json.dumps(request.POST))
        order = json.loads(resquest_order.get("orders"))
        reprint = False
        if order.get("items"):
            items = order["items"]
        else:
            items = [order]
            reprint = True
        response_order = {}
        response_order["order"] = {}
        response_order["order"]["items"] = items
        response_order["order"]["total_height"] = 120
        response_order["order"]["company_name"] = profile.COMPANY_NAME
        response_order["order"]["checkin_time"] = datetime.now()
        response_order["order"]["table_id"] = resquest_order.get('table_id')
        response_order["order"]["attendant_name"] = resquest_order.get("attendant_name") \
                                                    or request.user.first_name
        response_order["order"]["order_id"] = order["id"] if not reprint else order["order"]
        response_order["order"]["barcode"] = order["barcode"] if not reprint else ""

        respone_content = HttpResponse(content_type='application/pdf')
        data_object = generate_pdf('order_pdf.html',
                                   file_object=respone_content,
                                   context=response_order).getvalue()  #
        file_name = os.path.join(media_path, f'{str(order["id"])}.pdf' if not reprint else \
            f'reprint-item-order-{str(order["order"])}.pdf')
        with open(file_name, 'wb') as file:
            file.write(data_object)
            command_line = f'cat {file_name} | lpr -P {profile.PRINTER_CONFIG.get("name")}'
            result_print = run_command(command_line)

        return self.response(result_print)

    def reprint(self, request, id=None):
        self.start_process(request)
        order_id = id or request.POST["order_id"]
        order = Order.objects.filter(pk=int(order_id))
        media_path = "media/orders/"
        result_print = None
        if not os.path.exists(media_path):
            os.makedirs(media_path)
        if order.count() > 0:
            file_name = os.path.join(media_path, f"{str(order_id)}.pdf")
            command = f'cat {file_name} | lpr -P {profile.PRINTER_CONFIG.get("name")}'
            print(command)
            result_print = run_command(command)
        return self.response(result_print)

    def printer(self, request, id=None):
        self.start_process(request)
        order_id = id or request.POST["order_id"]
        order = Order.objects.filter(pk=int(order_id))
        media_path = "media/orders/"
        result_print = None
        if not os.path.exists(media_path):
            os.makedirs(media_path)
        if order.count() > 0:
            route_make_pdf = f"http://{request.get_host()}/api/sales/commands/order/pdf/{order_id}"
            file_name = os.path.join(media_path, f"{str(order_id)}.pdf")
            response = requests.get(route_make_pdf, params={"attendant_name": request.user.first_name})
            with open(file_name, 'wb') as file:
                file.write(response.content)
                command = f'cat {file_name} | lpr -P {profile.PRINTER_CONFIG.get("name")}'
                result_print = run_command(command)
        return self.response(result_print)
        # return self.response({"result": True, "object": None, "message": "Order was printed"})
        # return self.response({"result": False, "object": None, "message": "Object not found"})


class ItemController(BaseController):
    model = Item
    extra_fields = []
    extra_names = {}

    def items_by_order(self, request, id, extra_fields=None, is_response=True):
        return super().filter(request,
                              Item,
                              queryset=Item.objects.filter(order=int(id)).order_by('-id'),
                              extra_fields=extra_fields or self.extra_fields,
                              is_response=is_response)


class MenuProductController(BaseController):
    model = Product
    extra_fields = []
    extra_names = {}

    def load_products(self, request, group=None, is_response=True):
        if group:
            return super().filter(request,
                                  self.model,
                                  queryset=Product.objects.filter(group_id=int(group)).order_by('id'),
                                  extra_fields=self.extra_fields,
                                  is_response=is_response)
        else:
            return super().filter(request,
                                  self.model,
                                  queryset=Product.objects.all(),
                                  extra_fields=self.extra_fields,
                                  is_response=is_response)

    def load_by_id(self, request, id, is_response=True):
        return super().filter(request,
                              self.model,
                              queryset=Product.objects.filter(pk=int(id)),
                              extra_fields=self.extra_fields,
                              is_response=is_response)

    def filter_apply(self, request, is_response=True):
        queryset = Product.objects.all()
        verifier = VerifierRequest(request, queryset)
        queryset, total_registers, total_filtered, package, package_size = verifier.verify_filters(['type',
                                                                                                    'code',
                                                                                                    'name',
                                                                                                    'price'])
        response = {}
        if total_filtered > 0:
            response['result'] = True
            response['message'] = "Registros carregados com sucesso!"
            response['object'] = {}
            response['object']['total_registers'] = total_registers
            response['object']['total_filtered'] = total_filtered
            response['object']['package'] = package
            response['object']['package_size'] = package_size
            response['object']['total_packages'] = math.ceil(total_filtered / package_size)
            response['object']['elements'] = super().filter(request,
                                                            Product,
                                                            queryset=queryset,
                                                            extra_fields=self.extra_fields,
                                                            is_response=False)['object']
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

    def verify_search(self):
        search_value = self.request.GET.get('search')
        if search_value is not None:
            search_by = self.request.GET.get('search_by')
            if search_by is not None:
                if self.request.GET.get('search_type') == 'INITIALS':
                    return self.apply_filter({search_by + "__istartswith": search_value})
                else:
                    return self.apply_filter({search_by + "__icontains": search_value})
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
        self.file_name = None
        self.model = None
        self.dependency_model = None

    def get_model(self):
        dict_models = {
            "grupos": {
                "object": Group,
                "dependency": None
            },
            "produtos": {
                "object": Product,
                "dependency": Group
            }
        }
        return dict_models.get(self.file_name, None)

    def load(self, request):
        self.start_process(request)
        response_dict = {}
        communication = CommunicationController()
        if request.GET.get("data"):
            self.file_name = request.GET.get('data')
            self.model = self.get_model()
            self.dependency_model = self.model.get("dependency")
            response_dict = communication.field_search(model=self.model.get("object"),
                                                       filename=self.file_name,
                                                       dependency=self.dependency_model)
        else:
            self.model = Product
            response_dict = communication.field_search(model=self.model)
        return self.response(response_dict)
