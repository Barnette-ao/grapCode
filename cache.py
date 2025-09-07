import json
import os
from typing import List, Dict, Optional, Any

class CacheManager:
    """
    缓存管理器类
    """
    def __init__(self, cache_file: str = "article_href_cache.json"):
        self.cache_file = cache_file
    
    def load_article_links_by(self, date: str) -> Optional[List[Dict[str, str]]]:
        """从缓存加载指定日期的文章链接"""
        try:
            if not os.path.exists(self.cache_file):
                return None
                
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
                
            return cache_data.get(date)
            
        except Exception as e:
            print(f"加载缓存失败: {str(e)}")
            return None
    
    def save_all_article_links(self, article_links: List[Dict[str, str]], date: str) -> bool:
        """保存触发空数组的参数,格式如下：
        {
            "20230101": [{'title':'sada', 'href':'/index1.html'}, {'title':'sada', 'href':'/index2.html'}],
            "20230102": [{'title':'sada', 'href':'/index3.html'}],
            "20230103": [{'title':'sada', 'href':'/index4.html'}]
        }
        """
        try:
            cache_data = {}
            
            # 如果缓存文件存在，先读取现有数据
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
            
            # 更新缓存数据
            cache_data[date] = article_links
            
            # 写入缓存文件
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
                
            return True
            
        except Exception as e:
            print(f"保存缓存失败: {str(e)}")
            return False
    
    def remove_date_from_cache(self, date: str) -> bool:
        """从缓存中移除指定日期的数据"""
        try:
            if not os.path.exists(self.cache_file):
                return True
                
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            if date in cache_data:
                del cache_data[date]
                
                with open(self.cache_file, 'w', encoding='utf-8') as f:
                    json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            print(f"移除缓存失败: {str(e)}")
            return False
