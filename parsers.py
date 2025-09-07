from bs4 import BeautifulSoup,Tag
import re
from typing import List, Dict, Optional, Any

class HtmlParser:
    """HTML解析器"""
    def extract_keyword_match_number_bs4(self, html: str) -> int:
        """
        获取文件名在公文网的搜索框中的匹配个数

        用BeautifulSoup提取最大页码
        :param html: 网页源码
        :param default: 默认值
        :return: 关键词匹配数
        """
        soup = BeautifulSoup(html, 'html.parser')
        search_bar_box = soup.find('div', class_='so_bar')
        
        if not isinstance(search_bar_box, Tag):
            return -1

        # 2. 提取b标签的内容
        for b in search_bar_box.find_all('b'):
            match_number = b.get_text(strip=True)
        
        # 数字可能是4,626，所以需要将逗号替换为空字符串的方式去掉，然后转换为int类型    
        return int(match_number.replace(",", ""))

    def extract_page_number(self, html: str, default: int = 1) -> int:
        """提取最大页码"""
        if not html:
            return default
            
        soup = BeautifulSoup(html, 'html.parser')
        page_box = soup.find('div', class_='page')
        
        if not isinstance(page_box, Tag):
            return default
        # 有多页就有多页的<a href=XXX?&page = 1/2...
        # 将这些页码搜集起来，然后找出其中最大值，即最大页码 
        page_numbers = []
        for a in page_box.find_all('a', attrs={"href": True}):
            a_tag = a if isinstance(a, Tag) else None

            href = str(a_tag.get('href') or '') if a_tag else ''
            
            match = re.search(r'[?&]page=(\d+)', href)
            if match:
                page_numbers.append(int(match.group(1)))
        
        return max(page_numbers) if page_numbers else default
    
    def extract_article_links(self, html: str, date: str) -> List[Dict[str, str]]:
        """提取文章链接"""
        if not html:
            return []
            
        # 提取所有链接
        links = self._extract_unique_links(html)
        
        # 过滤出指定日期的链接
        filtered_links = [
            link for link in links 
            if str(link.get('title', '')).startswith(date)
        ]
        
        return filtered_links

    def _extract_unique_links(self, html:str) :
        links = self._extract_links(html)
        return self._remove_duplicate_links_of(links)

    def _remove_duplicate_links_of(self,links):
        """去重链接列表（基于title和href）"""
        seen = set()
        unique_links = []
        for item in links:
            # 用元组 (title, href) 作为去重键
            key = (item["title"].strip(), item["href"].strip())  # 去除首尾空格
            if key not in seen:
                seen.add(key)
                unique_links.append({"title": item["title"], "href": item["href"]})
        return unique_links

    def _extract_links(self, html: str) -> List[Dict[str, str]]:
        """提取所有链接"""
        soup = BeautifulSoup(html, 'html.parser')
        all_a_tag = soup.find_all("a", attrs={"title": True, "href": True})

        return [
            {
                "title": str(a.get("title") or ""),
                "href": str(a.get("href") or "")
            }
            for a in all_a_tag if isinstance(a, Tag)
        ]

    def is_doc(self, title: str) -> bool:
        """检查标题是否为文档类型"""
        # 实现文档类型检查逻辑
        return not "ppt" in title.lower()
    
    def get_article_title(self, article_title: str) -> str:
        """
        提取doc类的文章标题：
        """
        # 提取原始标题,doc标题
        pattern = r"\d+：(.+)"  # \d+ 匹配数字，：匹配冒号，(.*) 匹配内容
    
        match = re.search(pattern, article_title)
        # 去掉标题中的【团队精品】的字样
        if match:
            raw_title = match.group(1)
            doc_title = re.sub(r'^【[^】]*】\s*', '', raw_title)
            return f"{doc_title.strip()}"
        else:
            return ''

    def extract_exception_text(self, html: str) -> str:
        """提取所有文本内容"""
        soup = BeautifulSoup(html, 'html.parser')
        text =  soup.get_text(" ", strip=True)

        if text and "访问过于频繁" in text:
            return "访问过于频繁"
        elif text and "访问量用完" in text:
            return "访问量用完"
        
        return "" # 如果没有异常情况的关键字，返回空字符串
        

    def extract_article_content(self, html: str) -> Optional[List[Dict[str, str]]]:
        """提取文章内容"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            content_div = soup.find('div', class_='content-box')
            
            if not isinstance(content_div, Tag):
                return None
    
            paragraphs = content_div.find_all('p')
            
            if not paragraphs:
                return None

            p_tags = [
                {
                    "text": p.get_text(strip=True),  # 提取纯文本并去除首尾空格
                    "attrs": dict(p.attrs)  # 获取所有属性转为字典
                }
                for p in paragraphs
                if isinstance(p, Tag)
            ]    

            return [
                item 
                for item in p_tags 
                if item['text'].strip()
            ] # 过滤掉text为空字符串的字典元素
            
        except Exception as e:
            print(f"解析失败: {str(e)}")
            return None


    
            
    
