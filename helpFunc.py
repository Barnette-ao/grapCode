import postRequest
import json
from bs4 import BeautifulSoup
import re
import os
from datetime import datetime, timedelta



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
    if not response:
        print("请求失败！")
        return None
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

def extract_keyword_match_number_bs4(html: str) -> int:
    """
    用BeautifulSoup提取最大页码
    :param html: 网页源码
    :param default: 默认值
    :return: 关键词匹配数
    """
    soup = BeautifulSoup(html, 'html.parser')
    search_bar_box = soup.find('div', class_='so_bar')
    if not search_bar_box:
        print("未找到搜索结果")
        print("html",html)
        

    # 2. 提取b标签的内容
    for b in search_bar_box.find_all('b'):
        # print(b)
        match_number = b.get_text(strip=True)
    # 数字可能是4,626，所以需要将逗号替换为空字符串的方式去掉，然后转换为int类型    
    return int(match_number.replace(",", ""))

def extract_page_number_bs4(html: str, default: int = 1) -> int:
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
    """用BeautifulSoup提取所有p类文本和图片"""
    soup = BeautifulSoup(html, 'html.parser')

    # 查找是否存在'访问过于频繁'的字符串
    text = soup.get_text(" ", strip=True)
    if '访问过于频繁' in text:
        return "访问过于频繁"

    content_box = soup.find('div', class_='content-box')
    p_tags = []
    
    if not content_box:
        return []

    for p in content_box.find_all('p'):
        p_tags.append({
            "text": p.get_text(strip=True),  # 提取纯文本并去除首尾空格
            "attrs": dict(p.attrs)  # 获取所有属性转为字典
        })
    
    return [item for item in p_tags if item['text'].strip()] # 过滤掉text为空字符串的字典元素

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


def extra_title(pattern,text):
    match = re.search(pattern, text)
    return match.group(1) if match else None

def extra_doc_title(text):
    pattern = r"\d+：(.*)"  # \d+ 匹配数字，：匹配冒号，(.*) 匹配内容
    return extra_title(pattern,text)

def isDoc(text):
    return not "ppt" in text.lower()

def get_article_title(text,isWithExt = True):
    """
    过滤不是doc的文章比如ppt或者excel,只提取doc类的文章标题：
    """
    # 确定文件扩展名
    file_ext = ".docx"
    # 提取原始标题,doc标题
    doc_title = extra_doc_title(text)
    
    # 如果isWithExt为False，不拼接扩展名，直接返回标题
    if not isWithExt:
        return f"{doc_title}"

    # 如果isWithExt为True，拼接扩展名 返回最终标题
    return f"{doc_title}{file_ext}"

def generate_date_range(start_date_str, end_date_str):
    """
    生成两个日期之间的所有日期（包含起始和结束日期）
    
    参数:
        start_date_str: 起始日期字符串 (格式: YYYYMMDD)
        end_date_str: 结束日期字符串 (格式: YYYYMMDD)
        
    返回:
        List[str]: 日期字符串列表 (格式: YYYYMMDD)
    """
    # 转换字符串为日期对象
    start_date = datetime.strptime(start_date_str, "%Y%m%d")
    end_date = datetime.strptime(end_date_str, "%Y%m%d")
    
    # 确保起始日期不大于结束日期
    if start_date > end_date:
        start_date, end_date = end_date, start_date
    
    # 计算总天数差
    delta = end_date - start_date
    date_list = []
    
    # 生成日期序列
    for i in range(delta.days + 1):
        current_date = start_date + timedelta(days=i)
        date_list.append(current_date.strftime("%Y%m%d"))
    
    return date_list



PARAMS_CACHE_FILE = "request_cache.json"
def save_failed_params(params):
    """保存触发空数组的参数"""
    with open(PARAMS_CACHE_FILE, 'w') as f:
        json.dump({
            "last_failed_params": params,
            "failure_time": datetime.now().isoformat()
        }, f)

def load_failed_params():
    """加载上次失败的参数"""
    try:
        with open(PARAMS_CACHE_FILE) as f:
            data = json.load(f)
            # 检查是否已过冷却期（10分钟）
            failure_time = datetime.fromisoformat(data["failure_time"])
            if datetime.now() - failure_time < timedelta(minutes=10):
                return data["last_failed_params"]
    except (FileNotFoundError, json.JSONDecodeError):
        return None


ARTICLE_HREF_CACHE_FILE = "article_href_cache.json"
def save_all_article_links(article_links,date):
    """保存触发空数组的参数,格式如下：
    {
        "20230101": [{'title':'sada', 'href':'/index1.html'}, {'title':'sada', 'href':'/index2.html'}],
        "20230102": [{'title':'sada', 'href':'/index3.html'}],
        "20230103": [{'title':'sada', 'href':'/index4.html'}]
    }
    """
    # 1. 读取已有数据（如果文件存在）
    existing_data = {}
    if os.path.exists(ARTICLE_HREF_CACHE_FILE):
        with open(ARTICLE_HREF_CACHE_FILE, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
    
    # 2. 更新数据（合并旧数据和新数据）
    existing_data[date] = article_links  # 按日期作为键存储
    
    # 3. 写回文件
    with open(ARTICLE_HREF_CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, indent=2, ensure_ascii=False)  # indent美化格式

def remove_date_from_cache(date):
    """从缓存文件中删除指定日期的数据
    
    参数:
        date (str): 要删除的日期，格式如 "20230101"
    """
    # 1. 检查文件是否存在
    if not os.path.exists(ARTICLE_HREF_CACHE_FILE):
        print(f"警告: 缓存文件 {ARTICLE_HREF_CACHE_FILE} 不存在")
        return
    
    # 2. 读取已有数据
    with open(ARTICLE_HREF_CACHE_FILE, 'r', encoding='utf-8') as f:
        existing_data = json.load(f)
    
    # 3. 检查要删除的日期是否存在
    if date not in existing_data:
        print(f"警告: 日期 {date} 不在缓存中")
        return
    
    # 4. 删除指定日期的数据
    del existing_data[date]
    
    # 5. 写回文件
    with open(ARTICLE_HREF_CACHE_FILE, 'w' , encoding='utf-8') as f:
        json.dump(existing_data, f, indent=2, ensure_ascii=False)

def load_article_links_by(date):
    """加载上次失败的参数"""
    try:
        with open(ARTICLE_HREF_CACHE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # 安全地取键，没有就返回 None
            return data.get(date)  
               
    except (FileNotFoundError, json.JSONDecodeError):
        return None