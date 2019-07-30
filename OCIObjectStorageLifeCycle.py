import json
import oci
import sys
import os
import os.path
from datetime import date
from datetime import datetime
from datetime import timedelta
import io
import ast
from oci.object_storage.models import CreateBucketDetails
from oci.object_storage import UploadManager
from oci.object_storage.models import CreatePreauthenticatedRequestDetails
from oci.object_storage.transfer.constants import MEBIBYTE

def delete_bucket(namespace,compartment_dets):
    
    json_dict = list_buckets(namespace,compartment_dets)
    try:
        bucket_name = input("\n \t\tEnter the bucket number from above to Delete: ")
        bucket = object_storage.get_bucket(namespace, json_dict[int(bucket_name)])
            
        val = input("\n\t\tEnter Y/y/yes only to Continue bucket and object deletion: ")
        if val=='Y' or val=='y' or val=='yes':
            object_list = object_storage.list_objects(namespace, json_dict[int(bucket_name)])
            for idx2,objs in enumerate(object_list.data.objects):
                print('\n\t\t\t{}. Deleting object {}'.format(idx2+1,objs.name))
                object_storage.delete_object(namespace, json_dict[int(bucket_name)], objs.name)
            try:
                par_list = object_storage.list_preauthenticated_requests(namespace, json_dict[int(bucket_name)])
                #print(par_list.data)
                ##### Delete Pre-authentication request before deleting bucket from object storage ###########
                for idxs2,pars in enumerate(par_list.data):
                    print('\n\t\t\t{}. Deleting Pre-Authentication Request {}'.format(idxs2+1,pars.id))
                    object_storage.delete_preauthenticated_request(namespace, json_dict[int(bucket_name)], pars.id)
                bucket = object_storage.delete_bucket(namespace, json_dict[int(bucket_name)])
            except Exception as e:
                print("\n\t\tError" + e.message)            
            print("\n\t\tBucket '{}' and it's objects deleted".format(json_dict[int(bucket_name)]))
        else:
            print("\n\t\tYou have not accepted to delete bucket and its object try again by providing Y/y/yes only")
        
    #except Exception as e:
    #    print("\n\t\tError: " + e.message)
    except KeyError:
        print('\n\t\tTry again: Your input: {} contains non-numeric value'.format(bucket_name))
                
    
def list_buckets(namespace,compartment_dets):
    print("\n\t\t Buckets in this Compartment: ")  
    # Try catch block for error handling if bucket or object does not exist
    try:
        bucket = object_storage.list_buckets(namespace, compartment_dets)
        json_dict = {}
        for idx1,dicts in enumerate(bucket.data):
            json_load = json.loads(str(dicts))
            print("\n\t\t  {}.{}".format(idx1+1,json_load["name"]))
            json_dict.update({idx1+1:json_load["name"]})
    except Exception as e:
        print(e.args)
    return json_dict

def delete_object_in_os_bucket(namespace,compartment_dets):
    json_dict = list_buckets(namespace,compartment_dets)
    try:
        bucket_name = input("\n\t\tEnter the bucket number from which object to be deleted: ")
        object_list = object_storage.list_objects(namespace, json_dict[int(bucket_name)])
        print("\n\t\tListing Objects from Bucket {}: ".format(json_dict[int(bucket_name)]))
        json_dict_obj = {}
        for idx,objs in enumerate(object_list.data.objects):
            print('\n\t\t\t{}.{}'.format(idx+1,objs.name))
            json_load = json.loads(str(objs))
            json_dict_obj.update({idx+1:json_load["name"]})
        obj_name = input("\n\t\tEnter the object number to be deleted: ")
        try:
            object_list = object_storage.get_object(namespace, json_dict[int(bucket_name)],json_dict_obj[int(obj_name)])
            print('\n\t\t  Object {} Found in Bucket will be deleted Now'.format(json_dict_obj[int(obj_name)]))
            object_storage.delete_object(namespace, json_dict[int(bucket_name)], json_dict_obj[int(obj_name)])
            print('\n\t\t   Deleted Object {}'.format(json_dict_obj[int(obj_name)]))  
        except Exception as e:
            print("\n\t\t{}".format(e.message))
    except KeyError:
        print("\n\t\tError: Incorrect Bucket Number Entered" )   
    return

def list_objects_in_os_bucket(namespace,compartment_dets,**kwargs):
    json_dict = list_buckets(namespace,compartment_dets)
    bucket_name = input("\n\t\t Enter the bucket number from which objects are to be listed: ")
    
    try:
        object_lists = object_storage.list_objects(namespace, json_dict[int(bucket_name)])
        print("\n\t\t Listing Objects from Bucket {}: ".format(json_dict[int(bucket_name)]))
        for idx,objs in enumerate(object_lists.data.objects):
            print('\n\t\t\t{}.{}'.format(idx+1,objs.name))
        return json_dict[int(bucket_name)]
    except KeyError:
        print("\n\t\tError: UnKnown Bucket Number Entered")

def progresscallback(bytes_uploaded):
    print("\n\t\t{} additional bytes uploaded".format(bytes_uploaded))
    
