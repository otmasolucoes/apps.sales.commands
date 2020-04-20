from django.conf.urls import url
from django.urls import path, include
from otma.apps.sales.commands.api import TableController, CommandController, OrderController, MenuGroupController, MenuProductController


urlpatterns = [
    url(r'^load/$', CommandController().load),
    url(r'^table/load/$', TableController().load),
    url(r'^table/open/$', TableController().open),
    url(r'^table/close/$', TableController().close),
    url(r'^order/save/$', OrderController().save),

    url(r'^groups/load/$', MenuGroupController().load_groups),
    url(r'^products/load/$', MenuProductController().load_products),
    url(r'^commands/products/filter/$', MenuProductController().filter_apply),
    url(r'^commands/groups/$', MenuGroupController().all_groups),
    url(r'^commands/orders/load/$', OrderController().load_orders),
    url(r'^commands/orders/(?P<id>[^/]+)/status/(?P<status>[^/]+)/change/$', OrderController().change_orders_status),
    url(r'^commands/(?P<id>[^/]+)/orders/$', OrderController().orders_by_command),
    url(r'^commands/orders/(?P<id>[^/]+)/cancel/$', OrderController().cancel_orders_by_id),
    url(r'^commands/orders/(?P<id>[^/]+)/close/$', OrderController().close_orders_by_id),
    url(r'^commands/(?P<id>[^/]+)/close/$', CommandController().close_commands_by_id),
    url(r'^commands/table/(?P<table>[^/]+)/$', CommandController().commands_by_table),
    url(r'^commands/table/(?P<table>[^/]+)/command/(?P<id>[^/]+)/close/$', CommandController().close_commands_by_table),
    #path(r'user/', include('otma.apps.entities.user.urls')),
]
