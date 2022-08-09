Vue.component('app_commands',{
  mixins: [],
  props: ['controls', 'forms', 'selected', 'groups', 'complements'],
  data: function(){
    return {
      /*forms:{
        order:{
          object:{
            command: null,        // = models.ForeignKey(Command, on_delete=models.DO_NOTHING)
            product: null,        // = models.ForeignKey(Product, on_delete=models.DO_NOTHING)
            product_name: null,   //= models.CharField(_('Nome do produto'), max_length=50, null=False, blank=False, unique=False, error_messages=settings.ERRORS_MESSAGES)
            product_price: null,  //= models.DecimalField(max_digits=9, decimal_places=2, blank=True, null=True)
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
      }*/
    }
  },

  methods: {
    select_group: function(group){
      this.selected.group = group;
    },

    select_product: function(product){
      //this.selected.product = product;
      let cloned_product = JSON.parse(JSON.stringify(product));
      cloned_product.quantity = "1";
      cloned_product.observations = "";
      this.forms.order.object = cloned_product;
      this.selected.product = product;
      $("#OrderModal").modal()
    },

    return_menu: function(){
      this.selected.group = null;
    },

    increase_complement: function(complement){
      complement.quant = complement.quant + 1;
    },

    decrease_complement: function(extra){
      if(complement.quant > 0){
        complement.quant = complement.quant - 1;
      }
    },

    return_command: function(){
      this.selected.new_product = false;
    },

    load_menu: function(){
      let scope = this;
      let url = '/api/sales/groups/load/';

      let success_function = function(response) {
        console.log(response)
        //scope.groups = response
        //alert("sucesso");
      };

      let failure_function = function(response) {
        //alert("falhou");
      };

      this.request(url, 'GET', null, null, success_function, failure_function);
    },


  },

  created: function(){

  },

  mounted: function(){
  },

  template: `
    <div>
      <div style='padding:10px;'>
        <ul id='product-menu' :class="{'auto-grid-small':controls.screen.width<1024, 'auto-grid-large':controls.screen.width>=1024}" style='margin-left:-40px;'>
          <template v-if='selected.group'>
            <li v-if='controls.screen.fullscreen_mode' :style='controls.styles.themes.active.product_list' style='padding:5px;cursor:pointer;' @click='return_menu()'>
              <img class='menu-item-image' src="/static/apps/sales/commands/images/back.png" style='position:relative;top:10px;'/>
            </li>

            <template v-for='product in selected.group.products'>
              <li :style='controls.styles.themes.active.product_list' style='padding:5px;cursor:pointer;padding-bottom:10px;' @click='select_product(product)'>
                <img class='menu-item-image' style='float:left;' :src='product.image' />

                <div class='menu-item-price' style=''>
                  <div class='float-right' style='background:white;padding-left:10px;padding-right:5px;'>R$ {{ product.price }}</div>
                </div>
                <span>{{ product.name }}</span>
              </li>
            </template>
          </template>

          <template v-else>
            <!--<li :style='controls.styles.themes.active.product_list' style='padding:5px;cursor:pointer;' @click='return_command()'><!- v-if='controls.screen.fullscreen_mode' ->
              <img class='menu-item-image' src="/static/apps/sales/commands/images/back.png" :style='controls.styles.themes.active.product_list' style='position:relative;top:10px;'/>
            </li>-->
            <template v-for='group in groups'>
              <li :style='controls.styles.themes.active.product_list' style='padding:5px;cursor:pointer;padding-bottom:10px;' @click='select_group(group)'>
                <img class='menu-item-image' style='float:left;' :src='group.image' />
                <span>{{ group.name }}</span>
              </li>
            </template>
          </template>
        </ul>
      </div>
    </div>
  `
});

