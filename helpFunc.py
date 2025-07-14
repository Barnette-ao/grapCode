import postRequest
import json
from datetime import datetime


def build_query_params(sort_id, extra_params=None):
        """构建资源查询参数"""
        params = {
            'sort_id': sort_id,
            'page': 1,
            'limit': 9999,
            'type': 0,
            'plat_form': "mp-weixin"
        }
        if extra_params:
            params.update(extra_params)
        return params


def get_resource_list(postUrl, queryData):
    response = postRequest.postRequest(postUrl, queryData)
    if response['code'] == 200:
        # print("请求成功！")
        # print(json.dumps(response['data']['list'], indent=4, ensure_ascii=False))
        if len(response['data']['list']) > 0:
            return response['data']['list']


def datetime_to_timestamp(date_str):
    """将日期字符串,例如2025-06-23 16:47:54转换为时间戳"""
    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    return int(dt.timestamp())

def compare_timestamps(ts1, ts2):
    """比较两个时间戳"""
    if ts1 < ts2: return -1   # ts1 更早
    elif ts1 > ts2: return 1 # ts1 更晚
    else: return 0            # 相同