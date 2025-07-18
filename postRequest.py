import requests
import json
import helpFunc
import os
import simple_download_pdf


# 目标 URL

def postRequest(postUrl, queryData): 
    try:
        # 发送 POST 请求（JSON 数据）
        response = requests.post(postUrl, json=queryData)
        
        if response.status_code == 200:  # 201 表示创建成功
            # print("POST 请求成功！")
            return response.json()
        else:
            print(f"POST 请求失败，状态码：{response.status_code}")

    except Exception as e:
        print("发生错误：", e)


def postRequest_with_cookie(postUrl,cookie_value, queryData):
    try:
        # 设置请求头（包含Cookie）
        headers = {
            "Cookie": cookie_value,  # 直接设置Cookie字符串
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "Accept": "application/json"  # 明确要求JSON
        }

        # 发送 POST 请求（JSON 数据）
        response = requests.post(postUrl, headers=headers, json=queryData)
        
        if response.status_code == 200:  # 201 表示创建成功
            # print("POST 请求成功！")
            return response.json()
        else:
            print(f"POST 请求失败，状态码：{response.status_code}")

    except Exception as e:
        print("发生错误：", e)


def test_postRequest():
    BASE_URL = "https://www.gwsxwk.cn"
    postUrl = f"{BASE_URL}/index/article/download.html"
    queryData = {
        "detail_id" : "183755" 
    }
    resource_list = postRequest(postUrl, queryData)
    print("请求成功",json.dumps(resource_list, indent=4, ensure_ascii=False))

def test_download_single_pdf():
    API_URL_RESOURCE_ITEM = "https://ht.axuex.top/api/Resource/resdetail?from_id="
    queryData = {"id":"2124","token":"386c0d996d9bee266b55f4aa938e374d","plat_form":"mp-weixin"}
    response = requests.post(API_URL_RESOURCE_ITEM, json=queryData)
    print("请求成功",json.dumps(response.json(), indent=4, ensure_ascii=False))
    response = response.json()
    url = response['data']['link']
    file_ext = os.path.splitext(url)[1]
    filename = f"{response['data']['title']}{file_ext}"
    print(filename)

    params = {
        "base_dir": "先锋学霸资料",
        "firstcategory": "一年级下",
        "secondcategory": "数学",
        "filename": filename,
        "thirdcategory": ""
    }
    
        
    # 构建路径
    save_path = simple_download_pdf.build_save_path(**params)
    simple_download_pdf.simple_download_pdf(url, save_path)




if __name__ == "__main__":
   print(is_exist_in_gongwenwang(
    cookie_value = "Hm_lvt_1f013c54a127ce2677327e03b2f2dcaf=1752462376; gws_keeplogin=CQ4EBAxXCQBKAwwBAxcMAQlJAwUACQUFSQQCAAYFAwIADQBJBVBXBAtUDAYFAgdQUgwEUlMHVFdaUFZRAF0HAFFRBAwTCg___c___c; PHPSESSID=v966cok4relipmqlo5kc2j5mls; breadcrumb_0=; menu_0=[{%22title%22:%22%E6%96%87%E7%AB%A0%E7%AE%A1%E7%90%86%22%2C%22url%22:%22https://wx.06179.com/article/article/init.html%22%2C%22fullurl%22:%22https://wx.06179.com/article/article/init.html%22}]"
   ,queryData = { "sort": "", "order": "", "limit": 20, "page": 1, "title": "在单身青年联谊会上的致辞：以爱搭桥促良缘，携手同行谱新篇"}
   ))
    

