import json
loaded_machines = {}

def getNextMachine(ghost):
    print loaded_machines, len(loaded_machines)
    js = """
    var done = """ + json.dumps(loaded_machines.keys()) + """;
    var buttons = document.getElementsByTagName('a');
    var clicked_href = {};
    var qwe = 100;
    for(var i=0; i<buttons.length; i++){
        if(buttons[i].href.indexOf("tableHistoryClick") != -1){
                if(done.indexOf(buttons[i].href) == -1){
                        qwe = buttons[i].href;
                        break;
                }
        }
    } 
    qwe;
    """
    result, resources = ghost.evaluate(js)
    print "extracted machinetype", result
    loaded_machines[str(result)] = 1
    return result

