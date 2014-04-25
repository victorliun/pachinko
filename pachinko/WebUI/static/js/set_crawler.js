//set_crawler.js
var SetCrawler = {
    crawler_stop : function (tag){
        $(tag).val('START');
        // stoping crawling
    },
    crawler_start: function(tag) {
        $(tag).val("STOP");
        // start crawling
    },
    enableMachineTypesAutocomplete : function(val){
        $("#target_machine_types").bind( "keydown", function( event ) {
            if ( event.keyCode === $.ui.keyCode.TAB &&
                $( this ).data( "ui-autocomplete" ).menu.active ) {
                event.preventDefault();
            }
            else if (event.keyCode === $.ui.keyCode.ENTER){
                $(".ui-autocomplete").hide();
            }
        }).autocomplete({
            minLength:1,
            source: "/get_codes?hallcode="+val,
            focus: function() {
              return true;
            },
            select: function( event, ui ) {
              var terms = this.value.split(/,\s*/);
              // remove the current input
              terms.pop();
              // add the selected item
              terms.push( ui.item.value );
              // add placeholder to get the comma-and-space at the end
              terms.push( "" );
              this.value = terms.join( ", " );
              return false;
            },
            change: function( event,ui){
                if (this.value.match(/^\d+(,\s*\d+)*$/) != null){
                    $("#machine_type_helper").hide();
                }
                else {
                    $("#machine_type_helper").show();
                }
            }
        }); 
    },
}
$(document).ready(function(){
    // validate and submit form
    $("input[type='button']").click(function(){
        if( $(".helper").length != 0)
        {
            return;
        }
        
        if( $(this).val() === 'START' ){
            SetCrawler.crawler_start(this);
            return;   
        }
        if( $(this).val() === 'STOP' ){
            SetCrawler.crawler_stop(this);
            return;
        }
    });

    // autocomplete hallcode
    $( "#target_hallcode" ).bind( "keydown", function( event ) {
        if ( event.keyCode === $.ui.keyCode.ENTER )
            $(".ui-autocomplete").hide();
    }).autocomplete({
        minLength: 1,
        source: "/get_codes",
        select: function( event, ui ) {
            SetCrawler.enableMachineTypesAutocomplete(this.value);
            return false;
        },
        change: function( event,ui){
            if (this.value.match(/^\d+\s*$/) != null){
                $("#hallcode_helper").hide();
            }
            else {
                $("#hallcode_helper").show();
            }
        }
    });

    //validate yahoo account
    $("input[name='password']").blur(function(){
        var password = this.value;
        var account = $("input[name='username']").val();
        $.ajax({
            dataType:'json',
            url:"/check_yahoo_account",
            data:{'username':account, 'password':password},
            success: function (data) {
                if (data.status){
                    $("#yahoo_helper").hide();
                }else{
                    $("#yahoo_helper").show();
                }
            }
        });
    });

});
