import requests

def simple_get_request(url):
    try:
        # 发起 GET 请求
        response = requests.get(url, timeout=5)
        
        # 检查响应状态码
        if response.status_code == 200:
            print("请求成功！")
            print(f"响应内容:\n{response.json()}")
        else:
            print(f"请求失败，状态码: {response.status_code}")
    
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {e}")

# 测试调用
simple_get_request("https://ht.axuex.top/api/Resource/resourcesort?from_id=&plat_form=mp-weixin&limit=0&sort_id=311")