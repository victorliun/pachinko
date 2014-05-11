var now = new Date();
var oneYr = new Date();
//oneYr.setYear(now.getFullYear() - 1);
oneYr.setDate(now.getDate() - 5);

function getDateFormat (d) {
  //var d = new Date();
  var curr_date = d.getDate();
  if (curr_date < 10)
    curr_date = "0" + curr_date;
  var curr_month = d.getMonth() + 1; //Months are zero based
  if (curr_month < 10)
    curr_month = "0" + curr_month;
  var curr_year = d.getFullYear();
  return curr_year + "-" + curr_month + "-" + curr_date;
}
//alert(JSON.stringify(chartData));

$(document).ready(function () {
  $( "#from-datepicker" ).datepicker({
    altFormat: "yymmdd",
    dateFormat: "yy-mm-dd",
    // setDate: new Date(),
    onSelect: function (date) {
      if($("#by_hall").text() != "None"  && $("#by_machine_type").text() != "None"  && $("#by_machine").text() == "None" )
        show_machine_type();
      else if ($("#by_hall").text() != "None"  && $("#by_machine_type").text() == "None")
        show_machine_types_from_hallcode();
      updateTable(this,"tabledata");
      $.cookie("from_date", this.value);
    }
  });

  if($.cookie("from_date"))
    $( "#from-datepicker" ).datepicker('setDate', $.cookie('from_date'));
  else
    $( "#from-datepicker" ).datepicker('setDate', getDateFormat(now));


  $( "#to-datepicker" ).datepicker({
    altFormat: "yymmdd",
    dateFormat: "yy-mm-dd",
    // setDate: new Date(),
    onSelect: function (date) {
      if($("#by_hall").text() != "None"  && $("#by_machine_type").text() != "None"  && $("#by_machine").text() == "None" )
        show_machine_type();
      else if ($("#by_hall").text() != "None"  && $("#by_machine_type").text() == "None")
        show_machine_types_from_hallcode();
      updateTable(this, "tabledata");

      $.cookie("to_date", this.value);
    }
  });

  if($.cookie("to_date"))
    $( "#to-datepicker" ).datepicker('setDate', $.cookie('to_date'));
  else
    $( "#to-datepicker" ).datepicker('setDate', getDateFormat(now));
});

function updateTable(el, nextName) {
  var options;
  var txtStrng = '';
  hallcode = $("#hallcode li.selected").text();
  if (hallcode == "None")
    hallcode = ''
  machinetype = $("#machinetype li.selected").text();
  machinenumber = $("#machinenumber li.selected").text();
  startDate = $("#from-datepicker").val();
  endDate =  $("#to-datepicker").val();
  var full_url = "/Data?startDate=" + startDate + "&endDate=" + endDate + "&hallcode=" + hallcode + "&machinetype=" + machinetype +"&machinenumber=" + machinenumber;

  if(hallcode && machinetype && machinenumber =="None"){
    $("div#hall_table").hide();
    $("div#tables").hide();
    $("div#machine_type_table").show();
    return;
  }
  //grab ajax data
  $.ajax({
    async: false,
    url: full_url,
    dataType: 'json',
    success: function(data, textStatus, jqXHR)
    {
      //data - response from server
      options= data;
    },
    error: function (jqXHR, textStatus, errorThrown)
    {
      alert(textStatus)
      alert(jqXHR)
    }
  });
  //create the option list
  var renchan_series = 0;
  var renchan_wins = 0;
  var total_spins = 0;
  var first_spins = {};
  var closing_spins = {};
  var total_wins = 0;
  var single_wins = [];
  var ranges_peaks = {};
  var last_renchan = 0;
  $.each( options.reverse(), function(idx, obj) {
    if(!ranges_peaks[obj.date])
      ranges_peaks[obj.date] = {};

    if(obj.time_of_win.length>3)
      first_spins[obj.date] = parseInt(obj.spin_count_of_win);
    renchan_wins += obj.renchan;
    //count renchan series
    if (obj.renchan ==1 && obj.renchan != last_renchan)
      renchan_series += 1
    last_renchan = obj.renchan;

    total_spins += parseInt(obj.spin_count_of_win);

    var time_of_win = obj.time_of_win;
    if (time_of_win == "NaN")
      time_of_win = "--";
    
    var win_number = obj.win_number
    if(win_number != "--" && win_number != 0)
      total_wins += 1;
    else if (win_number == '--' && time_of_win == '--')
      closing_spins[obj.date] = obj.spin_count_of_win;
    if(obj.renchan == 0)
      single_wins.push(obj.spin_count_of_win);
    
    if (win_number == 0)
      win_number = '--'
    txtStrng += "<tr>";
    txtStrng += "<td>"+obj.date + "</td>" ;
    txtStrng += "<td>"+obj.renchan + "</td>" ;
    txtStrng += "<td>"+win_number + "</td>" ;
    txtStrng += "<td>"+time_of_win + "</td>" ;
    txtStrng += "<td>"+obj.spin_count_of_win + "</td>" ;
    if (!!obj.total_balls_out)
      txtStrng += "<td>"+obj.total_balls_out + "</td>" ;
    else
      txtStrng += "<td> -- </td>" ;
    if(obj.machine_range)
    {
      txtStrng += "<td>" + obj.machine_range + "</td>";
      if(ranges_peaks[obj.date][obj.machine] && ranges_peaks[obj.date][obj.machine] < obj.machine_range)
        ranges_peaks[obj.date][obj.machine] = parseInt(obj.machine_range);
      else if(!ranges_peaks[obj.date][obj.machine])
        ranges_peaks[obj.date][obj.machine] = parseInt(obj.machine_range);
    }
    else
      txtStrng += "<td>--</td>";
      txtStrng += "</tr>";
  });

  var temp = 0;
  for(var dt in first_spins){
    temp += first_spins[dt];
  }
  if (renchan_series == 0 )
    renchan_series = 1;
  $("#renchan_wins").text(renchan_wins);
  $("#renchan_average").text(Math.round(renchan_wins*100/renchan_series)/100);
  $("#first_win_spins").text(Math.round(100*(temp/Object.keys(first_spins).length))/100);
  $("#total_spins").text(total_spins);
  $("#total_wins").text(total_wins);
  $("#win_spin_ratio").text(Math.round(total_spins/total_wins));
  $("#av_single_win_spins").text(Math.round(
    single_wins.reduce(function(pv, cv) { 
      return pv + cv; }, 0)/single_wins.length));

  temp = 0;
  for(var dt in closing_spins){
    temp += closing_spins[dt];
  }

  $("#closing_spin_count").text(Math.round(100*(temp/Object.keys(closing_spins).length))/100);


  temp = 0;
  var c = 0;
  for(var dt in ranges_peaks){
    for(var m in ranges_peaks[dt]){
      temp += ranges_peaks[dt][m];
      c++;
    }
  }

  $("#peak_points").text(Math.round(100*(temp/c))/100);
  //clear the option list
  $('#'+nextName +' tbody').remove();
  //attach the option list
  $(txtStrng).appendTo('#'+nextName);

}

