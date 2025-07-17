# import boto3
# import os 

# folder_path='mCLQinVwxy5mGqFfwT2SNWS'

# bucket='mc-call'
# save_folder='data/'

# def download_images_from_S3(folder_path,bucket,save_folder):
#     s3 = boto3.resource('s3')
#     my_bucket = s3.Bucket(bucket)
#     prefix = folder_path
#     for s3_object in my_bucket.objects.filter(Prefix=prefix):
#         path, filename = os.path.split(s3_object.key)

#         os.makedirs(save_folder, exist_ok=True)
#         my_bucket.download_file(s3_object.key, save_folder + filename + '.jpeg')

#         return save_folder + filename + '.jpeg'
#     return '' 

# download_images_from_S3(folder_path,bucket,save_folder)


from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List,Dict
import numpy as np
from compute_size import estimate_target_object_size,get_depth_focallength
import glob 
import json 
import requests


from s3_util import download_images_from_S3


uuid='mCLQinVwxy5mGqFfwT2SNWS'

bucket='mc-call'



img_path='/mnt/ObjectMeasurement/ml-depth-pro/depth_foldermCLQinVwxy5mGqFfwT2SNWSi.jpg'



depth, f_px, cx, cy = get_depth_focallength(
    img_path
)

# print('************',depth, f_px, cx, cy )

# depth_name=f'{uuid}_{f_px}_{cx}_{cy}_.npy'
# np.save(f"depth_folder/{depth_name}", depth)

payload = {
    "uuid": "mCLQinVwxy5mGqFfwT2SNWSi",
    "bucket": "mc-call",
    "coords_refobj": [
        [1747.199954553324, 484.7737183750863],
        [2112.053140148892, 373.11758362458653],
        [2238.6348576004157, 897.9014169519352],
        [1858.8897052458449, 987.2263247523348]
        ],
    "ref_obj_w_m": 0.14,
    "ref_obj_h_m": 0.21,
    "coords_targetobj": {
        "3391ae33-2fde-48fd-9603-4bcde0eeb2a4": [
            [920.6957994286704, 853.2389630517353],
            [1252.042059816482, 495.93933185013617],
            [1732.3079877943212, 1005.835680544085],
            [1363.7318105090028, 1351.969698270634]
        ]}
}


coords_refobj=payload['coords_refobj']
coords_targetobj=payload['coords_targetobj']
ref_obj_w_m=payload['ref_obj_w_m']
ref_obj_h_m=payload['ref_obj_h_m']


depth_images=[f for f in glob.glob(f"depth_folder/*.npy") if uuid in f]

if len(depth_images) == 0:

    img_path=download_images_from_S3(
    f'{uuid}',
    bucket,
    f'data/'
)

    depth_name=f'{uuid}_{f_px}_{cx}_{cy}_.npy'
    depth, f_px, cx, cy = get_depth_focallength(
    img_path
    )
    np.save(f"depth_folder/{depth_name}", depth)
else:
    depth = np.load(depth_images[0])

    f_px,cx,cy=depth_images[0].split('_')[-4:-1]

    f_px=float(f_px)
    cx=float(cx)
    cy=float(cy)

target_size= estimate_target_object_size(
    depth,f_px,cx,cy,
    coords_refobj,
    coords_targetobj,
    ref_obj_w_m,
    ref_obj_h_m
)
        
