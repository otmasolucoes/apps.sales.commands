Vue.filter('titlecase', function(value){
  if(value){
    var sentence = value.toLowerCase().split(" ");
    for(var i = 0; i< sentence.length; i++){
      if(sentence[i].length > 2){
        sentence[i] = sentence[i][0].toUpperCase() + sentence[i].slice(1);
      }
    }
   return sentence.join(" ");
  }

  else{
    return "invalid"
  }
})

Vue.filter('uppercase', function(value){
  if(value){
    return value.toUpperCase();
  }

  else{
    return "invalid"
  }
})

Vue.filter('lowercase', function(value){
  if(value){
    return value.toUpperCase();
  }

  else{
    return "invalid"
  }
})

Vue.filter('format_money', function(value){
  let result = "";
  value = parseFloat(value);
  if(value >= 0){
    result = (value).toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
    result = result.replace(".","#").replace(/,/g, ".").replace("#",",");
    return result;
  }
  else{
    return "invalid"
  }
})


Vue.component('app_map', {
  props: ['id', 'address'],
  data: function () {
    return {
      map_url: null,
    }
  },

  created: function(){
    this.view_location();
  },

  methods:{

    view_location: function () {
      //alert("opa opa to indo")
      var latlon = this.address.latitude + "," + this.address.longitude;
      this.map_url = "https://maps.googleapis.com/maps/api/staticmap?center="+latlon+"&zoom=14&sensor=false&key=AIzaSyA5pZBwmGJJ8f8POml7158nP2yxgvFtoXA";
      //document.getElementById(this.id).innerHTML = "<img src='"+img_url+"'>";
    }
  },

  template: `
    <div>
      ID: {{ id }} - {{ map_url }}
      <div id="map_container">

      </div>

      <div>
      Endereço: {{ address }}
      </div>
    </div>
  `
})


