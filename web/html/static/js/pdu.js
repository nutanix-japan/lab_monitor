var init = function(){
  $('#button_register').click(create)
  load_hosts()
}

var load_hosts = function(){
  $.ajax({type:'get', url:'/api/temperature/v1/hosts/',
    success:function(j, status, xhr){
      draw_table(j)
    }, 
    error:function(d){

    }
  })
}

var draw_table = function(hosts){
  $("#tbody_pdulist").empty()

  for (const host of hosts){
    var host_uuid = host['uuid']
    var host_name = host['name']
    var host_ip = host['ip']
    var html = '<tr>' +
      '<th scope="row">' + 1 + '</th>' +
      '<td>' + host_name + '</td>' +
      '<td>' + host_ip + '</td>' +
      '<td><button class="btn btn-danger del-button" value="' + host_uuid + '">Delete</button></td>' +
    '</tr>'
    $("#tbody_pdulist").append(html)
  }
  $('.del-button').click(del)
}

var create = function(){
  var host_name = $('#input_name').val().trim()
  var host_ip = $('#input_ip').val().trim()

  if(host_name == ''){
    alert('please input host name');
    return
  }

  var rx = /^(?!0)(?!.*\.$)((1?\d?\d|25[0-5]|2[0-4]\d)(\.|$)){4}$/;
  if(!rx.test(host_ip)){
    alert('please input correct ip');
    return
  }

  var body = {
    'name':host_name,
    'ip':host_ip
  }
  $.ajax({type:'put', url:'/api/temperature/v1/hosts/', data:JSON.stringify(body),
    success:function(j, status, xhr){
      load_hosts()
    }, 
    error:function(d){

    }
  })
}

var del = function(){
  console.log('del clicked')
  var host_uuid = this.value

  $.ajax({type:'delete', url:'/api/temperature/v1/hosts/' + host_uuid,
    success:function(j, status, xhr){
      load_hosts()
    }, 
    error:function(d){

    }
  })
}