Vue.component('app_commands_user_register', {
	mixins: [base_communications],
	props:['form'],
	methods:{
		signup: function(){
			let scope = this;
			//alert('OLHA AÊ: ' + JSON.stringify(scope.form.object));
			let data_paramters = scope.form.object;
			let success_function = function(response){
				scope.errors = response.message;
        window.location.reload();
				window.location.href = "/sales/commands/login";
			};

			let failure_function = function(response){
				scope.form.errors = response.message;
			};

      let validation_function = function () {
        let result = true;
        let error_keys = {'first_name' : 'primeiro nome', 'family_name' : 'sobrenome', 'email' : 'e-mail', 'username' : 'usuário', 'password' : 'senha', 'confirm_password' : 'confirmação de senha', 'activation_code' : 'chave de autorização'};
        for(let field in data_paramters){
          if(!data_paramters[field]){
            error_notify(null,"Erro!","O campo de "+error_keys[field]+" é obrigatório");
            result = false;
          }
        }
        if(!validate_password(data_paramters.password)) {
          error_notify(null,"Senha inválida","Confira se sua senha tem mais de 8 caracteres, e contém letras e números");
          result = false;
        }
        if(!validate_confirm_password(data_paramters.password,data_paramters.confirm_password)) {
          error_notify(null,"Confirmação de senha inválida","Confira se sua senha é igual a confirmação");
          result = false;
        }
        if(!validate_email(data_paramters.email)) {
          error_notify(null,"E-mail inválido","Confira se seu e-mail foi digitado corretamente");
          result = false;
        }
        return result;
      };

			this.request('/api/core/authentication/user/register/','post',data_paramters, null, success_function, failure_function);
		},
	},
	template:
  `
  <div>
    <template>
      <div class="row">
        <div class="col-lg-12 col-md-12 col-sm-12 col-xs-12">
            <app_field_upper classes='form-control form-control-sm' label='Nome' title='Digite seu nome' type="text" v-model='form.object.first_name' :error='form.first_name'></app_field_upper>
        </div>
        <div class="col-lg-12 col-md-12 col-sm-12 col-xs-12">
            <app_field_upper classes='form-control form-control-sm' label='Sobrenome' title='Digite seu sobrenome' type="text" v-model='form.object.family_name' :error='form.family_name'></app_field_upper>
        </div>
      </div>
      <div class="row">
        <div class="col-lg-12 col-md-12 col-sm-12 col-xs-12">
            <app_field classes='form-control form-control-sm' label='E-mail' title='Digite seu e-mail' type="text" v-model='form.object.email' :error='form.email'></app_field>
        </div>
        <div class="col-lg-12 col-md-12 col-sm-12 col-xs-12">
          <app_field classes='form-control form-control-sm' label='Usuário' title='Digite um usuário' type="text" v-model='form.object.username' :error='form.username'></app_field>
        </div>
      </div>
      <div class="row">
        <div class="col-lg-6 col-md-12 col-sm-12 col-xs-12">
            <app_field classes='form-control form-control-sm' label='Senha' title='Digite uma senha' type="text" v-model='form.object.password' :error='form.username'></app_field>
        </div>
        <div class="col-lg-6 col-md-12 col-sm-12 col-xs-12">
            <app_field classes='form-control form-control-sm' label='Confirme a senha' title='Confirme a senha' type="text" v-model='form.object.confirm_password' :error='form.username'></app_field>
        </div>        
      </div>
      <br>
      <div class="row">
        <div class='col-lg-12 col-md-12 col-sm-12 col-xs-12' style='padding-left: 7px;padding-right: 7px;'>
          <div class="d-flex">
            <div class="mr-auto p-2">
              <button class="btn btn-sm btn-secondary" type="button" @click="back()">Cancelar</button>
            </div>
            <div class="p-2">
              <button class="btn btn-sm btn-secondary" type="button" style='width:80px;' @click="signup()">Salvar</button>
            </div>
          </div>
        </div>
      </div>
        <hr>
        <p style="text-align:center; font-size: x-small;">Já tem cadastro?  <a href="/sales/commands/login">Clique aqui.</a></p>
    </template>
  </div>
  `
});

Vue.component('app_commands_user_login', {
	mixins: [base_communications],
	props:['form'],
	methods:{
		login: function(){
			let scope = this;
			//let data_paramters = scope.form.object;
      //alert('OLHA AÊ: ' + JSON.stringify(scope.form.object));
			let data_paramters = Object.assign({}, scope.form.object, SESSION_PARAMTERS);
			let success_function = function(response){
				scope.errors = response.message;
        window.location.href = "/sales/commands";
				scope.init_form();
			};
			let failure_function = function(response){
				scope.form.errors = response.message;
				for (let error in scope.form.errors){
					error_notify(null,"Falha na operação!",scope.form.errors[error]);
				}
			};
			let validation_function = function () {
				let result = true;
				let error_keys = {'username' : 'usuário', 'password' : 'senha'};
				for(let field in data_paramters){
					if(!data_paramters[field]){
						error_notify(null,"Falha na operação!","O campo de "+error_keys[field]);
						result = false;
					}
				}
				return result;
			};
			this.request('/api/core/authentication/login/','post', data_paramters, null, success_function, failure_function);
		},
    init_form: function(){
      let scope = this;
		  scope.form.object = {};
    },
	},
	template:
  `
  <div>
    <template>
      <div class="row" style="height:40px;">
        <div class="col-lg-12 col-md-12 col-sm-12 col-xs-12">
          <app_input classes='form-control form-control-md' label='Usuário' placeholder='Digite seu usuário' type="text" v-model='form.object.username' :error='form.username'></app_input>
        </div>
      </div>
      <div class="row" style="height:30px;">
        <div class="col-lg-12 col-md-12 col-sm-12 col-xs-12">
          <app_input classes='form-control form-control-md' label='Senha' placeholder='Digite sua senha' type='password' v-model='form.object.password' :error='form.password'></app_input>
        </div>
      </div>  
      <hr>      
      <div class='row'>
        <div class="col-lg-12 col-md-12 col-sm-12 col-xs-12">
        <button class="btn btn-sm btn-secondary" type="button" style='width:99%;' @click="login()">Entrar</button>
        </div>
      </div>
      <hr>
      <p style="text-align:center; font-size: x-small;">Não tem cadastro?  <a href="/sales/commands/signup">Clique aqui para se cadastrar.</a></p>
    </template>
  </div>
  `
});
