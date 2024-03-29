import os
import barcode
from django.utils.translation import ugettext_lazy as _
from django.utils.deconstruct import deconstructible
from django.conf import settings
from django.db import models
from decimal import Decimal
from barcode.writer import ImageWriter


PRODUCT_TYPE = (
    ('NORMAL', 'NÃO PODE TER ADICIONAIS'),
    ('ADDABLE', 'PODE TER ADICIONAIS'),
    ('ADDITIONAL', 'É UM ADICIONAL'),
)

TABLE_STATUS = (
    ('ACTIVE', 'ATIVA'),
    ('WAITING', 'AGUARDANDO'),
    ('CLOSED', 'FECHADA'),
)

COMMAND_STATUS = (
    ('OPEN', 'ABERTA'),
    ('CLOSED', 'FECHADA'),
)

ORDER_STATUS = (
    ('SENT', 'ENVIADO'),
    ('FINISHED', 'FINALIZADO'),
)

PREPARATION_STATUS = (
    ('WAITING', 'AGUARDANDO'),
    ('IN_PROGRESS', 'EM ANDAMENTO'),
    ('READY', 'PRONTO'),
    ('CLOSED', 'ENTREGUE'),
    ('CANCELED', 'CANCELADO'),
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


class Group(models.Model):

    class Meta:
        db_table = 'apps_sales_commands_group'
        verbose_name = _('Grupo')
        verbose_name_plural = _('Grupos')

    code = models.CharField(_('Código do grupo'), max_length=10, null=False, blank=False, unique=True,
                            error_messages=settings.ERRORS_MESSAGES)
    name = models.CharField(_('Nome do grupo'), max_length=50, null=False, blank=False, unique=False,
                            error_messages=settings.ERRORS_MESSAGES)
    description = models.CharField(_('Descrição do grupo'), max_length=200, null=True, blank=True, unique=False,
                                   error_messages=settings.ERRORS_MESSAGES)
    image = models.ImageField(max_length=100, upload_to=PathAndRename("images/commands/groups/"), null=True, blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):

    class Meta:
        db_table = 'apps_sales_commands_product'
        verbose_name = _('Produto')
        verbose_name_plural = _('Produtos')

    group = models.ForeignKey(Group, null=True, blank=True, on_delete=models.DO_NOTHING)
    type = models.CharField(_('Tipo do produto'), max_length=10, null=True, blank=True, default='NORMAL',
                            choices=PRODUCT_TYPE, error_messages=settings.ERRORS_MESSAGES)
    code = models.CharField(_('Código do produto'), max_length=10, null=False, blank=False, unique=True,
                            error_messages=settings.ERRORS_MESSAGES)
    name = models.CharField(_('Nome do produto'), max_length=50, null=False, blank=False, unique=True,
                            error_messages=settings.ERRORS_MESSAGES)
    description = models.CharField(_('Descrição do produto'), max_length=200, null=True, blank=True,
                                   error_messages=settings.ERRORS_MESSAGES)
    price = models.DecimalField(max_digits=9, decimal_places=2, blank=True, null=True)
    image = models.ImageField(max_length=256, upload_to=PathAndRename("images/commands/products/"), null=True,
                              blank=True)
    have_promotion = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def get_image(self):
        return str(self.image)


class Table(models.Model):
    class Meta:
        db_table = 'apps_sales_commands_tables'
        verbose_name = _('Mesa')
        verbose_name_plural = _('Mesas')

    code = models.CharField(_('Número da mesa'), max_length=10, null=False, blank=False, unique=True,
                            error_messages=settings.ERRORS_MESSAGES)
    area = models.CharField(_('Identificação da area'), max_length=10, null=False, blank=False,
                            error_messages=settings.ERRORS_MESSAGES)
    status = models.CharField(_('Status da mesas'), max_length=20, default='CLOSED', choices=TABLE_STATUS,
                              null=True, blank=True, error_messages=settings.ERRORS_MESSAGES)
    total = models.DecimalField(max_digits=9, decimal_places=2, null=False, default=0)
    capacity = models.IntegerField(null=True, blank=True, default=4)

    def __str__(self):
        return f"MESA {self.code} ({self.area})"

    def commands(self):
        return []


class Command(models.Model):

    class Meta:
        db_table = 'apps_sales_commands_command'
        verbose_name = _('Comanda')
        verbose_name_plural = _('Comandas')

    code = models.CharField(_('Número da comanda'), max_length=10, null=False, blank=False, unique=True,
                            error_messages=settings.ERRORS_MESSAGES)
    table = models.ForeignKey(Table, on_delete=models.DO_NOTHING, null=True, blank=True,
                              error_messages=settings.ERRORS_MESSAGES)
    status = models.CharField(_('Status da comanda'), max_length=20, default='OPEN', choices=COMMAND_STATUS,
                              null=True, blank=True, error_messages=settings.ERRORS_MESSAGES)
    attendant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    client_document = models.CharField(_('Número de documento'), max_length=20, null=True, blank=True, unique=False,
                                       error_messages=settings.ERRORS_MESSAGES)
    branch = models.CharField(_('Código da loja'), max_length=2, null=False, blank=False,
                              error_messages=settings.ERRORS_MESSAGES)
    checkin_time = models.DateTimeField(_('Criação da comanda'), null=True, auto_now_add=True)
    checkout_time = models.DateTimeField(_('Fechamento da comanda'), null=True, blank=True)
    permanence_time = models.DurationField(null=True, blank=True)
    peoples = models.IntegerField(null=True, blank=True)
    total = models.DecimalField(max_digits=9, decimal_places=2, blank=False, null=False, default=0)

    def __str__(self):
        return f"COMANDA {self.code}"


class Order(models.Model):

    class Meta:
        db_table = 'apps_sales_commands_order'
        verbose_name = _('Pedido')
        verbose_name_plural = _('Pedidos')

    command = models.ForeignKey(Command, on_delete=models.DO_NOTHING)
    total = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    checkin_time = models.DateTimeField(_('Entrada de pedido'), null=True, auto_now_add=True)
    checkout_time = models.DateTimeField(_('Saída de pedido'), null=True, blank=True)
    barcode = models.CharField(_('Código de barras'), max_length=20, null=True, blank=True,
                               error_messages=settings.ERRORS_MESSAGES)
    status = models.CharField(_('Status'), max_length=20, default='SENT', choices=ORDER_STATUS, null=True,
                              blank=True, error_messages=settings.ERRORS_MESSAGES)

    def show_options(self):
        return False

    def create_barcode(self):
        """
        checkin_year = str(self.checkin_time.year)[2:]
        checkin_month = "%.2d" % (self.checkin_time.month)
        checkin_day = "%.2d" % (self.checkin_time.day)
        checkin_hour = "%.2d" % (self.checkin_time.hour)
        checkin_minute = "%.2d" % (self.checkin_time.minute)
        checkin_second = "%.2d" % (self.checkin_time.second)
        value = checkin_year + checkin_month + checkin_day + checkin_hour + checkin_minute + checkin_second
        """
        value = str(self.id).zfill(12)
        ean = barcode.get('ean13', value, writer=ImageWriter())
        filename = ean.save(f"media/barcodes/{value}")
        self.barcode = f"{value}.png"
        super(Order, self).save()
        return filename

    def save(self, *args, **kwargs):
        if not os.path.exists("media/barcodes/"):
            os.makedirs("media/barcodes/")
        if not os.path.exists("media/orders/"):
            os.makedirs("media/orders/")
        # self.total = Decimal(self.quantity) * Decimal(self.price)
        # self.command.total = self.command.total + self.total
        super(Order, self).save(*args, **kwargs)
        if self.barcode is None:
            self.create_barcode()


class Item(models.Model):

    class Meta:
        db_table = 'apps_sales_commands_item'
        verbose_name = _('Item')
        verbose_name_plural = _('Items')

    order = models.ForeignKey(Order, on_delete=models.DO_NOTHING)
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING)
    name = models.CharField(_('Nome do produto'), max_length=50, null=False, blank=False, unique=False,
                            error_messages=settings.ERRORS_MESSAGES)
    description = models.CharField(_('Descrição do produto'), max_length=200, null=True, blank=True,
                                   error_messages=settings.ERRORS_MESSAGES)
    price = models.DecimalField(max_digits=9, decimal_places=2, blank=True, null=True)
    quantity = models.DecimalField(max_digits=5, decimal_places=2, blank=False, null=False, default=1)
    image = models.CharField(_('Imagem do produto'), max_length=256, null=True, blank=True, unique=False,
                             error_messages=settings.ERRORS_MESSAGES)
    checkin_time = models.DateTimeField(_('Entrada do item'), null=True, auto_now_add=True)
    waiting_time = models.DurationField(null=True, blank=True)
    implement_time = models.DurationField(null=True, blank=True)
    duration_time = models.DurationField(null=True, blank=True)
    expected_time = models.DateTimeField(_('Término previsto'), null=True, blank=True)
    expected_duration = models.DurationField(null=True, blank=True)
    closed_time = models.DurationField(null=True, blank=True)
    was_sent = models.BooleanField(default=False)
    status = models.CharField(_('Status'), max_length=20, default='WAITING', choices=PREPARATION_STATUS, null=True,
                              blank=True, error_messages=settings.ERRORS_MESSAGES)
    observations = models.TextField('Observações', null=True, blank=True)


class Complement(models.Model):

    class Meta:
        db_table = 'apps_sales_commands_complement'
        verbose_name = _('Complemento')
        verbose_name_plural = _('Complementos')

    command = models.ForeignKey(Command, on_delete=models.DO_NOTHING)
    order = models.ForeignKey(Order, on_delete=models.DO_NOTHING)
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING)
    code = models.CharField(_('Código do produto'), max_length=10, null=False, blank=False, unique=False,
                            error_messages=settings.ERRORS_MESSAGES)
    name = models.CharField(_('Nome do produto'), max_length=50, null=False, blank=False, unique=False,
                            error_messages=settings.ERRORS_MESSAGES)
    price = models.DecimalField(max_digits=9, decimal_places=2, blank=True, null=True)
    quantity = models.DecimalField(max_digits=5, decimal_places=2, blank=False, null=False, default=1)

