from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, RootModel
from typing import Dict, Union, Literal, List
import numpy as np
from compute_size import estimate_target_object_size,get_depth_focallength
import glob 
import json 
import requests
import os 

import logging

# Configure logging
logging.basicConfig(
    filename="app.log",            # Log file name
    filemode="a",                  # Append mode
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
    level=logging.INFO             # Log level
)

app = FastAPI()

from s3_util import download_images_from_S3,uuid2filename

class EstimateSizeRequest(BaseModel):
    uuid: str
    bucket: str
    coords_refobj: List[List[float]]  # 4x2 array
    coords_targetobj: Dict[str, List[List[float]]]  # 4x2 array
    ref_obj_w_m: float
    ref_obj_h_m: float

class EstimateDepthRequest(BaseModel):
    uuid: str
    bucket: str



class EstimateDepthResponse(BaseModel):
    success: bool



class LineSize(BaseModel):
    type: Literal["line"]
    length: float
    width_top: float
    width_bottom: float
    height_left: float
    height_right: float

class PolygonSize(BaseModel):
    type: Literal["polygon"]
    width_top: float
    width_bottom: float
    height_left: float
    height_right: float
    area: float

class EstimateSizeResponse(RootModel[Dict[str, Union[LineSize, PolygonSize]]]):
    pass
    
@app.post("/estimate_depth", response_model=EstimateDepthResponse)
def estimate_depth(req: EstimateDepthRequest):
    try:

        uuid=req.uuid
        bucket=req.bucket

        img_path=download_images_from_S3(
            f'{uuid}',
            bucket,
            f'data/'
        )
        if img_path == '':
        
            raise HTTPException(status_code=404, detail="Image not found in S3 bucket")

        
        depth, f_px, cx, cy = get_depth_focallength(
            img_path
        )

        print('************',depth, f_px, cx, cy )

        logging.info(f"Depth estimation for UUID {uuid} completed successfully.")
        logging.info(f"Depth shape: {depth.shape}, Focal length: {f_px}, Cx: {cx}, Cy: {cy}")
        
        
        uuid=uuid2filename(uuid)
        depth_name=f'{uuid}_{f_px}_{cx}_{cy}_.npy'
        np.save(f"depth_folder/{depth_name}", depth)

        return EstimateDepthResponse(success=True)

    
    except Exception as e:
        logging.error("Error in /estimate_depth:\n" + traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e)) 

@app.post("/estimate_size", response_model=EstimateSizeResponse)
def estimate_size(req: EstimateSizeRequest):
    try:

        uuid=req.uuid
        bucket=req.bucket
        coords_refobj=req.coords_refobj
        coords_targetobj=req.coords_targetobj
        ref_obj_w_m=req.ref_obj_w_m
        ref_obj_h_m=req.ref_obj_h_m


        depth_images=[f for f in glob.glob(f"depth_folder/*.npy") if uuid2filename(uuid) in f]

        if len(depth_images) == 0:

            img_path=download_images_from_S3(
            f'{uuid}',
            bucket,
            f'data/'
        )

            uuid=uuid2filename(uuid)

            depth, f_px, cx, cy = get_depth_focallength(
            img_path
            )
            depth_name=f'{uuid}_{f_px}_{cx}_{cy}_.npy'
            np.save(f"depth_folder/{depth_name}", depth)
        else:
            depth = np.load(depth_images[0])

            f_px,cx,cy=depth_images[0].split('_')[-4:-1]

            f_px=float(f_px)
            cx=float(cx)
            cy=float(cy)

        target_size= estimate_target_object_size(
            depth,f_px,cx,cy,
            req.coords_refobj,
            req.coords_targetobj,
            req.ref_obj_w_m,
            req.ref_obj_h_m
        )
        logging.info(f"Estimated size for UUID {uuid}: {target_size}")

        return target_size
    except Exception as e:
        logging.error("Error in /estimate_size:\n" + traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e)) 