def create_pre_authenticated_request_for_os_object(namespace,compartment_dets):
    bucket_name = list_objects_in_os_bucket(namespace,compartment_dets)
    obj_name = input("\n\t\tEnter the object name from above to create PAR:")
    try:
        object_list = object_storage.get_object(namespace, bucket_name,obj_name)
        print('\n\t\t  Object {} Found in Bucket {} will be used to create PAR'.format(obj_name,bucket_name))
        names ="par-object-"+ str(obj_name)+ "-" + datetime.now().strftime('%Y%m%d')+ "-" + datetime.now().strftime('%H%M')
        print("\n\t\t" + names)
        objt_name = obj_name
        print("\n\t\t1. ObjectRead")
        print("\n\t\t2. ObjectWrite")
        print("\n\t\t3. ObjectReadWrite")
        print("\n\t\t4. AnyObjectWrite")
        object_access_type = {1:"ObjectRead", 2:"ObjectWrite", 3:"ObjectReadWrite", 4:"AnyObjectWrite"}
        try:
            obj_access_type = input("\n\t\tEnter object access type choose from the list above: ")
            num_days = input('\n\t\tEnter number of days for PAR validity: ')
            acc_type = object_access_type[int(obj_access_type)]
    
            number_of_days = int(num_days)
            end_date =datetime.utcnow() + timedelta(days=number_of_days)
            end_date = end_date.strftime('%Y-%m-%d')
            t = datetime.time(datetime.utcnow()).strftime('%H:%M:%S')
            time_det_expires = str(end_date)+ "T" +str(t)+"Z"
    
            create_preauthenticated_request_details= CreatePreauthenticatedRequestDetails(name=names,object_name=objt_name,access_type=acc_type,time_expires=time_det_expires)
            # print("\n\t\t"+str(create_preauthenticated_request_details))
            par_request = object_storage.create_preauthenticated_request(namespace, bucket_name, create_preauthenticated_request_details)
            json_load = json.loads(str(par_request.data))
            par_access_uri = json_load["access_uri"]
            var_region = config["region"]
            print("\n\thttps://objectstorage."+ var_region +".oraclecloud.com" + par_access_uri)            
        except KeyError:
            print('\n\t\tTry again: Your input: {} contains non-numeric value'.format(obj_access_type))
    except Exception as e:
        print("\n\t\t{}".format(e.message))    
                
def upload_objects_to_os_bucket(namespace):
    bucket_name = input("\n\tEnter the bucket name to upload objects: ")
    request = CreateBucketDetails(name=bucket_name,compartment_id=compartment_dets)
    try:
        bucket = object_storage.create_bucket(namespace, request)
        #print(bucket.data)
        print("\n\t"+bucket.data.etag)
    except Exception as e:
        print("\n\t" + e.message)

    directory=input("\n\tEnter the path to move files to OCI object storage: ")

    user_input=directory
    assert os.path.exists(user_input), "I did not find the directory at, "+str(user_input)

    print("\n\tFiles in directory " + str(directory) +" will be uploaded")
    user_input=directory

    files_to_process = [file for file in os.listdir(directory) if file.endswith('tar.gz')]

    for upload_file in files_to_process:
        print('\n\tUploading file {}'.format(upload_file))
        print('\n\t' + upload_file)
        partsize = 1000 * MEBIBYTE
        object_name=upload_file
        filename=os.path.join(directory,upload_file)
        upload_manager=UploadManager(object_storage,allow_parallel_uploads=True,allow_multipart_uploads=True)
        response=upload_manager.upload_file(namespace,bucket_name,object_name,filename,part_size=partsize,progress_callback=progresscallback)
        if str(response.data)=='None':
              print("\n\tUpload Complete")
    return

####################################  This is where the main program logic begins  ##########################################

print("Sample path for Windows and Linux/Unix\n")
print("1. Windows path example ==> D:\\cygwin64\\home\\someuser\\.oci\\config\n")
print("2. Linux/Unix path example ==> /home/opc/.oci/config\n")

config_path = input("\n\tEnter path of OCI config: ")
config = oci.config.from_file(config_path + "config","DEFAULT")
identity = oci.identity.IdentityClient(config)
user = identity.get_user(config["user"]).data
# print(user)
compartment_dets = config["compartment_id"]
print("\n\tCompartment Ocid: "+compartment_dets)

#################################### Read buckets inside a particular compartment ###########################################

object_storage = oci.object_storage.ObjectStorageClient(config)
namespace = object_storage.get_namespace().data
print("\n\tNamespace: " + namespace)

choice = False
while not choice:
    print("\n\n\t####################### Choose One of the Options Below ##################################\n")
    print("\t 1. List Buckets")
    print("\t 2. Delete Bucket")
    print("\t 3. Delete Object from Bucket")
    print("\t 4. List Object from Bucket")
    print("\t 5. Upload Object to Bucket")
    print("\t 6. Create Pre-Authenticated Request for Object in Bucket")
    print("\t 7. Exit")
    choice = input("\n \t\tEnter options between 1 to 6: ")
    try:
        if (int(choice)<1 and int(choice)>6):
            choice=False
            print("Enter values only between 1 and 6")
            continue
    except ValueError:
        print('\n\t\tTry again: Your input: {} contains non-numeric data'.format(choice))
        choice=False
        continue
    if int(choice)==1:
        list_buckets(namespace,compartment_dets)
        choice=False
        continue
    elif int(choice)==2:
        delete_bucket(namespace,compartment_dets)
        choice=False
        continue
    elif int(choice)==3:
        delete_object_in_os_bucket(namespace,compartment_dets)
        choice=False
        continue
    elif int(choice)==4:
        list_objects_in_os_bucket(namespace,compartment_dets)
        choice=False
        continue
    elif int(choice)==5:
        upload_objects_to_os_bucket(namespace)
        choice=False
        continue
    elif int(choice)==6:
        create_pre_authenticated_request_for_os_object(namespace,compartment_dets)
        choice=False
        continue
    elif int(choice)==7:
        print("\n\n\t Bye Bye....")
        break
    else:
        choice=False
        print("\n\t\tSelect Correct options")
        continue