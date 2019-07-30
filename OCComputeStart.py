import oci
import sys
import json

# Methods to list compute and also to start/stop comute instances

def oci_start_stop_instances(response_data):
    comp_list = {}
    for l,compartment in enumerate(response_data):
        #print("\t\t" + str(l+1)+". "+ str(compartment.id))
        comp_list.update({l+1:compartment.id})
    try:
        print("\n\n\t Choose the Compartment Id to List Compute Instances to STOP/START")
        compt_seq = 14
        print("\n\n\t Compartment ID --> "+str(comp_list[compt_seq]))

        cp = oci.core.compute_client.ComputeClient(config)
        instance_data = cp.list_instances(comp_list[compt_seq]).data 
    
        if instance_data is None:
            pass
        else:        
            inst_list = {}
            cnt = 0
            instances_to_stop = ["Hindalco-PresentationTier-Instance-01","Hindalco-AppTier-Instance-01","Hindalco-DBTier-Instance-01"]
            print("|****************************************************************************************************************|")
            for k,inst in enumerate(instance_data):
                if inst.lifecycle_state in('TERMINATED'):
                    continue
                if inst.display_name in instances_to_stop:
                    cnt+=1
                    print("  "+str(cnt+0)+ ". " + str(inst.display_name) + "-->" + '['+str(inst.lifecycle_state)+']')
                    inst_list.update({cnt:inst.id})
        
            print("|****************************************************************************************************************|")
        
            print("\n\n")
            
            for inst_name in inst_list:
                inst_seq = inst_name
                print("Choosen instance Number is :" + inst_list[inst_seq])
                act_val = "START"
                print(inst_list[inst_seq])
                try:
                    inst_action = cp.instance_action(inst_list[inst_seq], act_val).data
                    print(inst_action.display_name + "-->" + inst_action.lifecycle_state)
                    print(inst_action.time_created)
                    print("|****************************************************************************************************************|")
                except Exception as e:
                    print("\n\t\t{}".format(e.message))            
    except KeyError:
        print("\n\t\t{}".format("You have entered number which is out of range sequence provided above"))
        
    return
   
# INTIAL CONFIGURATION

config = oci.config.from_file("D:\\cygwin64\\home\\vinkarun\\.oci\\config_apacsehubt01","DEFAULT")
identity = oci.identity.IdentityClient(config)
user = identity.get_user(config["user"]).data
compt_id = identity.get_compartment(config["compartment_id"]).data
json_load = json.loads(str(compt_id))
print("This is the compartment: "+str(json_load["compartment_id"]))

# GET LIST OF COMPARTMENTS

response=identity.list_compartments(json_load["compartment_id"])
#print("This is your list of compartments "+str(response.data))

# GET LIST OF COMPUTE/DBCS INSTANCES FOR EACH COMPARTMENT IDS

print("\n\n")
print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
print("|        Listing Compartment Ids and its corresponding Compute Instances along with DBCS Instances        |")
print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

for compartments in response.data:
    if compartments.id != json_load["compartment_id"]:
        continue
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




choice = False
while not choice:
    print("\n\t\t1. Stop Compute Instances")
    choice = "1"
    if choice=="1":
        oci_start_stop_instances(response.data)