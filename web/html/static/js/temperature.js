var init = function(){
  var url = location.href
  if(url.includes('?showing_range=week')){
    $('#title').text('Temperature this week')
  }else if (url.includes('?showing_range=month')){
    $('#title').text('Temperature this month')
  }else{
    $('#title').text('Temperature today')
  }

  $.ajax({type:'get', url:'/api/temperature/v1/hosts/',
    success:function(j, status, xhr){
      add_hosts_to_select(j)
    }, 
    error:function(d){

    }
  })
}

var add_hosts_to_select = function(hosts){
  for (const host of hosts){
    var html = '<option value="' + host + '">' + host + '</option>'
    $("#host_select").append(html)
  }

  draw()
  $('#host_select').change(draw)
}

var draw = function(){
  var url = location.href
  if(url.includes('?showing_range=week')){
    var showing_range = 'week'
  }else if (url.includes('?showing_range=month')){
    var showing_range = 'month'
  }else{
    var showing_range = 'day'
  }

  var val = $("#host_select option:selected").val()
  var url = '/api/temperature/v1/temperatures/' + val + '?showing_range=' + showing_range
  $.ajax({type:'get', url:url,
    success:function(j, status, xhr){
      loaded(j, showing_range)
    }, 
    error:function(d){

    }
  })
}

var loaded = function(dataset, showing_range){
  console.log(dataset.length)
  d3.selectAll("svg > *").remove();

  var width = 720;
  var height = 300;

  //var svg = d3.select("body").append("svg").attr("width", width).attr("height", height);
  var svg = d3.select("svg").attr("width", width).attr("height", height);
  var padding = 30;

  //var timeparser = d3.timeParse("%Y-%m-%e %H:%M:%S");
  var timeparser = d3.timeParse("%s");

  dataset = dataset.map(function(d){
    return  { datetime: timeparser(d.timestamp), temperature:d.temperature } ;
  });

  var xScale = d3.scaleTime()
    .domain([d3.min(dataset, function(d){return d.datetime;}), 
      d3.max(dataset, function(d){return d.datetime;})])
    .range([padding, width - padding]);

  var yScale = d3.scaleLinear()
    .domain([d3.min(dataset, function(d){return d.temperature;}) - 5, 
      d3.max(dataset, function(d){return d.temperature;}) + 5])
    .range([height - padding, padding]);

  if(showing_range == 'week'){
    var xtf = d3.timeFormat("%m/%d%p")
  }else if(showing_range == 'month'){
    var xtf = d3.timeFormat("%m/%d")
  }else{
    var xtf = d3.timeFormat("%H:%M")
  }
  var axisx = d3.axisBottom(xScale)
  .ticks(10)
  .tickFormat(xtf);
  var axisy = d3.axisLeft(yScale);

  var line = d3.line()
      .x(function(d) { return xScale(d.datetime); })
      .y(function(d) { return yScale(d.temperature); });

  svg.append("g")
    .attr("transform", "translate(" + 0 + "," + (height - padding) + ")")
    .call(axisx);

  svg.append("g")
    .attr("transform", "translate(" + padding + "," + 0 + ")")
    .call(axisy);

  svg.append("path")
    .datum(dataset)
    .attr("fill", "none")
    .attr("stroke", "steelblue")
    .attr("stroke-linejoin", "round")
    .attr("stroke-linecap", "round")
    .attr("stroke-width", 1.5)
    .attr("d", line);  
}