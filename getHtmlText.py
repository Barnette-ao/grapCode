import keyword
from getRequest import simple_get_request_with_cookie
from helpFunc import (
    isDoc,
    extract_page_number_bs4,
    process_html_to_links,
    extract_p_bs4,
    get_article_title,
    generate_date_range,
    extract_keyword_match_number_bs4,
    save_all_article_links,
    load_article_links_by,
    remove_date_from_cache,
)
from getThresholdTime import GwsxwkTimeExtractor
from logger import log_exit_time_with_date

import saveToWord
import os
import argparse  

from urllib.parse import quote
import pydash as _ 
import time

BASE_URL = "https://www.gwsxwk.cn"

LOG_FILE="program_interrupt_web.log"

def get_html_text(date, cookie_str, page):
    """
    获取HTML文本
    """
    target_url = f"https://www.gwsxwk.cn/index/search/index.html?keyword={date}&search_type=10&page={page}"

    html_text = simple_get_request_with_cookie(target_url, cookie_str)
    # print("html_text",html_text)
    return html_text


def get_max_page(html_text):
    """
    获取最大页数
    """
    if(html_text):
        max_page = extract_page_number_bs4(html_text)
        return max_page


def parse_article_links(html_text, date):
    """
    从HTML文本中解析文章链接
    """ 
    if(html_text):
        unique_links = process_html_to_links(html_text)
       
        filtered_unique_links = list(
            filter(
                lambda x: str(x.get('title', '')).startswith(date),
                unique_links
            )
        )
       
        return filtered_unique_links


def get_all_article_links(date, cookie_str):
    """
    获取某一日所有的文章链接
    """
    def safe_extend(target_list, source_items):
        """安全扩展列表，自动过滤空值和非可迭代对象"""
        if source_items and isinstance(source_items, (list, tuple, set, frozenset)):
            target_list.extend(source_items)

    all_article_links = []

    # 1.首先访问第一页的文章情况
    html_text = get_html_text(date, cookie_str, 1)

    if not html_text:
        print(f"[ERROR] 无法获取页面内容: {date} - {cookie_str}")
        return None
    
    # 2. 提取最大页数
    max_page = get_max_page(html_text)
    print("max_page",max_page)
    
    article_links_by_page = parse_article_links(html_text, date)
    # 3. 获取第一页的文章链接文章链接,并安全加入all_article_links
    safe_extend(all_article_links, article_links_by_page)

    # 4. page > 1 的情况,分别遍历每一页，找到每一页的文章链接并安全加入all_article_links
    if max_page > 1:
        for page in range(2, max_page + 1):
            html_text = get_html_text(date, cookie_str, page)
            if not html_text:
                print(f"[ERROR] 无法获取页面内容: {date} - {cookie_str}")
                return None

            safe_extend(all_article_links, parse_article_links(html_text,date))

    return all_article_links



def get_article_link(href):
    """
    获取文章链接
    """
    return f"{BASE_URL}{href}"
    

# 访问链接1次
def request_article_html(article_link, cookie_str):
    """
    下载文章内容
    Args:
        article_link: 文章URL
        cookie_str: 认证Cookie
        
    Returns:
        str: 成功时返回特定文章的Html文本内容，失败时返回None
    """
    # 1. 获取文章的HTML链接
    article_link_href = f"{BASE_URL}{article_link['href']}"

    # 2. 获取文章的HTML内容
    html_text = simple_get_request_with_cookie(article_link_href, cookie_str)
    if not html_text:
        print(f"[ERROR] 无法获取文章内容: {article_link_href}")
        return None

    # 3. 解析文章的文本对象
    try:
        return extract_p_bs4(html_text)
    except Exception as e:
        print(f"[ERROR] 解析失败: {str(e)}")
        return None



def download_article_content(date, text_objects):
    # 4. 保存文件
    output_path = f"{date}/{text_objects[0]['text']}.docx"  # 使用第二段作为文件名
    # print("output_path",output_path)
    try:
        saveToWord.save_to_word(text_objects, output_path)
        return output_path
    except Exception as e:
        print(f"[ERROR] 文件保存失败: {str(e)}")
        return None

def is_exist_in_gongwenwang(keyword, gongwen_cookie_value):
    """
    检查文章是否已存在于公网网
    """
    # 1. 构建请求参数，将关键词进行URL编码
    print("keyword",keyword)
    q_param = quote(keyword)

    response = simple_get_request_with_cookie(
        url= f"https://wx.06179.com/doc/search.html?q={q_param}",
        cookie_value = gongwen_cookie_value, 
    )

    # print("response",response)
    return extract_keyword_match_number_bs4(response) > 0



def is_not_need_download(article_link, date, gongwen_cookie):
    """
    检查文件是否需要下载
    """
    if not isDoc(article_link['title']):
        print(f"文件不是doc类型，不允许下载。")
        return True

    
    # get_article_title(article_link['title'])会返回不带有扩展名的文件名
    title = get_article_title(article_link['title'], False)
    # 过滤掉title是""，空字符串的情况
    if not title:
        print(f"[ERROR] 无法解析文章标题: {article_link['title']}")
        return True
    

    # get_article_title(article_link['title'])会返回带有扩展名的文件名
    filepath = f"{date}/{get_article_title(article_link['title'])}"
    if os.path.exists(filepath):
        print(f"文件已下载，且不允许覆盖。")
        return True

    elif is_exist_in_gongwenwang(
            keyword = title,
            gongwen_cookie_value = gongwen_cookie
         ):
         print(f"文件已上传，且不允许覆盖。")
         return True
    
    return False

