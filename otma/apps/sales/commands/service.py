from django.template.loader import get_template, render_to_string
from django.http import HttpResponse
from django.conf import settings
from conf import profile
from otma.apps.sales.commands.models import Group, Product
from otma.apps.core.communications.api import BaseController
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


class CommunicationController(BaseController):

    def __init__(self):
        self.file_path = None
        self.dependency_model = None

    def read_json_file(self, json_file):
        self.file_path = json_file
        with open(json_file, 'r') as f:
            data = f.read()
        return json.loads(data)

    def find_files(self, data_name, extension=".json"):
        melinux_path = profile.MELINUX_INTEGRATION_PATH
        if not melinux_path.endswith('/'):
            melinux_path = os.path.dirname(melinux_path + '/')
        for json_file in glob.glob(os.path.join(melinux_path, '*' + extension)):
            filename = json_file.split('/')[-1:][0]
            if filename.split('/')[-1:][0].startswith(data_name):
                return json_file
        return None

    def load_data(self, item, model, code_group=None):
        object = model.objects.filter(code=item['code']).first()
        if not object:
            object = model()
        return self.save(item, object, code_group)

    def save(self, item, object, code_group):
        for field in item:
            if hasattr(object, field):
                if code_group:
                    object.name = item["description"]
                    object.group = Group.objects.filter(code=code_group).first()
                if field == 'price':
                    item[field] = item[field].replace(',', '.')
                object.__setattr__(field, item[field])
        return self.execute(object, object.save)

    def export_data(self, data_name):
        load_dict = {
            "object": []
        }
        content = self.read_json_file(self.find_files(data_name=data_name))[data_name]
        for item in content:
            group_load = self.load_data(item, Group)
            group_load["object"]["products"] = []
            for sub_item in item["products"]:
                product_load = self.load_data(sub_item, Product, item["code"])
                group_load["object"]["products"].append(product_load["object"])
            load_dict["object"].append(group_load["object"])
        load_dict["result"] = group_load["result"]
        load_dict["message"] = group_load["message"]
        if load_dict["result"]:
            os.remove(self.file_path)
            print('Objeto salvo com sucesso!!!')

        return load_dict

    def write_txt_file(self, data, file_name, out_folder_path=None, mode='w', delete=False):
        base_dir = settings.BASE_DIR + '/data/fixture/sales/commands'
        if mode:
            mode_open = mode
        folder_path = os.path.dirname(profile.MELINUX_INTEGRATION_PATH)
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
            return False


class PrinterController(object):

    def __init__(self):
        from cups import Connection
        self.connect = Connection()
        self.printers = self.connect.getPrinters()

    def scan(self):
        for printer in self.printers:
            print(printer, self.printers[printer]["device-uri"])

    def get_printers(self):
        return list(self.printers)

    def print(self, printer, filename, title=None, *args, **kwargs):
        if not title:
            title = ""
        self.connect.printFile(printer, filename, title, kwargs)


class PDFController(object):

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


class BarcodeControlller(object):

    def create(self, code):
        import barcode
        from barcode.writer import ImageWriter
        ean = barcode.get('ean13', code, writer=ImageWriter())
        filename = ean.save('media/barcodes/' + code)
        return filename


class QrCodeController(object):

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
