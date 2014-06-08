from connectMongo import DBConnection

def run_extract():
    """
    This script will extract existed hallcode machine_types and machine_numbers
    from pachinko_data2 'data' collection to machine_details.
    execute this by:
        python extract_machines.py
    """
    print "start Process"
    dbconnection = DBConnection()

    machine_detail = dbconnection.get_collection('pachinko_data2','machine_details')
    hallcodes = dbconnection.getHallCode('hallcode')
    #insert hallcode
    for hallcode in hallcodes:
        dbconnection.insert_hallcode(hallcode)
        machine_types = dbconnection.getMachineDetails('hallcode',hallcode,'','','machine_type')
        #insert machine_types
        for machine_type in machine_types:
            dbconnection.insert_machine_type(hallcode, machine_type)
            machines = dbconnection.getMachineDetails('hallcode',hallcode,'machine_type',
                machine_type,'machine')
            for machine in machines:
                dbconnection.insert_machine(hallcode, machine_type, machine)
                print "insert %s in %s in %s"%(machine, machine_type, hallcode)

    print "Process finished."

if __name__ == '__main__':
    run_extract()
