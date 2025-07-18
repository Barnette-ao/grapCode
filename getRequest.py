import requests
from selenium import webdriver

def simple_get_request(url):
    try:
        # 发起 GET 请求
        response = requests.get(url, timeout=5)
        
        # 检查响应状态码
        if response.status_code == 200:
            # print("请求成功！")
            print(f"响应内容:\n{response.json()}")
        else:
            print(f"请求失败，状态码: {response.status_code}")
    
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {e}")



def simple_get_request_with_cookie(url, cookie_value):
    try:
        # 设置请求头（包含Cookie）
        headers = {
            "Cookie": cookie_value,  # 直接设置Cookie字符串
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "Accept": "application/json"  # 明确要求JSON
        }
        
        # 发起带Cookie的GET请求
        response = requests.get(
            url,
            headers=headers,  # 传入自定义请求头
            timeout=5
        )
        
        # 检查响应状态码
        if response.status_code == 200:
           print("请求成功！")  
        #    print(f"原始响应:\n{response.text}")  # 打印前500字符
           if(response.text): 
             return response.text
           else:
             return ""
        else:
            print(f"请求失败，状态码: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"请求异常: {e}")


def get_cookie_string(date):
    target_url = f"https://www.gwsxwk.cn/index/search/index.html?keyword={date}&search_type=10"
    driver = webdriver.Chrome()
    driver.get(target_url)
    
    # 获取所有 Cookie 字典
    cookies = driver.get_cookies()
    driver.quit()
    
    # 转换为 key=value 字符串
    cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
    return cookie_str




if __name__ == "__main__":
    # 目标URL（包含参数）
    target_url = "https://www.gwsxwk.cn/index/search/index.html?keyword=20250714&search_type=10"
    
    cookie_string = get_cookie_string(target_url)
    print("Cookie 字符串:", cookie_string)

    




    