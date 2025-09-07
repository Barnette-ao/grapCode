from typing import List, Dict, Optional, Any
import os
import time
import pydash as _
from logger import log_exit_time_with_date

from http_client import HttpClient
from parsers import HtmlParser
from cache import CacheManager
from file import FileManager
from exceptions import AccessLimitError

LOG_FILE="program_interrupt_web.log"

class GWSXWK_ArticleDownloader:
    """
    思享公文文章下载器核心类
    """
    def __init__(self, gwsxwk_cookie: str, gongwen_cookie: str):
        self.base_url = "https://www.gwsxwk.cn"
        self.http_client = HttpClient(gwsxwk_cookie, gongwen_cookie)
        self.html_parser = HtmlParser()
        self.cache_manager = CacheManager()
        self.file_manager = FileManager()
    
    def get_html_text(self, date: str, page: int) -> Optional[str]:
        """获取HTML文本"""
        target_url = f"{self.base_url}/index/search/index.html?keyword={date}&search_type=10&page={page}"
        return self.http_client.get_with_gwsxwk_cookie(target_url)

    def get_article_links(self, date: str) -> Optional[List[Dict[str, str]]]:
        """获取某一日所有的文章链接"""
        # 尝试从缓存获取
        cached_links = self.cache_manager.load_article_links_by(date)
        if cached_links:
            return cached_links
            
        # 缓存中不存在，从网站获取
        all_article_links = self._fetch_all_article_links(date)
        if all_article_links:
            self.cache_manager.save_all_article_links(all_article_links, date)
        return all_article_links

    def _fetch_all_article_links(self, date: str) -> Optional[List[Dict[str, str]]]:
        """从网站获取所有文章链接"""
        all_article_links = []
        
        # 获取第一页
        html_text = self.get_html_text(date, 1)
        if not html_text:
            print(f"[ERROR] 无法获取页面内容: {date}")
            return None
        
        # 解析最大页数
        max_page = self.html_parser.extract_page_number(html_text)
        
        # 获取第一页的文章链接
        page_links = self.html_parser.extract_article_links(html_text, date)
        # 安全扩展列表，自动过滤空值和非可迭代对象
        if page_links and isinstance(page_links, (list, tuple, set, frozenset)):
            all_article_links.extend(page_links)
        
        # 获取剩余页面的链接
        if max_page and max_page > 1:
            for page in range(2, max_page + 1):
                html_text = self.get_html_text(date, page)
                if not html_text:
                    print(f"[ERROR] 无法获取页面内容: {date} - 第{page}页")
                    return None
                
                page_links = self.html_parser.extract_article_links(html_text, date)
                if page_links and isinstance(page_links, (list, tuple, set, frozenset)):
                    all_article_links.extend(page_links)
        
        return all_article_links

    def download_article(self, article_link: Dict[str, str], date: str) -> bool:
        """下载单篇文章"""
        # 检查是否需要下载
        if self._should_skip_download(article_link, date):
            return False
        
        # 获取文章内容
        article_url = f"{self.base_url}{article_link['href']}"
        article_html_text = self.http_client.get_with_gwsxwk_cookie(article_url)
        print("article_html_text",article_html_text)

        if not article_html_text:
            print(f"[ERROR] 无法获取文章内容: {article_url}")
            return False
        
        # 获取所有html中可能存在的异常情况的文本
        text = self.html_parser.extract_exception_text(article_html_text)
        # 检查是否触发限流
        if text in ["访问过于频繁","访问量用完"]:
            print(f"[ERROR] {text}: {article_url}")
            raise AccessLimitError(text)
        
        # 解析文章内容
        text_objects = self.html_parser.extract_article_content(article_html_text)
        print("text_objects",text_objects)

        if not text_objects:
            print(f"[ERROR] 无法解析文章内容: {article_url}")
            return False
        
        # 保存文章
        return self.file_manager.save_article(date, text_objects)
    
    def _should_skip_download(self, article_link: Dict[str, str], date: str) -> bool:
        """检查是否应该跳过下载"""
        # 检查是否为文档类型
        if not self.html_parser.is_doc(article_link['title']):
            print(f"文件不是doc类型，不允许下载: {article_link['title']}")
            return True
        
        # 获取文章标题
        title = self.html_parser.get_article_title(article_link['title'])
        if not title:
            print(f"[ERROR] 无法解析文章标题: {article_link['title']}")
            return True
        
        # 检查文件是否已存在
        filepath = f"{date}/{title}.docx"
        if os.path.exists(filepath):
            print(f"文件已下载，且不允许覆盖: {filepath}")
            return True
        
        # 检查是否已上传到公文网
        if self.http_client.is_exist_in_gongwenwang(title):
            print(f"文件已上传，且不允许覆盖: {title}")
            return True
        
        return False
    
    @log_exit_time_with_date(LOG_FILE)
    def download_articles_by_date(self, date: str) -> bool:
        """下载指定日期的所有文章"""
        article_links = self.get_article_links(date)
        # print("article_links",article_links)

        if not article_links:
            print(f"[ERROR] 没有文章链接: {date}")
            return False
        
        try:
            for article_link in article_links:
                # print("article_link",article_link)
                self.download_article(article_link, date)
            
            # 清除缓存
            self.cache_manager.remove_date_from_cache(date)
            return True
            
        except AccessLimitError as e:
            print(f"[ERROR] 下载 {date} 的文件时触发限流: {str(e)}")
            # 保存剩余未下载的链接
            current_index = _.find_index(article_links, article_link)
            remaining_links = article_links[current_index:]
            self.cache_manager.save_all_article_links(remaining_links, date)

            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(f"[ERROR: {e}] 下载 {date} 的文件时触发限流\n")
            raise # 继续向上传播

    def batch_download(self) -> bool:
        """批量下载指定日期范围的文章"""
        # 如果未指定日期范围，则使用阈值时间和当前日期
        from time_extractor import GwsxwkTimeExtractor
        extractor = GwsxwkTimeExtractor(log_file=LOG_FILE)
        start_date = extractor.get_threshold_time()
        end_date = extractor.get_date_of_today()
            
        
        from helpFunc import generate_date_range
        dates = generate_date_range(start_date, end_date)
        if not dates:
            print("没有需要下载的日期")
            return False
        
        while True:
            try:
                for date in dates:
                    print(f"----{date}-----")
                    self.download_articles_by_date(date)
                
                return True  # 全部日期正常下载完成
                
            except AccessLimitError as e:
                reason = str(e)
                if reason == "访问过于频繁":
                    print(f"[ERROR] 触发接口限流:暂停20分钟")
                    time.sleep(20 * 60)  # 等待20分钟后重试
                elif reason == "访问量用完":
                    print(f"[ERROR] 访问量用完:暂停执行")
                
                return False    

