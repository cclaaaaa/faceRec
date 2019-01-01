import requests
from json import JSONDecoder
import  cv2

# https://console.faceplusplus.com.cn/documents/4888381

http_urls=["https://api-cn.faceplusplus.com/facepp/v3/faceset/create","https://api-cn.faceplusplus.com/facepp/v3/detect",
"https://api-cn.faceplusplus.com/facepp/v3/faceset/addface","https://api-cn.faceplusplus.com/facepp/v3/search"];
key = "atJbXy90W7ChxK1P0vOLcz4Qq6Q5PkDs"
secret = "GLWNjjnVyUTiWUysugalf-kjRdcfiTZU"

data_create = {"api_key": key, "api_secret": secret, "return_landmark": "1"}
response = requests.post(http_urls[0], data=data_create)

req_con = response.content.decode('utf-8')
req_dict = JSONDecoder().decode(req_con)

faceset_token = req_dict["faceset_token"];
print(faceset_token)