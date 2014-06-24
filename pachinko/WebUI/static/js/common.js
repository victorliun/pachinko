function updateNext(el, nextName) {
    var startDate = $( "#from-datepicker" ).val();
    var endDate = $( "#to-datepicker" ).val();

    if(el == "hallcode")
        var full_url ="/getHallcode?startDate=" + startDate + "&endDate=" + endDate;
    else
        var url_arg = jQuery(el).attr("data");
    if(nextName == "machinetype")
        var full_url ="/getMachineDetails?hallcode="+url_arg+"&distinctcol=machine_type&startDate=" + startDate + "&endDate=" + endDate;
    else if (nextName == "machinenumber")
    {
       hallcode_value = $("#hallcode li.selected").text();
       var full_url ="/getMachineDetails?hallcode="
            + hallcode_value+"&machine_type="+url_arg
            +"&distinctcol=machine&startDate=" 
            + startDate + "&endDate=" + endDate;
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
        timeout: 120000,
        success: function(data, textStatus, jqXHR)
        {
            //data - response from server
            options= data;
        },
        error: function (jqXHR, textStatus, errorThrown)
        {
            alert("Timeout error");
        }
    });
    var selected_hall = $("#hallcode li.selected").text();
    //create the option list
    txtStrng += "<li data='blank'>None</li>";
    $.each( options, function(i,val) {
        if (val == selected_hall){
            txtStrng += "<li data='" + val + "' class='selected'>";
        }
        else
            txtStrng += "<li data='" + val + "'>";
        txtStrng += val ;
        txtStrng += "</li>";
    });
    if (nextName == "hallcode" && options.indexOf(selected_hall) == -1){
        $('#'+nextName).prev().text('None');
    }
    $('#'+nextName).text('');
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
    var endDate = $("input#to-datepicker").val();
    var url = "/get_machine_type_details?hallcode="+hallcode_value+"&machinetype="+machine_type +
        "&startDate="+startDate+"&endDate="+endDate;
    if (machine_type != "None")
    {
        $.ajax({
            async: false,
            url: url,
            dataType: 'json',
            timeout:120000,
            success: function(data, textStatus, jqXHR)
            {
                $("div#hall_table").hide();
                $("div#tables").hide();
                var table_string = "";
                $.each(data, function(index, val){
                    if (index % 2 == 0)
                      table_string += "<tr class='grey_bkc'>";
                    else
                      table_string += "<tr>";
                    table_string += "<td>"+val['machine']+ "</td><td>" 
                        + val['cash_result'] + "</td><td>" + val['average_cash_result'] 
                        + "</td><td>" + val['range'] +"</td><td>" + val['win_spin'] 
                        + "</td><td>" + val['single_win'] + "</td><td>"
                        + val['renchan'] + "</td><td>" + val['total_win'] +"</td></tr>";
                });
                $("div#machine_type_table table tr").slice(1).remove();
                $("div#machine_type_table table").append(table_string);
                $("div#machine_type_table").show();
            },
            error: function (jqXHR, textStatus, errorThrown)
            {
                alert("Timeout error");
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
            timeout:120000,
            success: function(data, textStatus, jqXHR)
            {
                $("div#tables").hide();
                $("div#machine_type_table").hide()
                var table_string = "";
                $.each(data, function(index, val){
                    if (index % 2 == 0)
                      table_string += "<tr class='grey_bkc'>";
                    else
                      table_string += "<tr>";
                    table_string += "<td>"+val['machine_type']+ "</td><td>"
                        + val['cash_result'] + "</td><td>" + val['average_cash_result'] 
                        + "</td><td>" + val['range'] + "</td><td>" + val['win_spin'] 
                        + "</td><td>" +val['single_win'] + "</td><td>"
                        + val['renchan'] + "</td><td>" + val['total_win'] +"</td></tr>";
                });
                $("div#hall_table table tr").slice(1).remove();
                $("div#hall_table table").append(table_string);
                $("div#hall_table").show();
            },
            error: function (jqXHR, textStatus, errorThrown)
            {
                alert("Timeout error");
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

function load_args(){
    var startDate = $("#arg_startDate").text();
    if(startDate){
        $( "#from-datepicker" ).datepicker('setDate', startDate);
    }
    var endDate = $("#arg_endDate").text();
    if(endDate){
        $( "#to-datepicker" ).datepicker('setDate', endDate);
    }
    var hallcode = $("#arg_hallcode").text();
    if(hallcode){
        $('#hallcode li[data='+hallcode+']').click();
    }
    var machinetype = $("#arg_machinetype").text();
    if(machinetype){
        $( "#machinetype li[data='"+machinetype+"']").click();
    }
    var machinenumber = $("#arg_machinenumber").text();
    if(machinenumber){
        $( "#machinenumber li[data='"+machinenumber+"']" ).click();
    }
}

