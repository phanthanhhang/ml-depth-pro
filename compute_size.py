from PIL import Image
import depth_pro
import torch
import numpy as np
from matplotlib import pyplot as plt

def get_torch_device() -> torch.device:
    """Get the Torch device."""
    device = torch.device("cpu")
    if torch.cuda.is_available():
        device = torch.device("cuda:0")
    elif torch.backends.mps.is_available():
        device = torch.device("mps")
    return device

# Load and preprocess an image.
model, transform = depth_pro.create_model_and_transforms(
    device=get_torch_device(),
    # device = torch.device("cuda:0"),
    precision=torch.half,
)
model.eval()


def pixel_to_camera_coords(coords, depths, f_px, cx, cy):
    coords = np.array(coords)
    X = (coords[:, 0] - cx) * depths / f_px
    Y = (coords[:, 1] - cy) * depths / f_px
    Z = depths
    return np.stack((X, Y, Z), axis=1)

def get_depth_focallength(image_path):
    ori_image = Image.open(image_path).convert("RGB")
    image_w, image_h = ori_image.width, ori_image.height
    cx, cy = image_w / 2, image_h / 2


    image, _, f_px = depth_pro.load_rgb(image_path)
    image = transform(image)

    # image = image.to('cuda:0')



    prediction = model.infer(image, f_px=f_px)


    depth = prediction["depth"].detach().cpu().numpy().squeeze()  # Depth in [m].
    # f_px = ["focallength_px"].detach().cpu().item()  # Focal length in pixels.

    f_px = prediction["focallength_px"]  # Focal length in pixels.

    return depth, f_px, cx, cy

def polygon_area_3d(vertices):
    if len(vertices) < 3:
        return 0.0
    v0 = np.array(vertices[0])
    area_vector = np.zeros(3)
    for i in range(1, len(vertices) - 1):
        vi = np.array(vertices[i]) - v0
        vi1 = np.array(vertices[i + 1]) - v0
        area_vector += np.cross(vi, vi1)
    return 0.5 * np.linalg.norm(area_vector)

def scaled_polygon_area(vertices, scale):
    original_area = polygon_area_3d(vertices)
    return (scale ** 2) * original_area

def estimate_target_object_size(
    depth,f_px,cx,cy,
    coords_refobj,
    coords_targetobjs,
    ref_obj_w_cm,
    ref_obj_h_cm
):
    """
    Estimate the size of the target object in the image.
    Args:
        image_path (str): Path to the image file.
        coords_refobj (list or np.ndarray): 4x2 array of reference object corner coordinates (pixels).
        coords_targetobj json (list or np.ndarray): 4x2 array of target object corner coordinates (pixels).
        ref_obj_w_cm (float): Real-world width of the reference object (cm).
        ref_obj_h_cm (float): Real-world height of the reference object (cm).
    Returns:
        (pad_width_cm, pad_height_cm): Estimated width and height of the target object (cm).
    """


    # depth, f_px, cx, cy=get_depth_focallength(image_path)

    # print(depth.shape)
    # print(f_px)

    # import time 
    # start_time = time.time()

    coords_refobj = np.array(coords_refobj, dtype=np.uint64)
    depth_refobj = depth[coords_refobj[:, 1], coords_refobj[:, 0]]  # TL, TR, BR, BL
    

    xyz_refobj = pixel_to_camera_coords(coords_refobj, depth_refobj, f_px, cx, cy)
    

    # 3D diagonal of the reference object and known real-world diagonal
    diag_refobj_real_cm = np.sqrt(ref_obj_w_cm**2 + ref_obj_h_cm**2)

    diag_refobj_3D = (np.linalg.norm(xyz_refobj[0] - xyz_refobj[2]) + np.linalg.norm(xyz_refobj[1] - xyz_refobj[3]))/2
    

    # Scaling factor: real-world cm per meter of 3D distance
    scale = diag_refobj_real_cm / diag_refobj_3D

    output_json={}
    for m_id,coords_targetobj in coords_targetobjs.items():
        output_json[m_id]={}
        coords_targetobj = np.array(coords_targetobj, dtype=np.uint64)
        # Depth at each corner point (in meters)
        depth_targetobj = depth[coords_targetobj[:, 1], coords_targetobj[:, 0]]
        xyz_targetobj = pixel_to_camera_coords(coords_targetobj, depth_targetobj, f_px, cx, cy)
        # Target object dimensions in 3D space
        
        if len(xyz_targetobj)==2:
            length = np.linalg.norm(xyz_targetobj[0]-xyz_targetobj[1])*scale
            output_json[m_id]['type']="line"
            output_json[m_id]['length']=length
            output_json[m_id]['width_top']=length
            output_json[m_id]['width_bottom']=length
            output_json[m_id]['height_left']=length
            output_json[m_id]['height_right']=length




        else:
            target_area = scaled_polygon_area(xyz_targetobj, scale)
            xyz_targetobj_loop = np.concatenate((xyz_targetobj[1:], xyz_targetobj[:1]), axis=0)

            target_size = [np.linalg.norm(p0 - p1)*scale for p0, p1 in zip(xyz_targetobj, xyz_targetobj_loop)]


            output_json[m_id]['type']="polygon"
            output_json[m_id]['width_top']=target_size[0]
            output_json[m_id]['width_bottom']=target_size[2]
            output_json[m_id]['height_left']=target_size[3]
            output_json[m_id]['height_right']=target_size[1]
            output_json[m_id]['area']=target_area

    return output_json


# if __name__ == "__main__":


#     depth = np.load('depth_folder/BZtgkqM7yoEUALaBCwMsw6im_1421.498291015625_306.0_181.5_.npy')

#     f_px,cx,cy=('depth_folder/BZtgkqM7yoEUALaBCwMsw6im_1421.498291015625_306.0_181.5_.npy').split('_')[-4:-1]

#     f_px=float(f_px)
#     cx=float(cx)
#     cy=float(cy)
#     ref_obj_w_m=10.0
#     ref_obj_h_m=5.0
#     coords_refobj=[[10, 10], [110, 10], [110, 60], [10, 60]]
#     coords_targetobj={'1234':[[200, 100], [300, 100],[300, 200],[200, 200]]}
#     width_m, height_m = estimate_target_object_size(
#     depth,f_px,cx,cy,
#     np.array(coords_refobj),
#     coords_targetobj,
#     ref_obj_w_m,
#     ref_obj_h_m
# )