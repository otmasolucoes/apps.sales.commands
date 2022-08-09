Vue.filter('format_datetime', function(value) {
  if (value) {
    return moment(String(value)).format('DD/MM/YYYY HH:mm:ss')
  }
});

Vue.filter('format_time', function(value) {
  if (value) {
    return moment(String(value)).format('HH:mm:ss')
  }
});

Vue.filter('format_time_short', function(value) {
  if (value) {
    return moment(String(value)).format('HH:mm')
  }
});

Vue.filter('format_text_duration', function(value) {
  if (value) {
    let parts = value.split(":")
    let hours = parts[0].replace("00","0");
    let minutes = parts[1].replace("00","0");
    let final = "";

    if(minutes[0] == "0"){
      minutes = minutes[1]
    }

    if(hours != "0"){
      final = final+hours+"h "
    }

    final = final+minutes+"m"

    return final;
  }
});

Vue.filter('format_time_duration', function(value) {
  if (value) {
    let hours = moment(String(value)).format('hh:mm');
    let parts = hours.split(":")
    let final = parts[0]+"h "+parts[1]+"m"
    return final;
  }
});

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