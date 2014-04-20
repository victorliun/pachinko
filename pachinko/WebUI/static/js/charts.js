var chartData = {};
var chartCursor;

var diffCharts = ["spincount", "winspincount", "closingspincount", "singlewinsspincount", "renchan" ,"totalwins"];
var diffFreq = ["day"];

var chartDates = {}
var chartPointers = {}

var now = new Date();
var oneYr = new Date();
//oneYr.setYear(now.getFullYear() - 1);
oneYr.setDate(now.getDate() - 5);

for(var i=0; i<diffCharts.length;i++)
{
    chartData[diffCharts[i]] = {};
    chartDates[diffCharts[i]] = {};
    chartPointers[diffCharts[i]] = {};
    for(var k=0; k<diffFreq.length; k++)
    {
        chartData[diffCharts[i]][diffFreq[k]] = [];
        chartDates[diffCharts[i]][diffFreq[k]] = {}
        //chartDates[diffCharts[i]][diffFreq[k]]["from"] = getDateFormat(oneYr).replace("-", "").replace("-", "");
        chartDates[diffCharts[i]][diffFreq[k]]["from"] = getDateFormat(oneYr);
        //chartDates[diffCharts[i]][diffFreq[k]]["to"] = getDateFormat(now).replace("-", "").replace("-", "");
        chartDates[diffCharts[i]][diffFreq[k]]["to"] = getDateFormat(now);
        chartPointers[diffCharts[i]][diffFreq[k]] = null;
    }
}

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

function generateChartsOnDropDownChange()
{
     for(var i=0;i<diffCharts.length;i++)
    {
        for(var k=0;k<diffFreq.length;k++)
        {
            var chart;
            chart = new AmCharts.AmSerialChart();
            chartPointers[diffCharts[i]][diffFreq[k]] = chart;

            $( "#" + diffCharts[i] + "-" + diffFreq[k] + "-datepicker" ).datepicker({
                altFormat: "yy-mm-dd",
                dateFormat: "yy-mm-dd",
                // setDate: new Date(),
                onSelect: function (date) {
                    var id = $(this).attr('id');
                    id = id.split("-");
                //alert("dsdsd is " + $("#hallcode option:selected").text());
                    chartDates[id[0]][id[1]]["from"] = date;//.replace("-", "").replace('-', "");
                    generateChartData(id[0], id[1], chartPointers[id[0]][id[1]]);
                }
            }).val(getDateFormat(oneYr));


            $( "#" + diffCharts[i] + "-" + diffFreq[k] + "-datepicker2" ).datepicker({
                altFormat: "yy-mm-dd",
                dateFormat: "yy-mm-dd",
                // setDate: new Date(),
                onSelect: function (date) {
                    var id = $(this).attr('id');
                    id = id.split("-");
                    chartDates[id[0]][id[1]]["to"] = date;//.replace("-", "").replace("-", "");
                    generateChartData(id[0], id[1], chartPointers[id[0]][id[1]]);
                }
            }).val(getDateFormat(now));

            //generateChartData(diffCharts[i], diffFreq[k], chartPointers[diffCharts[i]][diffFreq[k]]);
	        chart.pathToImages = "http://www.amcharts.com/lib/3/images/";
            //    alert(JSON.stringify(chartData));
            //alert(JSON.stringify(chartData[diffCharts[i]][diffFreq[i]]));
            chart.dataProvider = chartData[diffCharts[i]][diffFreq[k]];
            chart.categoryField = "date";
	        chart.dataDateFormat = "YYYY-MM-DD, JJ:NN:SS";
            chart.balloon.bulletSize = 5;

            // listen for "dataUpdated" event (fired when chart is rendered) and call zoomChart method when it happens
            chart.addListener("dataUpdated", zoomChart);

            // AXES
            // category
            var categoryAxis = chart.categoryAxis;
            categoryAxis.parseDates = true; // as our data is date-based, we set parseDates to true
            categoryAxis.minPeriod = "hh"; // our data is daily, so we set minPeriod to DD
            categoryAxis.dashLength = 1;
            categoryAxis.minorGridEnabled = true;
            categoryAxis.position = "bottom";
            categoryAxis.axisColor = "#DADADA";

            // value
            var valueAxis = new AmCharts.ValueAxis();
            valueAxis.axisAlpha = 0;
            valueAxis.dashLength = 1;
            chart.addValueAxis(valueAxis);
	
	    // GRAPH
            var graph = new AmCharts.AmGraph();
            graph.title = "red line";
            graph.valueField = "impressions";
            graph.bullet = "round";
            graph.bulletBorderColor = "#FFFFFF";
            graph.bulletBorderThickness = 2;
            graph.bulletBorderAlpha = 1;
            graph.lineThickness = 2;
            graph.lineColor = "#5fb503";
            graph.negativeLineColor = "#efcc26";
            graph.hideBulletsCount = 50; // this makes the chart to hide bullets when there are more than 50 series in selection
            chart.addGraph(graph);

            // CURSOR
            chartCursor = new AmCharts.ChartCursor();
            chartCursor.cursorPosition = "mouse";
            chartCursor.pan = true; // set it to fals if you want the cursor to work in "select" mode
            chart.addChartCursor(chartCursor);

            // SCROLLBAR
            var chartScrollbar = new AmCharts.ChartScrollbar();
            chart.addChartScrollbar(chartScrollbar);

            // WRITE
            //alert(diffCharts[i] + diffFreq[k]);
            chart.write(diffCharts[i] + diffFreq[k]);

            generateChartData(diffCharts[i], diffFreq[k], chart);

	    }
	}	

}