if __name__ == "__main__":
    gongwen_cookie = "PHPSESSID=men3bi6ie175dqrvuqb53gt0fl; Hm_lvt_1f013c54a127ce2677327e03b2f2dcaf=1756777162,1756866814,1757208926; HMACCOUNT=C8B0C3D372758140; gws_keeplogin=BwEEAlQABgxKAwwBAxcMAQlJAwUACQUFSQQCAAINBAMFBgxJVAJTAw4FDVAGUVQACQVRAgdXVAYKBQIFAlxUB1AMUFMTCg___c___c; gws_search_history=U10CVAcFBARYAwgPQlwPBQpGDwQBCxfSjrHSjrLSoarXgY7Ria4TDkQ___c; Hm_lpvt_1f013c54a127ce2677327e03b2f2dcaf=1757213036"
    gwsxwk_cookie = "PHPSESSID=utc3818fj1lq8ikp3kj0aqrakk; Hm_lvt_4e353b346bb9049b942dfe452e3934f8=1756777343,1756816173,1757208831; HMACCOUNT=C8B0C3D372758140; Hm_lvt_17a6d79f196bd7dceed5aefb62507766=1756777343,1756816173,1757208831; Hm_lpvt_17a6d79f196bd7dceed5aefb62507766=1757213122; Hm_lpvt_4e353b346bb9049b942dfe452e3934f8=1757213122"
    article_link = {
      "title": "2025090702：【团队精品】XX市XX航空分公司深入贯彻中央八项规定精神学习教育总结报告",
      "href": "/index/article/detail/detail_id/189004.html"
    }
    date = "20250907"
    download = GWSXWK_ArticleDownloader(gwsxwk_cookie, gongwen_cookie)
    download.download_article(article_link,date)
