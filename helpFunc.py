import postRequest
import json
from datetime import datetime
from bs4 import BeautifulSoup
import re


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


# 用bs4提取title和href
def extract_links_bs4(html):
    """用BeautifulSoup提取所有链接的title和href"""
    soup = BeautifulSoup(html, 'html.parser')
    return [
        {"title": a.get("title"), "href": a.get("href")}
        for a in soup.find_all("a", attrs={"title": True, "href": True})
    ]

def extract_page_number_bs4(html: str, default: int = 0) -> int:
    """
    用BeautifulSoup提取最大页码
    :param html: 网页源码
    :param default: 默认值
    :return: 最大页码
    """
    soup = BeautifulSoup(html, 'html.parser')
    page_box = soup.find('div', class_='page')
    
    if not page_box:
        return default

    # 2. 提取所有有效页码
    page_numbers = []
    for a in page_box.find_all('a', attrs={"href": True}):
        # 例如：href="/index/search/index.html?keyword=20250713&amp;search_type=10&amp;page=3"
        href_attr = a.get('href', '').strip()
        # 提取页码的正则表达式
        match = re.search(r'[?&]page=(\d+)', href_attr)
        
        if not match:
            continue
        
        page_numbers.append(int(match.group(1)))

    if not page_numbers:
        return default
    
    return max(page_numbers)    

def extract_p_bs4(html):
    """用BeautifulSoup提取所有p类文本"""
    soup = BeautifulSoup(html, 'html.parser')
    content_box = soup.find('div', class_='content-box')
    p_tags = []
    
    if not content_box:
        return []

    for p in content_box.find_all('p'):
        p_tags.append({
            "text": p.get_text(strip=True),  # 提取纯文本并去除首尾空格
            "attrs": dict(p.attrs)  # 获取所有属性转为字典
        })
    
    return p_tags

def get_unique_links_list(matches):
    """去重链接列表（基于title和href）"""
    seen = set()
    unique_links = []
    for item in matches:
        # 用元组 (title, href) 作为去重键
        key = (item["title"].strip(), item["href"].strip())  # 去除首尾空格
        if key not in seen:
            seen.add(key)
            unique_links.append({"title": item["title"], "href": item["href"]})
    return unique_links

def process_html_to_links(html):
    """
     完整处理流程：解析HTML → 去重链接
    """
    return get_unique_links_list(extract_links_bs4(html))
