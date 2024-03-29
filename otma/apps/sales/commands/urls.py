from django.conf.urls import url
from django.urls import path, include
from otma.apps.sales.commands.api import TableController, CommandController, \
    OrderController, MenuGroupController, MenuProductController, DatabaseController
from otma.apps.sales.commands.views import command_view_page, order_page

urlpatterns = [
    url(r'^load/$', CommandController().load),
    url(r'^open/$', CommandController().open),
    url(r'^close/(?P<id>[^/]+)/$', CommandController().close_commands_by_id),
    url(r'^table/(?P<table>[^/]+)/command/(?P<id>[^/]+)/close/$', CommandController().close_commands_by_table),
    url(r'^table/(?P<table>[^/]+)/$', CommandController().commands_by_table),
    # url(r'^(?P<code>+)/print/$', CommandController().load),

    url(r'^tables/load/$', TableController().load),
    url(r'^tables/open/$', TableController().open),
    url(r'^tables/close/(?P<id>\d+)/$', TableController().close_by_id),

    url(r'^order/save/$', OrderController().save),
    url(r'^order/print/$', OrderController().print),
    url(r'^order/reprint/(?P<id>\d+)/$', OrderController().reprint),
    url(r'^order/pdf/(?P<id>\d+)/$', OrderController().create_pdf),
    url(r'^order/view/(?P<id>\d+)/$', OrderController().view),
    url(r'^orders/load/$', OrderController().load_orders),
    url(r'^orders/(?P<id>[^/]+)/status/(?P<status>[^/]+)/change/$', OrderController().change_orders_status),
    url(r'^orders/(?P<id>[^/]+)/$', OrderController().orders_by_command),
    url(r'^orders/(?P<id>[^/]+)/cancel/$', OrderController().cancel_orders_by_id),
    url(r'^orders/(?P<id>[^/]+)/close/$', OrderController().close_orders_by_id),
    url(r'^orders/item/(?P<id>[^/]+)/status/(?P<status>[^/]+)/change/$', OrderController().change_status_item),

    url(r'^groups/$', MenuGroupController().all_groups),
    url(r'^groups/load/$', MenuGroupController().load_groups),
    url(r'^products/load/$', MenuProductController().load_products),
    url(r'^products/filter/$', MenuProductController().filter_apply),

    # url(r'^pdf/$', PDFController().get),

    url(r'^database/load/$', DatabaseController().load),
    # path(r'user/', include('otma.apps.entities.user.urls')),
]