var app = new Vue({
  el: '#app',
  mixins: [base_communications],
  data: function() {
    return {
      user: {
        history:[],
        cupons:[
          {'code':'', 'type':'DISCOUNT', 'name':'DESCONTO 10%', 'expired_date':'', 'complement':'PRIMEIRA COMPRA'},
          {'code':'', 'type':'DISCOUNT', 'name':'DESCONTO 5%', 'expired_date':'15/09/2020', 'complement':''},
          {'code':'', 'type':'DISCOUNT', 'name':'ENTREGA GRÁTIS', 'expired_date':'30/07/2020', 'complement':''},
        ],
      },

      controls:{
        location:{
          map: null,
          company_location: { lat: -20.374468, lng: -40.306149 },
          latitude:null,
          longitude:null,
          possible_addresses:[],

          address:{
            marker:null,
            latitude:null,
            longitude:null,
            street_name:null,
            address_number:null,
            neighborhood_name:null,
            city_name:null,
            state_name:null,
            state_initials:null,
            country_name:null,
            country_initials:null,
            postal_code:null,
            complement:null,
          }
        },
        payment:{
          method:null,
        },
        
        styles: {
          themes:{
            active: {
              'name':'Elegancia',
              'header':{'background':'#ddd', 'color':'#555'},
              'header_division':{'border-bottom':'2px solid #b36363'},
              'order_decoration':{'background-color':'rgba(28, 28, 28, 0.9)'},
              'product_list':{'background':'#ddd','color':'#666'}
            },

            options:[
              {
                'name':'Connect',
                'header':{'background':'#b22222', 'color':'#ffffff'},
                'header_division':{'border-bottom':'2px solid #b222222'},
                'order_decoration':{'background-color':'rgba(125, 76, 25, 0.9)'},
                'product_list':{'background':'rgb(255, 131, 0)'}
              },

              {
                'name':'Elegancia',
                'header':{'background':'#b22222', 'color':'#ffffff'},
                'header_division':{'border-bottom':'2px solid #b36363'},
                'order_decoration':{'background-color':'rgba(28, 28, 28, 0.9)'},
                'product_list':{'background':'#b22222'}
              },

              {
                'name':'Energia',
                'header':{'background':'#009000', 'color':'#ffffff'},
                'header_division':{'border-bottom':'2px solid #2e6b23'},
                'order_decoration':{'background-color':'rgba(13, 77, 13, 0.9)'},
                'product_list':{'background':'#009000'}
              },

              {
                'name':'Paz',
                'header':{'background':'#191f40', 'color':'#ffffff'},
                'header_division':{'border-bottom':'2px solid #1d2c60'},
                'order_decoration':{'background-color':'rgba(25, 31, 64, 0.9)'},
                'product_list':{'background':'#191f40'}
              },
            ]
          }
        },
        clock: null,
        screen: {
          width: window.innerWidth,
          height: window.screen.height,
          fullscreen_mode: false,
        },
        page:{
          current:"menu",
        },

        urls: {
          groups: '/api/sales/commands/groups/load/',
        }
      },

      forms: {
        address:{
          latitude:"-20.3510301",
          longitude:"-40.2845386",
          street_name:"RUA BRASÍLIA",
          address_number:"50",
          neighborhood_name:"ITAPUÃ",
          city_name:"VILA VELHA",
          state_name:"ESPÍRITO SANTO",
          state_initials:"ES",
          country_name:"BRASIL",
          country_initials:"BR",
          postal_code:"29.101-730",
          complement:"7º ANDAR",

          /*latitude:null,
          longitude:null,
          street_name:null,
          address_number:null,
          neighborhood_name:null,
          city_name:null,
          state_name:null,
          state_initials:null,
          country_name:null,
          country_initials:null,
          postal_code:null,
          complement:null,*/
        },

        command:{
          change_client_name:false,
        },

        search:{
          value: null,
          field: 'name',
          type: 'contains',
        },

        order:{
          conditions:{
            payments_methods_opened: false,
            "name": "DIEGAO",
          },
          object:{
            command: null,        // = models.ForeignKey(Command, on_delete=models.DO_NOTHING)
            product: null,        // = models.ForeignKey(Product, on_delete=models.DO_NOTHING)
            name: null,   //= models.CharField(_('Nome do produto'), max_length=50, null=False, blank=False, unique=False, error_messages=settings.ERRORS_MESSAGES)
            price: null,  //= models.DecimalField(max_digits=9, decimal_places=2, blank=True, null=True)
            quantity: null,       //= models.DecimalField(max_digits=5, decimal_places=2, blank=False, null=False, default=1)
            total: null,          //= models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

            checkin_time: null,   //= models.DateTimeField(_('Entrada de pedido'), null=True, auto_now_add=True)
            checkout_time: null,  //= models.DateTimeField(_('Saída de pedido'), null=True, blank=True)
            waiting_time: null,   //= models.DurationField(null=True, blank=True)
            implement_time: null, //= models.DurationField(null=True, blank=True)
            duration_time: null,  //= models.DurationField(null=True, blank=True)
            status: null,         //= models.CharField(_('Status'), max_length=20, default='WAITING', choices=STATUS_OF_ORDER, null=True, blank=True, error_messages=settings.ERRORS_MESSAGES)
            observations: null,
          },

          conditions:{},
          backup:{},
          errors:{},
        }
      },

      selected:{
        table_group: 'GERAL',
        table: null,
        table_index: null,

        command: null,
        command_index: null,
        item: null,

        group:null,
        product:null,

        new_product: false,
        new_products: [],

        order: null,
      },

      command:{
        products:[],
        total: 0,
      },

      complements:[
        {'id':'1', 'name':'Ovo', 'price':1.50, 'quant':0},
        {'id':'1', 'name':'Queijo', 'price':2.00, 'quant':0},
        {'id':'1', 'name':'Presunto', 'price':2.00, 'quant':0},
        {'id':'1', 'name':'Hamburguer', 'price':3.50, 'quant':0},
      ],

      groups: [],

      user: {

      },
    }
  },

  filters: {
    round: function(value){
      return value.toFixed(2);
    },

    title(value){
      if(value){
        value = value.toLowerCase().split(' ');
      }
      else{
        value = "";
      }

      let final = [];
      for(let word of value){
        if(word.length > 2){
          final.push(word.charAt(0).toUpperCase()+ word.slice(1));
        }
        else{
          final.push(word);
        }
      }

      return final.join(' ');
    }
  },

  watch: {
    // whenever question changes, this function will run
    "controls.page.current": function (new_value, old_value) {
      if(new_value=='confirm'){
        let scope = this;
        //setTimeout(function(){ scope.init_location(); }, 200);
      }
    }
  },

  methods: {
    init_location: function(){
      let company_location = { lat: -20.374468, lng: -40.306149 };
      this.controls.location.map = new google.maps.Map(document.getElementById('map_container'), {
        center: this.controls.location.company_location,
        disableDefaultUI: true,
        zoomControl: false,
        mapTypeControl: false,
        scaleControl: false,
        streetViewControl: true,
        rotateControl: false,
        fullscreenControl: true,
        zoom: 14
      });

     /* google.maps.event.addListener(this.controls.location.map, 'dragend', function(event) {
        alert("ai papai vou marcar minha propria posição sozinho"+JSON.stringify(event));
        //addMarker(event.latLng, map);
      });*/

      var marker = new google.maps.Marker({
        position: this.controls.location.company_location,
        map: this.controls.location.map,
        icon: "http://maps.google.com/mapfiles/ms/icons/blue-dot.png",
        title: "Connect Carnes",
        draggable:true,
      });


      this.controls.location.service_area = new google.maps.Circle({
        strokeColor: "#c0e1b7",
        fillColor: "#e0f0db",
        strokeOpacity: 0.8,
        strokeWeight: 2,
        fillOpacity: 0.35,
        map:this.controls.location.map,
        center: this.controls.location.company_location,
        radius: 5000
      });

      this.show_location(parseFloat(this.forms.address.latitude), parseFloat(this.forms.address.longitude));
    },

    show_location: function(latitude, longitude){
      let scope = this;
      var pos = {
        lat: latitude,
        lng: longitude
      };

      this.controls.location.address.marker = new google.maps.Marker({
        position: pos,
        map: this.controls.location.map,
        //title: 'Diego Pasti'+pos.lat+','+pos.lng,
        draggable:false,
      });
      this.controls.location.map.setCenter(pos);

      this.controls.location.address.marker.addListener('click', function() {
        scope.controls.location.map.setZoom(17);
        scope.controls.location.map.setCenter(scope.controls.location.address.marker.getPosition());
      });

      this.controls.location.address.marker.addListener('click', function() {
        scope.controls.location.map.setZoom(17);
        scope.controls.location.map.setCenter(scope.controls.location.address.marker.getPosition());
      });

      if (!this.area_attended(pos, this.controls.location.company_location, 5)){
        alert("Região fora da área de entrega");
      }

      //var infoWindow = new google.maps.InfoWindow;
      //infoWindow.setPosition(pos);
      //infoWindow.setContent('Região fora da área de atendimento');
      //infoWindow.open(map);
    },

    handleLocationError: function(browserHasGeolocation, infoWindow, pos) {
      alert("Deu erro")
      infoWindow.setPosition(pos);
      infoWindow.setContent(browserHasGeolocation ?
        'Error: The Geolocation service failed.' :
        'Error: Your browser doesn\'t support geolocation.');
      infoWindow.open(map);
    },

    area_attended: function(checkPoint, centerPoint, km){
       var ky = 40000 / 360;
       var kx = Math.cos(Math.PI * centerPoint.lat / 180.0) * ky;
       var dx = Math.abs(centerPoint.lng - checkPoint.lng) * kx;
       var dy = Math.abs(centerPoint.lat - checkPoint.lat) * ky;
       return Math.sqrt(dx * dx + dy * dy) <= km;
    },

    get_location: function(position){
      let scope = this;
      let data_parameters = {};

      this.controls.location.latitude = position.coords.latitude;
      this.controls.location.longitude = position.coords.longitude;
      this.controls.location.accuracy = position.coords.accuracy;
      this.controls.location.altitude = position.coords.altitude;
      this.controls.location.speed = position.coords.speed;

      data_parameters['latitude'] = this.controls.location.latitude;
      data_parameters['longitude'] = this.controls.location.longitude;

      let success_function = function(response){
        scope.controls.location.address.marker.setMap(null);
        scope.controls.location.address = response.object;
        scope.controls.location.address.marker = null;
        scope.forms.address = JSON.parse(JSON.stringify(response.object));
        scope.show_location(position.coords.latitude, position.coords.longitude)
      }

      let failure_function = function(response){
        alert("DEU RUIM:"+JSON.stringify(response))
      }

      this.request('/api/core/commons/locations/get_address/', "get", data_parameters, null, success_function, failure_function);
    },

    get_position: function(){
      var options = {
        enableHighAccuracy: true,
        timeout: 5000,
        maximumAge: 0
      };

      function showError( error ) {
        alert('Serviço de geolocalização precisa de um dominio seguro (https)');
      }

      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(this.get_location,showError, options);
      }
      else {
        alert('O carregamento do endereço com base na sua localização atual não foi autorizada, preencha manualmente.')
      }
    },

    open_payment_panel: function(){
      this.forms.order.conditions = !this.forms.order.conditions;
      alert("switch")
    },

    select_product: function(product){
      //this.selected.product = product;
      let cloned_product = JSON.parse(JSON.stringify(product));
      cloned_product.quantity = "1.00";
      cloned_product.observations = "";
      this.forms.order.object = cloned_product;
      this.selected.product = product;
      $("#exampleModal").modal()
    },

    select_panel: function(panel){
      this.controls.page.current = panel;
    },

    filter_tables: function(option){
      this.selected.table_group = option;
    },

    print_command: function(command){
      window.open("/api/sales/command/"+command.code+"/", "_blank");
    },

    view_order: function(order){
      window.open("/api/sales/commands/order/"+this.selected.order.id+"/", "_blank");
    },

    print_order: function(order){
      let data_paramters = {"order_id":order.id}
      success_function = function(){
        alert("Pedido gerado com sucesso!");
      }

      failure_function = function(){
        alert("Erro! Não foi possivel gerar o pedido")
      }

      this.request('/api/sales/commands/order/print/', "post", data_paramters, null, success_function, failure_function);
    },

    confirm_item: function(item){
      alert("confirmei");
    },

    confirm_new_itens: function(){
      let scope = this;
      for (index in this.selected.new_products) {
        var value = this.selected.new_products[index];
        value.is_confirmed = true;
        this.selected.table.products.unshift(value);
      }
      this.selected.new_products = [];
    },

    show_options: function(command_index , order, order_index){
      if(this.selected.order){
        if(this.selected.order.id==order.id){
          this.selected.table.commands[command_index].orders[order_index].show_options = false;
          this.selected.command_index = null;
          this.selected.order_index = null;
          this.selected.order = null;
        }
        else{
          this.selected.table.commands[command_index].orders[this.selected.order_index].show_options = false;
          this.selected.table.commands[command_index].orders[order_index].show_options = true;
          this.selected.command_index = command_index;
          this.selected.order_index = order_index;
          this.selected.order = order;
        }
      }
      else{
        this.selected.table.commands[command_index].orders[order_index].show_options = true;
        this.selected.command_index = command_index;
        this.selected.order_index = order_index;
        this.selected.order = order;
      }
    },

    open_client_name_field: function(){
      this.forms.command.change_client_name = true;
    },

    confirm_client_name_field: function(){
      this.forms.command.change_client_name = false;
    },

    include_order:function(){
      let data_paramters = {};
      data_paramters['name'] = this.selected.product.name;
      data_paramters['image'] = this.selected.product.image;
      data_paramters['price'] = this.selected.product.price;
      data_paramters['quantity'] = this.forms.order.object.quantity;
      data_paramters['total'] = this.selected.product.price*this.forms.order.object.quantity;
      data_paramters['checkin_time'] = null;
      data_paramters['checkout_time'] = null;
      data_paramters['waiting_time'] = null;
      data_paramters['implement_time'] = null;
      data_paramters['duration_time'] = null;
      data_paramters['status'] = null;
      data_paramters['observations'] = this.forms.order.object.observations;

      for (var i = 0; i < this.forms.order.object.quantity; i++ ){
        this.command.products.push(data_paramters);
      }

      this.command.total = this.command.total + data_paramters['total'];
      alert("adicionei ao carrinho")
    },

    save_order: function(command, command_index){
      let scope = this;
      let data_paramters = {};
      data_paramters['command_id'] = this.selected.command.id;
      data_paramters['product_id'] = this.selected.product.id;
      data_paramters['name'] = this.selected.product.name;
      data_paramters['image'] = this.selected.product.image;
      data_paramters['price'] = this.selected.product.price;
      data_paramters['quantity'] = this.forms.order.object.quantity;
      data_paramters['total'] = this.selected.product.price*this.forms.order.object.quantity;

      data_paramters['checkin_time'] = null;
      data_paramters['checkout_time'] = null;
      data_paramters['waiting_time'] = null;
      data_paramters['implement_time'] = null;
      data_paramters['duration_time'] = null;
      data_paramters['status'] = null;
      data_paramters['observations'] = this.forms.order.object.observations;

      let success_function = function(response) {
        scope.print_order(response.object);
        response.object.show_options = false;
        scope.selected.command.orders.unshift(response.object);
        //alert("TOTAL DA COMANDA ANTES:"+scope.selected.command.total+" - VALOR A ADICIONAR:"+response.object.total+ " - TOTAL:"+(parseFloat(scope.selected.command.total) + parseFloat(response.object.total)))
        //scope.selected.command.total = parseFloat(scope.selected.command.total) + parseFloat(response.object.total);  //parseFloat(scope.selected.command.total) + parseFloat(response.object.total);
        //alert("TOTAL DA MESA:"+scope.selected.table.total +" - RESPONSE:"+parseFloat(response.object.total))
        scope.selected.table.total = parseFloat(scope.selected.table.total) + parseFloat(response.object.total);
        //alert("somei: "+scope.selected.table.total);
        scope.selected.new_product = null;
        $('#exampleModal').modal('hide');
      };

      let failure_function = function(response) {
        return false;
      };

      this.request('/api/sales/commands/order/save/', "post", data_paramters, null, success_function, failure_function);
    },

    select_item: function(command, item){
      this.selected.command = command;
      this.selected.product = {'id':parseInt(item.product), 'code':'0', 'name':item.name, 'image':item.image, 'price':item.price, 'quantity':1, 'description':'', 'have_promotion':true, 'is_confirmed':false, 'show_options':false};;

      /*this.forms.order.object = {
        command: command.id,
        product: item.id,
        name: item.name,
        price: item.price,
        quantity: 1,
        total: item.price,

        checkin_time: null,
        checkout_time: null,
        waiting_time: null,
        implement_time: null,
        duration_time: null,
        is_confirmed: false,
        show_options: false,
        status: "WAITING",
        observations:"",
      }*/


      //$("#exampleModal").modal();
      //$('#exampleModal').modal('show');

      /*if(item.is_confirmed){
        let new_item = JSON.parse(JSON.stringify(item));
        new_item.quant = 1;
        new_item.is_confirmed = false;
        new_item.show_options = false;
        this.selected.new_products.push(new_item);
      }*/
    },

    unselect_item: function(item){
      this.selected.item = null;
    },

    increase_item: function(index){
      this.selected.table.products[index].quant = this.selected.table.products[index].quant + 1
      //item.quant = item.quant + 1;
      //this.selected.item.quant = this.selected.item.quant + 1;
    },

    decrease_item: function(index){
      if(this.selected.table.products[index].quant >1){
        this.selected.table.products[index].quant = this.selected.table.products[index].quant - 1
      }
      else{
        this.selected.table.products[index].quant = 0
        //this.selected.table.products.shift()
        this.selected.table.products.splice(index,1);
      }
    },

    increase_new_item: function(index){
      this.selected.new_products[index].quant = this.selected.new_products[index].quant + 1
    },

    decrease_new_item: function(index){
      if(this.selected.new_products[index].quant >1){
        this.selected.new_products[index].quant = this.selected.new_products[index].quant - 1
      }
      else{
        this.selected.new_products[index].quant = 0
        //this.selected.table.products.shift()
        this.selected.new_products.splice(index,1);
      }
    },

    verify_screen: function () {
      this.controls.screen.width = window.innerWidth;
      this.controls.screen.height = window.innerHeight;

      let is_mobile = false;
      (function(a){if(/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce|xda|xiino|android|ipad|playbook|silk/i.test(a)||/1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(a.substr(0,4))) check = true;})(navigator.userAgent||navigator.vendor||window.opera);

      if(!is_mobile){
        if((screen.availHeight || screen.height-30) <= window.innerHeight) {
          this.controls.screen.fullscreen_mode = true;
        } else {
          this.controls.screen.fullscreen_mode = false;
        }
      }
    },

    init_complements: function(){

    },

    back_menu: function(){
      if(this.selected.product){
        $('#exampleModal').modal('hide');
        this.selected.product = null;
        history.pushState(null, document.title, location.href);
      }

      else if(this.selected.group){
        this.selected.group = null;
        history.pushState(null, document.title, location.href);
      }

      else if(this.selected.command){
        this.selected.command = null;
        this.selected.command_index = null;
        this.selected.new_product = false;
        history.pushState(null, document.title, location.href);
      }

      else if(this.selected.table){
        this.selected.table = null;
        history.pushState(null, document.title, location.href);
      }
      else{
        if(confirm("Deseja mesmo sair do sistema?")){
          window.location = "/logout";
        }
      }
      history.pushState(null, document.title, location.href);
    },

    open_menu: function(command, index){
      this.selected.command = command;
      this.selected.new_product = true;
      this.selected.command_index = index;
    },

    repeat_order: function(command, command_index, order){
      let cloned_order = JSON.parse(JSON.stringify(order));
      this.forms.order.object = cloned_order;
      this.selected.product = order;
      //this.selected.command = command;
      //this.selected.new_product = true;
      //this.selected.command_index = command_index;
    },

    load_tables: function () {
      let scope = this;
      let success_function = function(response) {
        scope.tables = response.object;
      };

      let failure_function = function(response) {
        return false;
      };

      this.request('/api/sales/commands/tables/load/', "get", null, null, success_function, failure_function);
    },

    open_table: function (table, index) {
      let scope = this;
      let data_paramters = {'table_id':table.id}

      let success_function = function(response) {
        Vue.set(scope.tables,index,response.object);
        scope.open_command(table, index);
      };

      let failure_function = function(response) {};

      this.request('/api/sales/commands/tables/open/', "post", data_paramters, null, success_function, failure_function);
    },

    close_table: function (table, index) {
      let scope = this;
      let data_paramters = {'table_id':table.id}

      let success_function = function(response) {
        scope.tables[index] = response.object;
      };

      let failure_function = function(response) {

      };

      this.request('/api/sales/commands/table/close/', "post", data_paramters, null, success_function, failure_function);
    },

    select_table: function(table, index){
      let scope = this;
      if(table.status=='CLOSED'){
        if (confirm("Abrir nova comanda na mesa "+table.code)) {
          scope.open_table(table, index);
        }
      }

      else{
        this.selected.table = table;
        this.selected.table_index = index;
      }
    },

    unselect_table: function(table){
      this.selected.table = null;
    },

    open_command: function(table, table_index){
      let scope = this;
      let data_paramters = {'table_id':table.id}

      let success_function = function(response) {
        scope.tables[table_index].commands.push(response.object);
        if(scope.selected.table==null){
          scope.selected.table = scope.tables[table_index];
          scope.selected.table_index = table_index;
        }
      };

      let failure_function = function(response) {
        alert("Erro! Não foi possivel abrir nova comanda")
      };

      this.request('/api/sales/commands/open/', "post", data_paramters, null, success_function, failure_function);
    },

    close_command: function(command, index){
      let scope = this;
      let data_paramters = {'command_id':command.id}

      if(table.status=='CLOSED'){
        if (confirm("Deseja mesmo Encerrar a command "+command.code)) {
          //scope.open_table(table, index);
          //this.open_command(table, index);
          alert("ihh cara.. vc quer encerrar mesmo");

          let success_function = function(response) {
            scope.tables[index].commands.push(response.object);
            scope.selected.table = table;
            scope.selected.table_index = index;
          };

          let failure_function = function(response) {

          };

          //this.request('/api/sales/commands/close/', "post", data_paramters, null, success_function, failure_function);
        }
      }
    },

    load_groups: function () {
      let scope = this;
      let success_function = function(response) {
        scope.groups = response.object;
      };

      let failure_function = function(response) {
        return false;
      };

      this.request('/api/sales/commands/groups/load/', "get", null, null, success_function, failure_function);
    },

    update_clock: function(){
      this.controls.clock = moment().utc().format();
      //this.controls.clock = new Date().utc().format();
    },

    get_user: function () {
      let scope = this;
      let data_parameters = {};
      let success_function = function(response) {
        scope.errors = response.message;
        scope.user = response.object;
        scope.user.password = '';
        //scope.session.is_blocked = response.object.session.is_blocked;
        //localStorage.setItem("is_blocked", response.object.session.is_blocked);
        //scope.controls.page.loaded = true;
      };

      let failure_function = function(response) {
        window.location.href = "/sales/commands/login";
      };

      this.request('/api/core/authentication/get_user/', 'get', data_parameters, null, success_function, failure_function);
    },
  },

  mounted: function(){
    alert("mounted");
  },

  beforeCreated: function(){
    alert("antes de criar");
  },

  created: function(){
    alert("aqui?")
    this.forms.address = {
      latitude:"-20.333730799999998",
      longitude:"-40.373235199999996",
      street_name:"Rua Demóstenes Nunes Vieira",
      address_number:"60",
      neighborhood_name:"Alto Lage",
      city_name:"Cariacica",
      state_name:"Espírito Santo",
      state_initials:"ES",
      country_name:"Brasil",
      country_initials:"BR",
      postal_code:"29.151-260",
      complement:"Segundo Andar",
    }
    alert("Defini posição inicial");
  },

  computed: {
    current_time: function(){
      if(this.controls.clock){
        return moment(String(this.controls.clock)).format('HH:mm:ss');
        //return this.controls.clock.format("hh:mm:ss");
      }
    },

    product_in_command: function(){
      let new_array = [];
      this.selected.table.commands.products.forEach(function(item, chave){
        if(item.quant > 0){
          new_array.push(item);
        }
        else{
          alert(item.name+":"+item.quant+"TIRAR");
        }
      });

      console.log("VEJA COMO FICOU ENTAO:"+JSON.stringify(new_array));
      this.selected.table.products = new_array;
      return this.selected.table.products;
    },
  },

  created: function () {
    //this.load_tables();
    //this.init_product_complements();
  },

  mounted: function () {

  }
});
