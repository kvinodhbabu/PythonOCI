from oci.object_storage import UploadManager
from oci.object_storage.transfer.constants import MEBIBYTE

import json
import oci
import sys
import os
import os.path
import io
import ast
from oci.object_storage.models import CreateBucketDetails

def progresscallback(bytes_uploaded):
    print("{} additional bytes uploaded".format(bytes_uploaded))

config = oci.config.from_file("D:\\cygwin64\\home\\vinkarun\\.oci\\config","DEFAULT")
identity = oci.identity.IdentityClient(config)
user = identity.get_user(config["user"]).data
print(user)
compartment_dets = config["compartment_id"]
print(compartment_dets)

#################################### creating the bucket###########################################

object_storage = oci.object_storage.ObjectStorageClient(config)
namespace = object_storage.get_namespace().data
print(namespace)
bkt_name = input("\n\t\t Enter Bucket Name to Create Object Storage: ")
request = CreateBucketDetails(name=bkt_name,compartment_id=compartment_dets)

try:
    bucket = object_storage.create_bucket(namespace, request)
    #print(bucket.data)
    print(bucket.data.etag)
except Exception as e:
    print(e.message)

print("Enter the path to move backup files to OCI object storage: ")
directory=input()

user_input=directory
assert os.path.exists(user_input), "I did not find the directory at, "+str(user_input)

print("Files in directory "+str(directory)+" will be uploaded")
bucket_name=bkt_name
user_input=directory

files_to_process = [file for file in os.listdir(directory) if file.endswith('tar.gz')]

################################uploading the data into Sales_Data --> Something wrong here cant upload for some reasons
for upload_file in files_to_process:
    print('Uploading file {}'.format(upload_file))
    print(upload_file)
    partsize = 1000 * MEBIBYTE
    print(partsize)
    object_name=upload_file
    filename=os.path.join(directory,upload_file)
    upload_manager=UploadManager(object_storage,allow_parallel_uploads=True,allow_multipart_uploads=True)
    response=upload_manager.upload_file(namespace,bucket_name,object_name,filename,part_size=partsize,progress_callback=progresscallback)
    print(response.data)
