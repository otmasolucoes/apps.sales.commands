from django.template.loader import get_template, render_to_string
from django.http import HttpResponse
from django.conf import settings
from conf import profile

from barcode import get_barcode_class, generate
from barcode.writer import ImageWriter

import datetime
import qrcode
import shutil
import django
import json
import glob
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_project.settings')
django.setup()


class CommunicationController:

    def __init__(self):
        self.file_path = None
        self.dependency_model = None

    def read_json_file(self, json_file):
        self.file_path = json_file
        with open(json_file, 'r') as f:
            data = f.read()
        return json.loads(data)

    def find_files(self, filename=None, extension=None):
        list_files = []
        if not extension:
            extension = '.json'
        melinux_path = profile.MELINUX_INTEGRATION_PATH
        if not melinux_path.endswith('/'):
            path = os.path.dirname(melinux_path + '/')
        else:
            path = os.path.dirname(melinux_path)
        if filename:
            file_path = os.path.join(path, filename + extension)
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
        update = None
        for item in content:
            update = self.execute_update(item, model)
        if update:
            os.remove(self.file_path)
            print('Objeto atualizado com sucesso!!!')
            return update
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
            return update
        else:
            print('Erro,não foi possível efetuar a operação...')
            return False

    def load_data(self, item, model):
        try:
            object = model.objects.filter(code=item['code'].strip())
        except:
            object = model.objects.filter(code=item['code'])
        if object.count() > 0:
            object = object[0]
            #print('JÁ EXISTE ESSE CARA NO BANCO.', item['name'])
            self.update(item, object)
        else:
            object = model()
            self.save(item, object)
        return True

    def save(self, item, object):
        for field in item:
            if hasattr(object, field):
                if field == 'group':
                    group = self.dependency_model.objects.filter(code=item[field])
                    if group.count() > 0:
                        group = group[0]
                        object.group = group
                else:
                    try:
                        if field == 'price':
                            item[field] = item[field].replace(',', '.')
                        object.__setattr__(field, item[field].strip())
                    except:
                        print(field)
                        object.__setattr__(field, item[field])
        try:
            object.save()
        except:
            print('DEU ERRO...')
            #raise
            pass

    def update(self, item, object):
        for field in item:
            if hasattr(object, field) and field != 'group':
                try:
                    if field == 'price':
                        item[field] = item[field].replace(',', '.')
                    object.__setattr__(field, item[field].strip())
                except:
                    object.__setattr__(field, item[field])
        try:
            object.save()
        except:
            print('DEU ERRO...')
            #raise
            pass

    def execute_update(self, item, model):
        object = model.objects.filter(code=item['code'].strip())
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

    def field_search(self, model=None, filename=None, extension=None, dependency=None):
        if dependency:
            self.dependency_model = dependency
        if filename:
            files = self.find_files(filename, extension)
            if files:
                for file in files:
                    return self.execute_load(file, model=model)
            else:
                print('Nenhum arquivo de alteração encontrado!!!')
        else:
            files = self.find_files(extension)
            if files:
                for file in files:
                    return self.check_update(file, model=model)
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
        from cups import Connection
        self.connect = Connection()

    def scan(self):
        printers = self.connect.getPrinters()
        for printer in printers:
            print(printer, printers[printer]["device-uri"])
        return printers

    def set_printer(self):
        return list(self.connect.getPrinters())

    def print(self, printer, filename, title=None, *args, **kwargs):
        if not title:
            title = ""
        try:
            self.connect.printFile(printer, filename, title, kwargs)
        except:
            print("Não foi possivel enviar a impressao")


class PDFController:

    def generate_PDF(self, data, filename):
        #import sysconfig
        from weasyprint import HTML
        html_string = render_to_string('order.html', {'order': data})
        pdf_path = f'media/pdf/{filename}'
        #pdf_path = sysconfig.get_paths()['purelib'] + '/otma/apps/sales/commands/templates/pdf/test.pdf'
        pdf = HTML(string=html_string, base_url='http://0.0.0.0:8000/').write_pdf(pdf_path)
        if os.path.isfile(pdf_path):
            printer = PrinterController()
            print('O PDF FOI GERADO PREPARANDO PARA IMPRIMIR...', pdf_path)
            printer.print(profile.PRINTER_CONFIG, pdf_path, title="test_python")
            print('IMPRIMIDO COM SUCESSO!!!')
        else:
            print('ERRO, NÃO CONSEGUI GERAR O PDF E IMPRIMIR...')
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename={}'.format(filename)
        response['Content-Transfer-Encoding'] = 'binary'
        return response


class BarcodeControlller:

    def create(self, code):
        import barcode
        from barcode.writer import ImageWriter
        ean = barcode.get('ean13', code, writer=ImageWriter())
        filename = ean.save('media/barcodes/' + code)
        return filename


class QrCodeController:

    def create(self, data, id):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        value = str(self.id).zfill(12)
        img = qr.make_image(fill_color="black", back_color="white")
        filename = img.save('media/qrcodes/' + id + '.png')
        return filename
