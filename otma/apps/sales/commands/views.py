from django.shortcuts import render, HttpResponse
from django.template.loader import render_to_string
from otma.apps.sales.commands.models import Command, Order, Complement
from otma.apps.sales.commands.service import PDFController
import os.path


def format_datetime(value):
    from datetime import timezone, datetime, timedelta
    if value is not None:
        datetime_with_timezone = value.astimezone(timezone.utc).strftime('%d/%m/%Y %H:%M:%S')
        return datetime_with_timezone
        #return value.strftime("%d/%m/%Y, %H:%M:%S")
    else:
        return None

def commands_page(request):
    return render(request, "commands.html", {'base_page': 'new_base_page.html'})

def command_view_page(request, code):
    command = Command.objects.filter(code=int(code))
    if command.count() > 0:
        command = command[0]

        """response = {
            'id':command.id,
            'code':command.code,
            'table':command.table,
            'status':command.status,
            'attendant':command.attendant,
            'client_document':command.client_document,
            'branch':command.branch,
            'checkin_time':command.checkin_time,
            'checkout_time':command.checkout_time,
            'permanence_time':command.permanence_time,
            'peoples':command.peoples,
            'total':command.total,
            'orders':[],
            #'barcode':barcode
        }"""

        return render(request, "order.html", context=response)

def order_page(request, id):
    import os.path
    order = Order.objects.filter(pk=int(id))
    if order.count() > 0:
        order = order[0]
        barcode = order.barcode
        if barcode is None:
            barcode = order.create_barcode()
        else:
            if not os.path.isfile("/media/barcodes/" + order.barcode):
                barcode = order.create_barcode()

        response = {
            'id':order.id,
            'command':order.command_id,
            'product':order.product_id,
            'product_name':order.product_name,
            'product_image':order.product_image,
            'product_price':order.product_price,
            'quantity':order.quantity,
            'total':order.total,

            'checkin_time':order.checkin_time,
            'checkin_time_hours':order.checkin_time, #.strftime("%H:%M"),
            'checkout_time':format_datetime(order.checkout_time),
            'waiting_time':order.waiting_time,
            'implement_time':order.implement_time,
            'closed_time':format_datetime(order.closed_time),
            'duration_time':order.duration_time,
            'expected_time':order.expected_time,
            'expected_duration':order.expected_duration,

            'barcode':order.barcode,
            'status':order.status,
            'observations':order.observations,
        }
        return render(request, "order.html", context={"order":response})
