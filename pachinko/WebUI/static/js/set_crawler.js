//set_crawler.js
var SetCrawler = {
    crawler_stop : function (tag){
        $(tag).val('START');
        // stoping crawling
    },
    crawler_start: function(tag) {
        $(tag).val("STOP");
        // start crawling
    }
}
$(document).ready(function(){
    $("input[type='button']").click(function(){
        if( $(this).val() === 'START' ){
            SetCrawler.crawler_start(this);
            return;   
        }
        if( $(this).val() === 'STOP' ){
            SetCrawler.crawler_stop(this);
            return;
        }
    });

});