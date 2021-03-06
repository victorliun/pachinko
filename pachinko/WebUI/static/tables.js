var now = new Date();
var oneYr = new Date();
//oneYr.setYear(now.getFullYear() - 1);
oneYr.setDate(now.getDate() - 5);

function getDateFormat (d) {
//    var d = new Date();
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
			updateTable(this,"tabledata");
                }
            }).val(getDateFormat(oneYr));


            $( "#to-datepicker" ).datepicker({
                altFormat: "yymmdd",
                dateFormat: "yy-mm-dd",
                // setDate: new Date(),
                onSelect: function (date) {
			updateTable(this, "tabledata");
                }
            }).val(getDateFormat(now));

          } );

	function updateTable(el, nextName) {
                                var options
                                var txtStrng = '';
				hallcode = $("#hallcode option:selected").text();
   				machinetype = $("#machinetype option:selected").text();
		   		machinenumber = $("#machinenumber option:selected").text();
				startDate = $("#from-datepicker").val();
				endDate =  $("#to-datepicker").val();
                                var full_url = "/Data?startDate=" + startDate + "&endDate=" + endDate + "&hallcode=" + hallcode + "&machinetype=" + machinetype +"&machinenumber=" + machinenumber;

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
			var total_spins = 0;
			var first_spins = {};
			var closing_spins = {};
			var total_wins = 0;
			var single_wins = [];
			var ranges_peaks = {};
                        $.each( options.reverse(), function(idx, obj) {
				if(!ranges_peaks[obj.date])
					ranges_peaks[obj.date] = {};

				if(obj.time_of_win.length>3)
					first_spins[obj.date] = parseInt(obj.spin_count_of_win);
				renchan_series += obj.renchan;
				total_spins += parseInt(obj.spin_count_of_win);
				if(obj.win_number != "--")
					total_wins += 1;
				else
					closing_spins[obj.date] = obj.spin_count_of_win;
				if(obj.renchan == 0)
					single_wins.push(obj.spin_count_of_win);
                                txtStrng += "<tr>";
                                txtStrng += "<td>"+obj.date + "</td>" ;
                                txtStrng += "<td>"+obj.renchan + "</td>" ;
                                txtStrng += "<td>"+obj.win_number + "</td>" ;
                                txtStrng += "<td>"+obj.time_of_win + "</td>" ;
                                txtStrng += "<td>"+obj.spin_count_of_win + "</td>" ;
                                txtStrng += "<td>"+obj.total_balls_out + "</td>" ;
				if(obj.machine_range)
				{
					txtStrng += "<td>" + obj.machine_range + "</td>";
					if(ranges_peaks[obj.date][obj.machine] && ranges_peaks[obj.date][obj.machine] < obj.machine_range)
						ranges_peaks[obj.date][obj.machine] = parseInt(obj.machine_range);
					else if(!ranges_peaks[obj.date][obj.machine])
						ranges_peaks[obj.date][obj.machine] = parseInt(obj.machine_range);
				}
                                txtStrng += "</tr>";
                            });
			var temp = 0;
			for(var dt in first_spins){
				temp += first_spins[dt];
			}

			$("#renchan_series").text(renchan_series);
			$("#first_win_spins").text(Math.round(100*(temp/Object.keys(first_spins).length))/100);
			$("#total_spins").text(total_spins);
			$("#total_wins").text(total_wins);
			$("#win_spin_ratio").text(Math.round(total_spins/total_wins));

			$("#av_single_win_spins").text(Math.round(single_wins.reduce(function(pv, cv) { return pv + cv; }, 0)/single_wins.length));


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

