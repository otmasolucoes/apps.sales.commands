from django.conf import settings
import os
import sys
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
        with open(json_file, 'r') as f:
            data = f.read()
        return json.loads(data)

    def find_files(self, extension=None):
        list_files = []
        if not extension:
            extension = '*.json'

        path = os.path.dirname('/home/clientes/gigabyte/controller')
        #path = os.path.expanduser("~/")

        for file in glob.glob(os.path.join(path, extension)):
            filename = file.split('/')[-1:][0]
            if filename.split('/')[-1:][0].startswith('card'):
                json_file = file
                list_files.append(json_file)
        return list_files

    def check_update(self, object, model):
        content = self.read_json_file(object)['cardapio']
        self.file_path = object
        update = None
        for item in content:
            update = self.execute_update(item, model)
        if update:
            os.remove(self.file_path)
            print('Objeto atualizado com sucesso!!!')
        else:
            print('Erro,não foi possível efetuar a operação...')

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

    def field_search(self, model=None, extension=None):
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