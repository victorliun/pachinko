function updateNext(el, nextName) {
    if(el == "hallcode")
        var full_url ="/getHallcode/column=hallcode";
    else
        var url_arg = jQuery(el).attr("data");
    if(nextName == "machinetype")
        var full_url ="/getMachineDetails?column=hallcode&value="+url_arg+"&distinctcol=machine_type";
    else if (nextName == "machinenumber")
    {
       hallcode_value = $("#hallcode li.selected").text();
       var full_url ="/getMachineDetails?column=hallcode&value="+hallcode_value+"&column2=machine_type&value2="+url_arg+"&distinctcol=machine";
       if(url_arg== "blank")
       {
         full_url = "/getMachineDetails?";
       }
   }
   var options;
   var txtStrng = '';
    //grab ajax data
    $.ajax({
        async: false,
        url: full_url,
            //type: 'POST',
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
    txtStrng += "<li data='blank'>None</li>";
    $.each( options, function(i,val) {
        txtStrng += "<li data='" + val + "'>";
        txtStrng += val ;
        txtStrng += "</li>";
    });
     //clear the option list
     $('#'+nextName).text('');
     $('#'+nextName).prev().text('None');
    //attach the option list
    $(txtStrng).appendTo('#'+nextName);

}

function show_machine_type()
{
    var hallcode_value = $("#hallcode li.selected").text();
    var machine_type = $("#machinetype li.selected").text();
    if( hallcode=="None")
        return;
    var startDate = $("input#from-datepicker").val();
    var endDate =  $("input#to-datepicker").val();
    var url = "/get_machine_type_details?hallcode="+hallcode_value+"&machinetype="+machine_type +
        "&startDate="+startDate+"&endDate="+endDate;
    if (machine_type != "None")
    {
        $.ajax({
            async: false,
            url: url,
            dataType: 'json',
            success: function(data, textStatus, jqXHR)
            {
                $("div#hall_table").hide();
                $("div#tables").hide();
                var table_string = "";
                $.each(data, function(index, val){
                    table_string += "<tr><td>"+val['machine']+ "</td><td>" 
                        + val['range'] +"</td><td>" + val['win_spin'] 
                        + "</td><td>" +val['single_win'] + "</td><td>"
                        + val['renchan'] + "</td><td>" + val['total_win'] +"</td></tr>";
                });
                $("div#machine_type_table table tr").slice(1).remove();
                $("div#machine_type_table table").append(table_string);
                $("div#machine_type_table").show();
            },
            error: function (jqXHR, textStatus, errorThrown)
            {
                alert(textStatus)
                alert(jqXHR)
            }
        });
    }
    else{
        $("div#hall_table").show();
        $("div#tables").hide();
        $("div#machine_type_table").hide();
    }
}

function show_machine_types_from_hallcode()
{
    //this function
    var hallcode_value = $("#hallcode li.selected").text();
    var startDate = $("input#from-datepicker").val();
    var endDate =  $("input#to-datepicker").val();
    var url = "/get_machine_type_details?hallcode="+hallcode_value +
        "&startDate="+startDate+"&endDate="+endDate;
    if( hallcode_value != "None"){
        $.ajax({
            async: false,
            url: url,
            dataType: 'json',
            success: function(data, textStatus, jqXHR)
            {
                $("div#tables").hide();
                $("div#machine_type_table").hide()
                var table_string = "";
                $.each(data, function(index, val){
                    table_string += "<tr><td>"+val['machine_type']+ "</td><td>" 
                        + val['range'] +"</td><td>" + val['win_spin'] 
                        + "</td><td>" +val['single_win'] + "</td><td>"
                        + val['renchan'] + "</td><td>" + val['total_win'] +"</td></tr>";
                });
                $("div#hall_table table tr").slice(1).remove();
                $("div#hall_table table").append(table_string);
                $("div#hall_table").show();
            },
            error: function (jqXHR, textStatus, errorThrown)
            {
                alert(textStatus)
                alert(jqXHR)
            }
        });
    }
    else{
        updateTable($('#hallcode a'), 'tabledata');
        $("div#hall_table").hide();
        $("div#tables").show();
        $("div#machine_type_table").hide()
    }
}

