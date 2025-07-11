import requests


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




