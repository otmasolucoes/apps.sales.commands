from django.shortcuts import render, HttpResponse
from otma.apps.sales.commands.models import Command, Order



def format_datetime(value):
    from datetime import timezone, datetime, timedelta


    if value is not None:
        datetime_with_timezone = value.astimezone(timezone.utc).strftime('%d/%m/%Y %H:%M:%S')
        print("VEJA DATA:",datetime_with_timezone)
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
        #barcode = BarcodeControlller().create("200421143412")

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

        #print("OLHA A SAIDA:",barcode)
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
            if not os.path.isfile("/media/barcodes/"+order.barcode):
                print("nao tem esse codigo de barras, vou criar")
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

        # print("OLHA A SAIDA:",barcode)
        return render(request, "order.html", context={"order":response})

def print_command(request):
    from django_xhtml2pdf.utils import generate_pdf
    path = os.path.join(BASE_DIR, "static/imagens/")
    # print(request.POST)
    resultado = list(resultado)
    descricao_destinatario = ""
    descricao_periodo = ""

    status = request.POST['filtrar_por_status']
    if status == 'TODOS PROTOCOLOS':
        status = "GERAL"

    if request.POST['filtrar_por_cliente'] != '' and request.POST['filtrar_por_cliente'] != 'TODOS':
        cliente = entidade.objects.get(pk=request.POST['filtrar_por_cliente']).nome_razao

        if request.POST['filtrar_por_status'] == 'ABERTOS':
            descricao_destinatario = descricao_destinatario + u"Relatório de Protocolos em aberto do cliente " + cliente
        else:
            descricao_destinatario = descricao_destinatario + u"Relatório de Protocolos do cliente " + cliente
    else:
        cliente = "TODOS"
        if request.POST['filtrar_por_status'] == 'ABERTOS':
            descricao_destinatario = descricao_destinatario + u"Relatório de protocolos em aberto dos clientes"
        else:
            descricao_destinatario = descricao_destinatario + u"Relatório de protocolos dos clientes"

    if request.POST['filtrar_desde'] != '':
        if request.POST['filtrar_por_operacao'] == 'EMITIDOS':
            # descricao_periodo = descricao_periodo +"Emitidos desde "+request.POST['filtrar_desde']
            descricao_periodo = descricao_periodo + request.POST['filtrar_desde']

        elif request.POST['filtrar_por_operacao'] == 'RECEBIDOS':
            descricao_periodo = descricao_periodo + request.POST['filtrar_desde']

    else:
        pass
        # if request.POST['filtrar_por_operacao'] == 'EMITIDOS':
        #    descricao_periodo = descricao_periodo +" Emitidos"
        #
        # elif request.POST['filtrar_por_operacao'] == 'RECEBIDOS':
        #    descricao_periodo = descricao_periodo +"Recebidos"
        # else:
        #    pass

    if request.POST['filtrar_ate'] != '':
        descricao_periodo = descricao_periodo + u" ATÉ " + request.POST['filtrar_ate']

    data = date.today()
    hora = datetime.datetime.now().strftime("%H:%M")

    resultado = resultado
    novo_result = []

    nova_lista = split_subparts(resultado, 50)
    # print("VEJA QUANTAS PAGINAS DEVEM TER:",len(resultado),"REGISTROS EM ",len(nova_lista)," PAGINA(S)")

    protocolo.index = 0;
    parametros = {
        'protocolos': nova_lista,
        'counter': 0,
        'path_imagens': path,
        'emitido_por': request.user.get_full_name(),
        'descricao_destinatario': descricao_destinatario,
        'filtro_operacao': request.POST['filtrar_por_operacao'].capitalize(),
        'filtro_status': status,
        'filtro_periodo': descricao_periodo,
        'filtro_cliente': cliente,

        'data_emissao': data,
        'hora_emissao': hora
    }
    # context = Context(parametros)
    resp = HttpResponse(content_type='application/pdf')
    result = generate_pdf('protocolo/imprimir_relatorio_simples.html', file_object=resp, context=parametros)
    return result