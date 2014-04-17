$(document).ready(function(){
    updateNext('hallcode','hallcode');
    updateTable(this, 'tabledata');
    $("a#by_hall").parent().hover(function(){
        //updateNext(this, 'machinetype');
        $("#hallcode").show();
    }, function(){
        $("#hallcode").hide();
       // $(this).find('#hallcode').slideToggle();
    });

    $("ul#hallcode li").click(function(){
        $("a#by_hall").html(this.textContent);
        $("#hallcode").hide();
        $("#hallcode li.selected").removeClass("selected");
        $(this).addClass("selected");
        updateNext(this, 'machinetype')
        $("a#by_hall").focus();
    });
    
    $("a#by_hall").keydown(function(event){
        if (event.keyCode == 39){//right arrow key down 
            var selected = $("#hallcode li.selected");
            if (selected.length){
                selected.removeClass("selected");
                next = selected.next();
                if (next.length == 0)
                    return;
            }
            else{
                next = $("#hallcode li:first");
                next.addClass("selected");               
            }
            next.addClass("selected");
            $("a#by_hall").html(next.html());
            updateNext(next,"machinetype");
        }
        else if (event.keyCode == 37){// left arrow key down
            var selected = $("#hallcode li.selected");
            if (selected.length){
                prev = selected.prev();
                if (prev.length == 0)
                    return;
                selected.removeClass("selected");
            }
            else{
                prev = $("#hallcode li:last");              
            }
            prev.addClass("selected");
            $("a#by_hall").html(prev.html());
            updateNext(prev,"machinetype");
        }      
    });
    //by machine type
    $("a#by_machine_type").parent().hover(function(){
        $("#machinetype").show();
    }, function(){
        $("#machinetype").hide();
    });
    $("ul#machinetype").on("click","li", function(){
        $("a#by_machine_type").html(this.textContent);
        $("#machinetype").hide();
        $("#machinetype li.selected").removeClass("selected");
        $(this).addClass("selected");
        updateNext(this, 'machinenumber')
        $("a#by_machine_type").focus();
    });
    $("a#by_machine_type").keydown(function(event){
        if (event.keyCode == 39){//right arrow key down 
            var selected = $("#machinetype li.selected");
            if (selected.length){
                next = selected.next();
                if (next.length == 0)
                    return;
                selected.removeClass("selected");
            }
            else{
                next = $("#machinetype li:first");              
            }
            next.addClass("selected");
            $("a#by_machine_type").html(next.html());
            updateNext(next,"machinenumber");
        }
        else if (event.keyCode == 37){// left arrow key down
            var selected = $("#machinetype li.selected");
            if (selected.length){
                selected.removeClass("selected");
                prev = selected.prev();
                if (prev.length == 0)
                    return;
            }
            else{
                prev = $("#machinetype li:last");              
            }
            prev.addClass("selected");
            $("a#by_machine_type").html(prev.html());
            updateNext(prev,"machinenumber");
        }      
    });

    //by machine number
    $("a#by_machine").parent().hover(function(){
        $("#machinenumber").show();
    }, function(){
        $("#machinenumber").hide();
    });
    $("ul#machinenumber").on("click","li", function(){
        $("a#by_machine").html(this.textContent);
        $("#machinenumber").hide();
        $("#machinenumber li.selected").removeClass("selected");
        $(this).addClass("selected");
        updateTable(this, 'tabledata')
        $("a#by_machine").focus();
    });
    $("a#by_machine").keydown(function(event){
        if (event.keyCode == 39){//right arrow key down 
            var selected = $("#machinenumber li.selected");
            if (selected.length){
                next = selected.next();
                if (next.length == 0)
                    return;
                selected.removeClass("selected");
            }
            else{
                next = $("#machinenumber li:first");              
            }
            next.addClass("selected");
            $("a#by_machine").html(next.html());
            updateTable(next,"tabledata");
        }
        else if (event.keyCode == 37){// left arrow key down
            var selected = $("#machinenumber li.selected");
            if (selected.length){
                selected.removeClass("selected");
                prev = selected.prev();
                if (prev.length == 0)
                    return;
            }
            else{
                prev = $("#machinenumber li:last");            
            }
            prev.addClass("selected");
            $("a#by_machine").html(prev.html());
            updateTable(prev,"tabledata");
        }      
    });
});