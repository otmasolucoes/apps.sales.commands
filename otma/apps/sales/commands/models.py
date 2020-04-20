from django.utils.translation import ugettext_lazy as _
from django.utils.deconstruct import deconstructible

from django.conf import settings
from django.db import models
from decimal import Decimal
import os


STATUS_OF_TABLE = (
    ('ACTIVE', 'ATIVA'),
    ('WAITING', 'AGUARDANDO'),
    ('CLOSED', 'FECHADA'),
)


STATUS_OF_COMMAND = (
    ('OPEN', 'ABERTA'),
    ('CLOSED', 'FECHADA'),
)

STATUS_OF_ORDER = (
    ('WAITING', 'AGUARDANDO'),
    ('IN_PROGRESS', 'EM ANDAMENTO'),
    ('READY', 'PRONTO'),
    ('CLOSED', 'ENTREGUE'),
    ('CANCELED', 'CANCELADO'),
)

TYPE_OF_PRODUCT = (
    ('NORMAL', 'NÃO PODE TER ADICIONAIS'),
    ('ADDABLE', 'PODE TER ADICIONAIS'),
    ('ADDITIONAL', 'É UM ADICIONAL'),
)


@deconstructible
class PathAndRename(object):

    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        filename = '{}.{}'.format(instance.code, ext)
        file_path = os.path.join(settings.MEDIA_ROOT + '/' + self.path, filename)
        if os.path.exists(file_path):
            os.remove(file_path)

        return os.path.join(self.path, filename)

class Table(models.Model):
    class Meta:
        db_table = 'apps_sales_commands_tables'
        verbose_name = _('Mesa')
        verbose_name_plural = _('Mesas')

    code = models.CharField(_('Número da mesa'), max_length=10, null=False, blank=False, unique=True, error_messages=settings.ERRORS_MESSAGES)
    area = models.CharField(_('Identificação da area'), max_length=10, null=False, blank=False, error_messages=settings.ERRORS_MESSAGES)
    status = models.CharField(_('Status da mesas'), max_length=20, default='CLOSED', choices=STATUS_OF_TABLE, null=True, blank=True, error_messages=settings.ERRORS_MESSAGES)
    capacity = models.IntegerField(null=True, blank=True, default=4)

    def __str__(self):
        return "MESA"+self.code+" ("+self.area+")"