// generate some random data, quite different range
function generateChartData(chartType, chartFreq, chrt) {
    var k = "";
    // var diffCharts = ["imp", "os", "uniq", "url"];
    // var diffFreq = ["day", "month"];
    if (chartType=="spincount")
        k = "renchan";
    else if(chartType=="winspincount")
        k = "spin_count_of_win";
    else if(chartType == "closingspincount")
        k = "machine";
    else if(chartType == "singlewinsspincount")
        k = "win_number";
    else if(chartType == "renchan")
        k = "renchan";
    else if(chartType == "totalwins")
        k = "machine";
    //console.log(chartType + " " + chartFreq)
    //var startDate =  chartDates[chartType][chartFreq]["from"]; //"2014-01-07";
    //var endDate = chartDates[chartType][chartFreq]["to"]; //"2014-02-08";
    var startDate = $("#from-datepicker").val();
    var endDate = $("#to-datepicker").val();
    if(chartFreq == "month")
    {
        startDate = startDate.substring(0, 7);
        endDate = endDate.substring(0, 7);
    }
//	alert(startDate);i
    hallcode = $("#hallcode li.selected").text();
    machinetype = $("#machinetype li.selected").text();
    machinenumber = $("#machinenumber li.selected").text();
    var url = "/Data?startDate=" + startDate + "&endDate=" + endDate + "&hallcode=" + hallcode + "&machinetype=" + machinetype +"&machinenumber=" + machinenumber + "&chart=" + chartType;
    
//alert(chartType + " " + chartFreq + " " + url);
//chartData[chartType][chartFreq] = [];
    $.getJSON(url, function (data) {
        if(chartData[chartType][chartFreq].length > 0)
            chartData[chartType][chartFreq] = [];

        for (i = 0; i < data.length; i++) {
	if(chartFreq=="day"){
            chartData[chartType][chartFreq].push({
                //date: getDate(data[i].date),
                date: parseDate(data[i]["date"], data[i]["time_of_win"]),
                impressions: data[i]["value"]
            });
	    }
	    else
	    {
            chartData[chartType][chartFreq].push({
                //date: getDate2(data[i].date),
                date: parseDate2(data[i].date),
                impressions: data[i][k]
            });
	    }

        }
	
    //      alert(JSON.stringify(chartData));
        //chrt.validateData();
        chrt.dataProvider = chartData[chartType][chartFreq];
        chrt.validateData();
    });
}

// this method is called when chart is first inited as we listen for "dataUpdated" event
function zoomChart() {
    // different zoom methods can be used - zoomToIndexes, zoomToDates, zoomToCategoryValues
    //chart.zoomToIndexes(chartData.length - 40, chartData.length - 1);
}

// changes cursor mode from pan to select
function setPanSelect() {
    // if (document.getElementById("rb1").checked) {
    //     chartCursor.pan = false;
    //     chartCursor.zoomable = true;
    // } else {
    //     chartCursor.pan = true;
    // }
    // chart.validateNow();
}

function parseDate(input, hr) {
    var parts = input.split('-');
    var p2 = hr.split(":");
    if(p2.length < 2)
    	return new Date(parts[0], parts[1]-1, parts[2]);
    else
    return new Date(parts[0], parts[1] - 1, parts[2], p2[0], p2[1]); // Note: months are 0-based
//	return new Date(input);
}

function getDate(a) {
    a = '' + a;
    a = a.substring(0, 4) + '-' + a.substring(4, 6) + '-' + a.substring(6);
    return parseDate(a);
}
function parseDate2(input) {
    var parts = input.split('-');
    return (new Date(parts[0], parts[1])-1); // Note: months are 0-based
}

function getDate2(a) {
    a = '' + a;
    a = a.substring(0, 4) + '-' + a.substring(4, 6);
    return parseDate2(a);
}
