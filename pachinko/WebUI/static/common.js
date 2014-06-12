
  function updateNext(el, nextName) {
                        if(el == "hallcode")
                                var full_url ="/getHallcode/column=hallcode";
                        else
                                var url_arg = el.value;
                                if(nextName == "machinetype")
                                        var full_url ="/getMachineDetails?column=hallcode&value="+url_arg+"&distinctcol=machine_type";
                                else if (nextName == "machinenumber")
					{
					hallcode_value = $("#hallcode option:selected").text();
                                        var full_url ="/getMachineDetails?column=hallcode&value="+hallcode_value+"&column2=machine_type&value2="+url_arg+"&distinctcol=machine";
					}
                        var options
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
                                        alert(textStatus)
                                        alert(jqXHR)
                                }
                        });
                        //create the option list
                        txtStrng += "<option value=blank> </option>";
                        $.each( options, function(i,val) {
                                txtStrng += "<option value=\"" + val + "\">";
                                txtStrng += val ;
                                txtStrng += "</option>";
                        });
                         //clear the option list
                        $('#'+nextName).text('');
                        //attach the option list
                        $(txtStrng).appendTo('#'+nextName);

                        }


