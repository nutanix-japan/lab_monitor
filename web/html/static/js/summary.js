var init = function(){
  console.log('init')
  load_summary()
}

var load_summary = function(){
  $.ajax({type:'get', url:'/api/temperature/v1/summary/',
    success:function(j, status, xhr){
      draw_max(j)
      draw_table(j['hosts'])
    }, 
    error:function(d){

    }
  })
}

var draw_max = function(data){
  if(data['day_timestamp'] == 0){
    // no sensor. do nothing
    return
  }

  $('#day_max').text(data['day_max'])
  $('#day_timestamp').text(dateFormat.format(
    new Date(data['day_timestamp'] * 1000), 'yyyy-MM-dd hh:mm:ss'))
  $('#day_name').text(data['day_name'])

  $('#week_max').text(data['week_max'])
  $('#week_timestamp').text(dateFormat.format(
    new Date(data['week_timestamp'] * 1000), 'yyyy-MM-dd hh:mm:ss'))
  $('#week_name').text(data['week_name'])

  $('#month_max').text(data['month_max'])
  $('#month_timestamp').text(dateFormat.format(
    new Date(data['month_timestamp'] * 1000), 'yyyy-MM-dd hh:mm:ss'))
  $('#month_name').text(data['month_name'])
}

var draw_table = function(hosts){
  $("#tbody_summary").empty()

  for (const host of hosts){
    var host_name = host['name']
    var host_ip = host['ip']
    var timestamp = host['timestamp']
    if(timestamp == 0){
      var dt = ''
      var temperature = ''
    }else{
      var dt = dateFormat.format(new Date(timestamp * 1000), 'yyyy-MM-dd hh:mm:ss')
      var temperature = host['temperature']
    }
    var html = '<tr>' +
      '<th scope="row">' + 1 + '</th>' +
      '<td>' + host_name + '</td>' +
      '<td>' + host_ip + '</td>' +
      '<td>' + temperature + '</td>' +
      '<td>' + dt + '</td>' +
    '</tr>'
    $("#tbody_summary").append(html)
  }
}

var dateFormat = {
  _fmt : {
    "yyyy": function(date) { return date.getFullYear() + ''; },
    "MM": function(date) { return ('0' + (date.getMonth() + 1)).slice(-2); },
    "dd": function(date) { return ('0' + date.getDate()).slice(-2); },
    "hh": function(date) { return ('0' + date.getHours()).slice(-2); },
    "mm": function(date) { return ('0' + date.getMinutes()).slice(-2); },
    "ss": function(date) { return ('0' + date.getSeconds()).slice(-2); }
  },
  _priority : ["yyyy", "MM", "dd", "hh", "mm", "ss"],
  format: function(date, format){
    return this._priority.reduce((res, fmt) => res.replace(fmt, this._fmt[fmt](date)), format)
  }
};