def get_cached_article_links(date,gwsxwk_cookie_str):
    # 如果缓存中不存在该日期的article_links，则从思享公文网获取所有article_links并保存到缓存中   
    if not load_article_links_by(date):
        article_links = get_all_article_links(date, gwsxwk_cookie_str)    
        save_all_article_links(article_links, date)
    # 如果缓存中已经存在该日期的article_links，则直接读取缓存中的article_links
    else:
        article_links = load_article_links_by(date)
    
    return article_links

class AccessLimitError(Exception):
    """触发接口限流时抛出"""
    pass

def download_article_by_link(article_links, article_link,gwsxwk_cookie_str,date):
    # 4. 请求文章html内容
    text_objects = request_article_html(article_link, gwsxwk_cookie_str)
    # text_objects = "访问过于频繁"

    # 5. 如果text_objects访问过于频繁
    if text_objects in ["访问过于频繁","访问量用完"]:
        print(f"[ERROR] {text_objects}: {BASE_URL}{article_link['href']}")
        
        # 查找当前article_link在article_links中的索引
        index = _.find_index(article_links, article_link)
        # 从article_links中删除当前article_link之前的所有元素
        article_links = article_links[index:]
        save_all_article_links(article_links, date)          
        # 抛异常让外层捕获
        raise AccessLimitError(text_objects)

    # 6. 下载文章内容
    download_article_content(date, text_objects)


@log_exit_time_with_date(LOG_FILE)
def download_article_by_date(gwsxwk_cookie_str, date, gongwen_cookie):
    article_links = get_cached_article_links(date,gwsxwk_cookie_str)

    print("article_links",article_links)

    try:
        # 3. 遍历该date下每一篇文章链接字典元素
        for article_link in article_links:
            # 检查文件是否需要下载
            if is_not_need_download(article_link, date, gongwen_cookie):
                continue
            
            download_article_by_link(article_links, article_link,gwsxwk_cookie_str,date)
    except AccessLimitError as e:
        # 立即记录
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"[ERROR: {e}] 下载 {date} 的文件时触发限流\n")
        raise # 继续向上抛出
    
    # 7. 清空date这一日的缓存
    remove_date_from_cache(date)

    
def batched_download_article_by_date():
    parser = argparse.ArgumentParser(description="批量下载DOCX资源")
    parser.add_argument("--gwsxwk_cookie",required=True, type=str, help="思享公文认证Cookie")
    parser.add_argument("--gongwen_cookie",required=True, type=str, help="公文网认证Cookie")
    
    args = parser.parse_args()
    while True:
        try:
            gwsxwk_cookie = args.gwsxwk_cookie
            gongwen_cookie = args.gongwen_cookie

            # 1. 获取开始日期和结束日期
            gwsxwk_extractor = GwsxwkTimeExtractor(log_file=LOG_FILE)
            start_date = gwsxwk_extractor.get_threshold_time()
            end_date = gwsxwk_extractor.get_date_of_today()
            print("start_date",start_date)
            print("end_date",end_date)

            dates = generate_date_range(start_date, end_date)
            if not dates:
                print("没有需要下载的日期")
                exit()

            for date in dates:
                print(f"----{date}-----")
                download_article_by_date(gwsxwk_cookie, date, gongwen_cookie)

            break; # 全部日期正常下载完
        except AccessLimitError as e:
            reason = str(e)
            if reason == "访问过于频繁":
                print(f"[ERROR] 触发接口限流:暂停20分钟")
                time.sleep(20 * 60)  # 等待20 * 60秒后重试
            elif reason == "访问量用完":
                print(f"[ERROR] 访问量用完:暂停执行")
                break

if __name__ == "__main__":
    # date = "20250826"
    
    gongwen_cookie = "PHPSESSID=hdolnrlil5qrpvua3g5e54bger; Hm_lvt_1f013c54a127ce2677327e03b2f2dcaf=1756777162,1756866814; HMACCOUNT=C8B0C3D372758140; gws_keeplogin=UwwGUFQABlZKAwwBAxcMAQlJAwUACQUFSQQCAAIBAgQHAAVJBQwAAQEEAAJRUw0MAVcNBwMDUwUOAgFXBFsADANXA1cTCg___c___c; Hm_lpvt_1f013c54a127ce2677327e03b2f2dcaf=1756866853"
    gwsxwk_cookie_str ="Hm_lvt_17a6d79f196bd7dceed5aefb62507766=1756777343,1756816173; HMACCOUNT=C8B0C3D372758140; Hm_lvt_4e353b346bb9049b942dfe452e3934f8=1756777343,1756816173; PHPSESSID=l3qg0eejibhjja1kq2cuvi61ns; Hm_lpvt_4e353b346bb9049b942dfe452e3934f8=1756866784; Hm_lpvt_17a6d79f196bd7dceed5aefb62507766=1756866784"

    batched_download_article_by_date()

    # article_links = get_cached_article_links(date,gwsxwk_cookie_str)
    # print("article_links",article_links)
    # article_link = {
    #   "title": "2025082620：【团队精品】个人近两年思想工作总结",
    #   "href": "/index/article/detail/detail_id/187906.html"
    # }
    # download_article_by_link(article_links, article_link,gwsxwk_cookie_str,date)


    

