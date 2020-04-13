from otma.apps.sales.commands.utils import render_to_pdf
from django.conf import settings
from django.template.loader import get_template
#from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import View
#from barcode.writer import ImageWriter
from barcode import get_barcode_class
from barcode import generate
from cups import Connection
import os
#import sys
import json
import glob
import shutil
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_project.settings')

django.setup()


class CommunicationController:

    def __init__(self):
        self.file_path = None

    def read_json_file(self, json_file):
        self.file_path = json_file
        with open(json_file, 'r') as f:
            data = f.read()
        return json.loads(data)

    def find_files(self, filename=None, extension=None):
        list_files = []
        if not extension:
            extension = '.json'
        path = os.path.dirname('/home/clientes/gigabyte/controller')
        #path = os.path.expanduser("~/")
        if filename:
            file_path = os.path.join(path, filename)
            if os.path.exists(file_path):
                list_files.append(file_path)
        else:
            for file in glob.glob(os.path.join(path, '*' + extension)):
                filename = file.split('/')[-1:][0]
                if filename.split('/')[-1:][0].startswith('card'):
                    json_file = file
                    list_files.append(json_file)
        return list_files

    def check_update(self, object, model):
        content = self.read_json_file(object)['cardapio']
        #self.file_path = object
        update = None
        for item in content:
            update = self.execute_update(item, model)
        if update:
            os.remove(self.file_path)
            print('Objeto atualizado com sucesso!!!')
        else:
            print('Erro,não foi possível efetuar a operação...')

    def execute_load(self, object, model):
        content = self.read_json_file(object)
        key = list(content)[0]
        for item in content[key]:
            update = self.load_data(item, model)
        if update:
            os.remove(self.file_path)
            print('Objeto salvo com sucesso!!!')
        else:
            print('Erro,não foi possível efetuar a operação...')

    def load_data(self, item, model):
        try:
            object = model.objects.filter(code=int(item['code'].strip()))
        except:
            object = model.objects.filter(code=int(item['code']))
        if object.count() > 0:
            print('JÁ EXISTE ESSE CARA NO BANCO.')
        else:
            object = model()
            for field in item:
                if hasattr(object, field):
                    try:
                        if field == 'price':
                            item[field] = item[field].replace(',', '.')
                        object.__setattr__(field, item[field].strip())
                    except:
                        object.__setattr__(field, item[field])
            try:
                object.save()
            except:
                raise
                #return False
        return True

    def execute_update(self, item, model):
        object = model.objects.filter(code=int(item['code'].strip()))
        if object.count() > 0:
            try:
                object = object[0]
                for field in item:
                    if hasattr(object, field):
                        object.__setattr__(field, item[field].strip())
                object.save()
                return True
            except:
                return False
        else:
            return False

    def field_search(self, model=None, filename=None, extension=None):
        if filename:
            files = self.find_files(filename, extension)
            if files:
                for file in files:
                    self.execute_load(file, model=model)
            else:
                print('Nenhum arquivo de alteração encontrado!!!')
        else:
            files = self.find_files(extension)
            if files:
                for file in files:
                    self.check_update(file, model=model)
            else:
                print('Nenhum arquivo de alteração encontrado!!!')

    def write_txt_file(self, data, file_name, out_folder_path=None, mode='w', delete=False):
        base_dir = settings.BASE_DIR + '/data/fixture/sales/commands'
        if mode:
            mode_open = mode
        folder_path = os.path.dirname('/home/cleiton/clientes')
        if out_folder_path:
            folder_path = out_folder_path
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

        file_dir = os.path.join(base_dir + '/', file_name + '.txt')
        new_file_dir = os.path.join(folder_path, '/' + file_name + '.txt')

        try:
            _data = data
            with open(file_dir, mode_open) as f:
                file_txt = f.write(str(_data))
                print(f'\nArquivo salvo em: {file_dir}')
            if delete:
                newPath = shutil.copy(file_dir, out_folder_path)
                print(f'\nArquivo copiado para: {out_folder_path}')
                os.remove(file_dir)
                print(f'\nArquivo em: {file_dir} deletado com sucesso!!!')
            return file_txt
        except:
            print('Erro!!!')


class PrinterController:

    def __init__(self):
        self.connect = Connection()

    def scan(self):
        printers = self.connect.getPrinters()
        for printer in printers:
            print(printer, printers[printer]["device-uri"])

    def set_printer(self):
        return list(self.connect.getPrinters())

    def print(self, printer, filename, title=None, *args, **kwargs):
        if not title:
            title = ""
        self.connect.printFile(printer, filename, title, kwargs)


class PDFController(View):

    def get(self, request, *args, **kwargs):
        template = get_template('pdf/orders.html')
        context = {
            "invoice_id": 123,
            "customer_name": "John Cooper",
            "amount": 1399.99,
            "today": "Today",
        }
        html = template.render(context)
        pdf = render_to_pdf('pdf/orders.html', context)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = "Order_%s.pdf" %("12341231")
            content = "inline; filename='%s'" %(filename)
            download = request.GET.get("download")
            if download:
                content = "attachment; filename='%s'" %(filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")


class BarcodeControlller:

    def __init__(self):
        self.ean = get_barcode_class('ean13')

    def create(self, code):
        #ean = self.ean(code, writer=ImageWriter())
        #fullname = ean.save('barcode')
        name = generate(self.ean, code, output='barcode_svg')
        return name
