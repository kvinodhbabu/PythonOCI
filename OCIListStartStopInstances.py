import oci
import sys

# Methods to list compute/dbcs and also to start/stop instances

def oci_list_compute(response_data):
    comp_list = {}
    for i,compartment in enumerate(response_data):
        print("\t\t" + str(i+1)+". "+ str(compartment.id))
        comp_list.update({i+1:compartment.id})    
    compt_seq = numInput('\n\n\t Choose the Compartment Id to List Compute Instances')
    print("\n\n\t Choosen Compartment ID --> "+str(comp_list[compt_seq]))
    print("\n")
    cp = oci.core.compute_client.ComputeClient(config)
    instance_data = cp.list_instances(comp_list[compt_seq]).data

    if instance_data is None:
        pass
    print("\t\t|*******************************************************************************************|")
    for inst_details in instance_data:
        if inst_details.lifecycle_state not in('TERMINATED'):
            print("\t\t| Instance Name: "+ inst_details.display_name)
            print("\t\t| Image Id: "+ inst_details.image_id)
            print("\t\t| Launch Mode: "+ inst_details.launch_mode)
            print("\t\t| LifeCycle State: "+ inst_details.lifecycle_state)
            print("\t\t| Region: "+ inst_details.region)
            print("\t\t|*******************************************************************************************|")
    return

def oci_list_dbcs(response_data):    
    comp_list = {}
    for i,compartment in enumerate(response_data):
        print("\t\t" + str(i+1)+". "+ str(compartment.id))
        comp_list.update({i+1:compartment.id})

    compt_seq = numInput('\n\n\t Choose the Compartment Id to List DBCS Instances')
    
    print("\n\n\t Choosen Compartment ID --> "+str(comp_list[compt_seq]))    

    dbcs = oci.database.DatabaseClient(config)
    dbinst = dbcs.list_db_systems(comp_list[compt_seq]).data
    
    
    for db_inst_details in dbinst:
        if db_inst_details is None:
            continue
        if db_inst_details.lifecycle_state not in('TERMINATED'):
            print("\n")
            print("|=============================================================================================|")
            print("| DBCS DB System Details: "+ db_inst_details.display_name.ljust(68)+"|")
            print("| DBCS Availability Domain: "+ db_inst_details.availability_domain.ljust(66)+"|")
            print("| DBCS Cluster Name: "+ str(db_inst_details.cluster_name).ljust(73)+"|")
            print("| DBCS CPU Core Count: "+ str(db_inst_details.cpu_core_count).ljust(71)+"|")
            print("| DBCS Data Storage Percentage: "+ str(db_inst_details.data_storage_percentage).ljust(62)+"|")
            print("| DBCS Data Storage Size in GB's: "+ str(db_inst_details.data_storage_size_in_gbs).ljust(60)+"|")
            print("| DBCS Database Edition: "+ str(db_inst_details.database_edition).ljust(69)+"|")
            print("| DBCS Disk Redundancy: "+ str(db_inst_details.disk_redundancy).ljust(70)+"|")        
            print("| DBCS LifeCycle Details: "+ str(db_inst_details.lifecycle_details).ljust(68)+"|")
            print("| DBCS LifeCycle State: "+ str(db_inst_details.lifecycle_state).ljust(70)+"|")
            print("| DBCS Node Count: "+ str(db_inst_details.node_count).ljust(75)+"|")
            print("| DBCS Instance Shape: "+ str(db_inst_details.shape).ljust(71)+"|")       
            db_homes = dbcs.list_db_homes(compartments.id,db_inst_details.id).data
            for home_list in db_homes:
                db_list = dbcs.list_databases(compartments.id,home_list.id).data
                for database_list in db_list:
                    print("| DBCS DB Name: "+ str(database_list.db_name).ljust(78)+"|") 
                    print("| DBCS DB Unique Name: "+ str(database_list.db_unique_name).ljust(71)+ "|")
                    print("| DBCS DB Character Set: "+ str(database_list.ncharacter_set).ljust(69)+"|")
                    print("| DBCS DB Time Created: "+ str(database_list.time_created).ljust(70)+"|")
            print("|=============================================================================================|")
            print("\n")
            
    return

def numInput(txtToDisplay):
    while True:
        try:
            userInput = int(raw_input(txtToDisplay))
        except ValueError:
            print("\n\t\t You must enter a number")
            continue
        else:
            return userInput
            break 

def oci_start_stop_instances(response_data):
    comp_list = {}
    for l,compartment in enumerate(response_data):
        print("\t\t" + str(l+1)+". "+ str(compartment.id))
        comp_list.update({l+1:compartment.id})
    
    compt_seq = numInput("\n\n\t Choose the Compartment Id to List Compute Instances to STOP/START")
    print("\n\n\t Compartment ID --> "+str(comp_list[compt_seq]))

    cp = oci.core.compute_client.ComputeClient(config)
    instance_data = cp.list_instances(comp_list[compt_seq]).data 
    
    if instance_data is None:
        pass
    else:        
        inst_list = {}
        print("|****************************************************************************************************************|")
        for k,inst in enumerate(instance_data):
            print("  "+str(k+1)+ ". " + str(inst.id) + "-->" + str(inst.display_name))
            inst_list.update({k+1:inst.id})
        
        print("|****************************************************************************************************************|")
        
        print("\n\n")
        inst_seq = numInput("Choose the Compute instance number to start/stop")
        print("Choose instance Number is :" + inst_seq)
       
        print("Enter the actions SOFTSTOP/SOFTRESET/START: ")
        act_val = input()
        print(inst_list[inst_seq])        
        inst_action = cp.instance_action(inst_list[inst_seq], act_val).data
        print(inst_action.display_name + "-->" + inst_action.lifecycle_state)
        print(inst_action.time_created)
        print("|****************************************************************************************************************|")
    return
   
