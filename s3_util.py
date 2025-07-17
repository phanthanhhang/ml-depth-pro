import boto3
import os 

def uuid2filename(uuid):

    uuid= uuid.replace('/', '_')

    return os.path.splitext(uuid)[0]

def download_images_from_S3(folder_path,bucket,save_folder):
    s3 = boto3.resource('s3')
    my_bucket = s3.Bucket(bucket)
    prefix = folder_path
    for s3_object in my_bucket.objects.filter(Prefix=prefix):
        path, filename = os.path.split(s3_object.key)



        os.makedirs(save_folder, exist_ok=True)

        file_name= uuid2filename(s3_object.key)+ '.jpeg'

        my_bucket.download_file(s3_object.key, save_folder + file_name)

        return save_folder + file_name 
    return '' 

