import requests


# # Địa chỉ API của bạn
# url = "https://aibe-measurement.motionscloud.com/estimate_depth"

# # Dữ liệu test
# payload = {
#     "uuid": "CTHgTFvrWi8RM66UwAFpJY7W/input/uwFSE9VkUaFW2BSX9DHCCmZS_front_left_view.jpg",
#     "bucket": "mc-call",
#     "callback": ""
# }

# # Gửi POST request
# response = requests.post(url, json=payload)
# # In kết quả
# if response.status_code == 200:
#     data = response.json()

#     print('9999999999999',data)
# else:
#     print(f"{response.status_code} - {response}")



# Địa chỉ API của bạn
url = "https://aibe-measurement.motionscloud.com/estimate_size"


# {
#   "uuid": "mCLQinVwxy5mGqFfwT2SNWSi",
#   "bucket": "mc-call",
#   "coords_refobj": [
#     [1747.199954553324, 484.7737183750863],
#     [2112.053140148892, 373.11758362458653],
#     [2238.6348576004157, 897.9014169519352],
#     [1858.8897052458449, 987.2263247523348]
#     ],
#    "ref_obj_w_m": 0.14,
#    "ref_obj_h_m": 0.21,
#    "coords_targetobj": {
#     "3391ae33-2fde-48fd-9603-4bcde0eeb2a4": [
#         [920.6957994286704, 853.2389630517353],
#         [1252.042059816482, 495.93933185013617],
#         [1732.3079877943212, 1005.835680544085],
#         [1363.7318105090028, 1351.969698270634]
#     ]}
# }

# # Dữ liệu test
# payload = {
#     "uuid": "mCLQinVwxy5mGqFfwT2SNWSi",
#     "bucket": "mc-call",
#     "coords_refobj": [
#         [1747, 484],
#         [2112, 373.11758362458653],
#         [2238.6348576004157, 897.9014169519352],
#         [1858.8897052458449, 987.2263247523348]
#         ],
#     "ref_obj_w_m": 0.14,
#     "ref_obj_h_m": 0.21,
#     "coords_targetobj": {
#         "3391ae33-2fde-48fd-9603-4bcde0eeb2a4": [
#             [920.6957994286704, 853.2389630517353],
#             [1252.042059816482, 495.93933185013617],
#             [1732.3079877943212, 1005.835680544085],
#             [1363.7318105090028, 1351.969698270634]
#         ]}
# }


payload={
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
        [1252.042059816482, 495.93933185013617]
    ]}
}

# payload={
#   "uuid": "CTHgTFvrWi8RM66UwAFpJY7W/input/uwFSE9VkUaFW2BSX9DHCCmZS_front_left_view.jpg",
#   "bucket": "mc-call",
#   "coords_refobj": [
#     [1747.199954553324, 484.7737183750863],
#     [2112.053140148892, 373.11758362458653],
#     [2238.6348576004157, 897.9014169519352],
#     [1858.8897052458449, 987.2263247523348]
#     ],
#    "ref_obj_w_m": 0.14,
#    "ref_obj_h_m": 0.21,
#    "coords_targetobj": {
#     "3391ae33-2fde-48fd-9603-4bcde0eeb2a4": [
#         [920.6957994286704, 853.2389630517353],
#         [1252.042059816482, 495.93933185013617]
#     ]}
# }

# Gửi POST request
response = requests.post(url, json=payload)
# In kết quả
if response.status_code == 200:
    data = response.json()
    print("✅ Kết quả:",data)
    # print(f"Chiều rộng (cm): {data['target_width_m']}")
    # print(f"Chiều cao (cm): {data['target_height_m']}")
    # print('target_area',data['target_area'])
    # print('target_size',data['target_size'])
else:
    print(f"❌ Lỗi: {response.status_code} - {response.text}")