class Group(models.Model):

    class Meta:
        db_table = 'apps_sales_commands_group'
        verbose_name = _('Grupo')
        verbose_name_plural = _('Grupos')

    code = models.CharField(_('Código do grupo'), max_length=10, null=False, blank=False, unique=True, error_messages=settings.ERRORS_MESSAGES)
    name = models.CharField(_('Nome do grupo'), max_length=50, null=False, blank=False, unique=False, error_messages=settings.ERRORS_MESSAGES)
    description = models.CharField(_('Descrição do grupo'), max_length=200, null=True, blank=True, unique=False, error_messages=settings.ERRORS_MESSAGES)
    image = models.ImageField(max_length=100, upload_to=PathAndRename("images/commands/groups/"), null=True, blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    class Meta:
        db_table = 'apps_sales_commands_product'
        verbose_name = _('Produto')
        verbose_name_plural = _('Produtos')

    group = models.ForeignKey(Group, null=True, blank=True, on_delete=models.DO_NOTHING)
    type = models.CharField(_('Tipo do produto'), max_length=10, null=True, blank=True, default='NORMAL', choices=TYPE_OF_PRODUCT, error_messages=settings.ERRORS_MESSAGES)
    code = models.CharField(_('Código do produto'), max_length=10, null=False, blank=False, unique=True, error_messages=settings.ERRORS_MESSAGES)
    name = models.CharField(_('Nome do produto'), max_length=50, null=False, blank=False, unique=True, error_messages=settings.ERRORS_MESSAGES)
    description = models.CharField(_('Descrição do produto'), max_length=200, null=True, blank=True, error_messages=settings.ERRORS_MESSAGES)

    price = models.DecimalField(max_digits=9, decimal_places=2, blank=True, null=True)
    image = models.ImageField(max_length=256, upload_to=PathAndRename("images/commands/products/"), null=True, blank=True)
    have_promotion = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def get_image(self):
        return str(self.image)


class Command(models.Model):
    class Meta:
        db_table = 'apps_sales_commands_command'
        verbose_name = _('Comanda')
        verbose_name_plural = _('Comandas')

    code = models.CharField(_('Número da comanda'), max_length=10, null=False, blank=False, unique=True, error_messages=settings.ERRORS_MESSAGES)
    table = models.ForeignKey(Table, on_delete=models.DO_NOTHING, null=True, blank=True, error_messages=settings.ERRORS_MESSAGES)
    status = models.CharField(_('Status da comanda'), max_length=20, default='OPEN', choices=STATUS_OF_COMMAND, null=True, blank=True, error_messages=settings.ERRORS_MESSAGES)
    attendant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    client_document = models.CharField(_('Número de documento'), max_length=20, null=True, blank=True, unique=False, error_messages=settings.ERRORS_MESSAGES)
    branch = models.CharField(_('Código da loja'), max_length=2, null=False, blank=False, error_messages=settings.ERRORS_MESSAGES)
    checkin_time = models.DateTimeField(_('Entrada de pedido'), null=True, auto_now_add=True)
    checkout_time = models.DateTimeField(_('Saída de pedido'), null=True, blank=True)
    permanence_time = models.DurationField(null=True, blank=True)
    peoples = models.IntegerField(null=True, blank=True)
    total = models.DecimalField(max_digits=9, decimal_places=2, blank=False, null=False, default=0)

    def __str__(self):
        return "COMANDA "+self.code


class Order(models.Model):
    class Meta:
        db_table = 'apps_sales_commands_order'
        verbose_name = _('Pedido')
        verbose_name_plural = _('Pedidos')

    command = models.ForeignKey(Command, on_delete=models.DO_NOTHING)
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING)
    product_name = models.CharField(_('Nome do produto'), max_length=50, null=False, blank=False, unique=False, error_messages=settings.ERRORS_MESSAGES)
    product_image = models.CharField(_('Imagem do produto'), max_length=256, null=True, blank=True, unique=False, error_messages=settings.ERRORS_MESSAGES)
    product_price = models.DecimalField(max_digits=9, decimal_places=2, blank=True, null=True)
    quantity = models.DecimalField(max_digits=5, decimal_places=2, blank=False, null=False, default=1)
    total = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    checkin_time = models.DateTimeField(_('Entrada de pedido'), null=True, auto_now_add=True)
    checkout_time = models.DateTimeField(_('Saída de pedido'), null=True, blank=True)
    waiting_time = models.DurationField(null=True, blank=True)
    implement_time = models.DurationField(null=True, blank=True)
    closed_time = models.DurationField(null=True, blank=True)
    duration_time = models.DurationField(null=True, blank=True)
    expected_time = models.DateTimeField(_('Término previsto'), null=True, blank=True)
    expected_duration = models.DurationField(null=True, blank=True)


    status = models.CharField(_('Status'), max_length=20, default='WAITING', choices=STATUS_OF_ORDER, null=True, blank=True, error_messages=settings.ERRORS_MESSAGES)
    observations = models.TextField('Observações', null=True, blank=True)

    def show_options(self):
        return False

    def save(self, *args, **kwargs):
        self.total = Decimal(self.quantity) * Decimal(self.product_price)
        self.command.total = self.command.total + self.total
        super(Order, self).save(*args, **kwargs)


class Additional(models.Model):
    class Meta:
        db_table = 'apps_sales_commands_additional'
        verbose_name = _('Adicional')
        verbose_name_plural = _('Adicionais')

    command = models.ForeignKey(Command, on_delete=models.DO_NOTHING)
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING)
    order = models.ForeignKey(Order, on_delete=models.DO_NOTHING)
