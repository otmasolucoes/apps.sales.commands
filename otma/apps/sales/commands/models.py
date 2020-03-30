from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.core.files.base import ContentFile
from django.utils.deconstruct import deconstructible
import sysconfig
import datetime
import requests
import base64
import json
import os

STATUS_OF_COMMAND = (
    ('OPEN', 'Aberto'),
    ('CLOSED', 'Fechado'),
)

STATUS_OF_ORDER = (
    ('AWAITING', 'Aguardando'),
    ('IN_PROGRESS', 'Em andamento'),
    ('READY', 'Pronto'),
    ('CANCELED', 'Cancelado'),
)


@deconstructible
class PathAndRename(object):

    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        filename = '{}.{}'.format(instance.code, ext)
        file_path = os.path.join(settings.MEDIA_ROOT + '/' + self.path, filename)
        print(file_path)
        if os.path.exists(file_path):
            print('JÁ EXISTE UMA IMAGEM COM ESSE NOME,VOU REMOVER ESSA E CRIAR UMA NOVA.')
            os.remove(file_path)

        return os.path.join(self.path, filename)


class Group(models.Model):

    class Meta:
        db_table = 'apps_sales_commands_group'
        verbose_name = _('Grupo')
        verbose_name_plural = _('Grupos')

    #upload_path = 'images/'
    code = models.CharField(_('Código do grupo'), max_length=10, null=False, blank=False, unique=True, error_messages=settings.ERRORS_MESSAGES)
    name = models.CharField(_('Nome do grupo'), max_length=50, null=False, blank=False, unique=False, error_messages=settings.ERRORS_MESSAGES)
    description = models.CharField(_('Descrição do grupo'), max_length=200, null=True, blank=True, unique=False, error_messages=settings.ERRORS_MESSAGES)
    image = models.ImageField(max_length=100, upload_to=PathAndRename("images/commands/groups/"), null=True, blank=True)
    #image_url = models.URLField(null=True, blank=True, default='')

    """def save(self, *args, **kwargs):
        if self.image:
            print('OLHA AE A IMAGEM: ', self.image)
        if self.image_url != '' and self.image_url != None:
            print('SOU NONE OU ""')
            file_save_dir = self.upload_path
            filename = self.image_url.split('/')[-1]
            filepath = os.path.join(file_save_dir, str(self.code) + '.' + filename.split('.')[-1])

            response = requests.get(self.image_url)
            with open(settings.MEDIA_ROOT + "/" + filepath, 'wb') as file:
                file.write(response.content)

            self.image = filepath
            self.image_url = ''
        super().save()"""


class Product(models.Model):
    class Meta:
        db_table = 'apps_sales_commands_product'
        verbose_name = _('Produto')
        verbose_name_plural = _('Produtos')

    group = models.ForeignKey(Group, null=True, blank=True, on_delete=models.DO_NOTHING)
    type = models.CharField(_('Tipo do produto'), max_length=2, null=True, blank=True, default='', error_messages=settings.ERRORS_MESSAGES)
    code = models.CharField(_('Código do produto'), max_length=10, null=False, blank=False, unique=True, error_messages=settings.ERRORS_MESSAGES)
    name = models.CharField(_('Nome do produto'), max_length=50, null=False, blank=False, unique=True, error_messages=settings.ERRORS_MESSAGES)
    description = models.CharField(_('Descrição do produto'), max_length=200, null=True, blank=True, error_messages=settings.ERRORS_MESSAGES)
    price = models.FloatField(_("Preço do produto"), max_length=10, null=True, blank=True)
    image = models.ImageField(max_length=100, upload_to=PathAndRename("images/commands/products/"), null=True, blank=True)
    #image_url = models.URLField(null=True, blank=True, default='')


class Command(models.Model):
    class Meta:
        db_table = 'apps_sales_commands_command'
        verbose_name = _('Comanda')
        verbose_name_plural = _('Comandas')

    official_document = models.CharField(_('Número de documento'), max_length=20, null=True, blank=True, unique=False, error_messages=settings.ERRORS_MESSAGES)
    branch = models.CharField(_('Código da loja'), max_length=2, null=False, blank=False, error_messages=settings.ERRORS_MESSAGES)
    waiter = models.CharField(_('Identificação do garçom'), max_length=2, null=False, blank=False, error_messages=settings.ERRORS_MESSAGES)
    number = models.CharField(_('Número da comanda'), max_length=10, null=False, blank=False, unique=True, error_messages=settings.ERRORS_MESSAGES)
    enter = models.DateTimeField(_('Entrada de pedido'), null=True, auto_now_add=True)
    exit = models.DateTimeField(_('Saída de pedido'), null=True, blank=True)
    table = models.CharField(_('Identificação da mesa'), max_length=10, null=False, blank=False, error_messages=settings.ERRORS_MESSAGES)
    status = models.CharField(_('Status da comanda'), max_length=20, default='OPEN', choices=STATUS_OF_COMMAND, null=True, blank=True, error_messages=settings.ERRORS_MESSAGES)


class Order(models.Model):
    class Meta:
        db_table = 'apps_sales_commands_order'
        verbose_name = _('Pedido')
        verbose_name_plural = _('Pedidos')

    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING)
    command = models.ForeignKey(Command, on_delete=models.DO_NOTHING)
    enter = models.DateTimeField(_('Entrada de pedido'), null=True, auto_now_add=True)
    exit = models.DateTimeField(_('Saída de pedido'), null=True, blank=True)
    quantity = models.CharField(_('Quantidade'), max_length=2, null=False, blank=False, error_messages=settings.ERRORS_MESSAGES)
    note = models.TextField('Complemento', null=True, blank=True)
    status = models.CharField(_('Status do pedido'), max_length=20, default='AWAITING', choices=STATUS_OF_ORDER, null=True, blank=True, error_messages=settings.ERRORS_MESSAGES)


class Additional(models.Model):
    class Meta:
        db_table = 'apps_sales_commands_additional'
        verbose_name = _('Adicional')
        verbose_name_plural = _('Adicionais')

    command = models.ForeignKey(Command, on_delete=models.DO_NOTHING)
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING)
    order = models.ForeignKey(Order, on_delete=models.DO_NOTHING)