# INTIAL CONFIGURATION

config = oci.config.from_file("D:\\cygwin64\\home\\vinkarun\\.oci\\config_apacsehubt01","DEFAULT")
identity = oci.identity.IdentityClient(config)
user = identity.get_user(config["user"]).data
compt_id = identity.get_user(config["compartment_id"]).data
print(compt_id )

# GET LIST OF COMPARTMENTS

response=identity.list_compartments(compt_id )
#print("This is your list of compartments "+str(response.data))

# GET LIST OF COMPUTE/DBCS INSTANCES FOR EACH COMPARTMENT IDS

print("\n\n")
print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
print("|        Listing Compartment Ids and its corresponding Compute Instances along with DBCS Instances        |")
print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

for compartments in response.data[compartment_id]:
    print("\n\n")    
    print("Compartment ID --> "+ compartments.id)
    cp = oci.core.compute_client.ComputeClient(config)
    instance = cp.list_instances(compartments.id).data

    if instance is None:
        continue
    print("|+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++|")
    for inst_details in instance:
        if inst_details.lifecycle_state not in('TERMINATED'):
            print("# Instance Name: "+ inst_details.display_name)
            print("# Image Id: "+ inst_details.image_id)
            print("# Launch Mode: "+ inst_details.launch_mode)
            print("# LifeCycle State: "+ inst_details.lifecycle_state)
            print("# Region: "+ inst_details.region)
            print("|+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++|")
    # GET LIST OF DBCS INSTANCES 
    dbcs = oci.database.DatabaseClient(config)
    dbinst = dbcs.list_db_systems(compartments.id).data
        
    for db_inst_details in dbinst:
        if db_inst_details is None:
            continue
        if db_inst_details.lifecycle_state not in('TERMINATED'):
            print("\n")
            print("|=============================================================================================|")
            print("| DBCS DB System Details: "+ db_inst_details.display_name.ljust(68)+"|")
            print("| DBCS Availability Domain: "+ db_inst_details.availability_domain.ljust(66)+"|")
            print("| DBCS Cluster Name: "+ str(db_inst_details.cluster_name).ljust(73)+"|")
            print("| DBCS CPU Core Count: "+ str(db_inst_details.cpu_core_count).ljust(71)+"|")
            print("| DBCS Data Storage Percentage: "+ str(db_inst_details.data_storage_percentage).ljust(62)+"|")
            print("| DBCS Data Storage Size in GB's: "+ str(db_inst_details.data_storage_size_in_gbs).ljust(60)+"|")
            print("| DBCS Database Edition: "+ str(db_inst_details.database_edition).ljust(69)+"|")
            print("| DBCS Disk Redundancy: "+ str(db_inst_details.disk_redundancy).ljust(70)+"|")        
            print("| DBCS LifeCycle Details: "+ str(db_inst_details.lifecycle_details).ljust(68)+"|")
            print("| DBCS LifeCycle State: "+ str(db_inst_details.lifecycle_state).ljust(70)+"|")
            print("| DBCS Node Count: "+ str(db_inst_details.node_count).ljust(75)+"|")
            print("| DBCS Instance Shape: "+ str(db_inst_details.shape).ljust(71)+"|")       
            db_homes = dbcs.list_db_homes(compartments.id,db_inst_details.id).data
            for home_list in db_homes:
                db_list = dbcs.list_databases(compartments.id,home_list.id).data
                for database_list in db_list:
                    print("| DBCS DB Name: "+ str(database_list.db_name).ljust(78)+"|") 
                    print("| DBCS DB Unique Name: "+ str(database_list.db_unique_name).ljust(71)+ "|")
                    print("| DBCS DB Character Set: "+ str(database_list.ncharacter_set).ljust(69)+"|")
                    print("| DBCS DB Time Created: "+ str(database_list.time_created).ljust(70)+"|")
            print("|=============================================================================================|")
            print("\n")
            
choice = False
while not choice:
    print("\n\n\t Choose Either Compute/DBCS")
    print("\t\t 1. Compute")
    print("\t\t 2. DBCS")
    print("\t\t 3. Start/Stop Compute Instances")
    print("\t\t 4. Exit")
    choice = input("\n \t\tEnter options between 1 to 4: ")
    if choice==1:
        oci_list_compute(response.data)
    elif choice==2:
        oci_list_dbcs(response.data)
    elif choice==3:
        oci_start_stop_instances(response.data)
    elif choice==4:
        break
    else:    
        choice=False
        print("Select Correct options")
        continue