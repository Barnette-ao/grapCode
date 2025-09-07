import requests
from urllib.parse import quote
from typing import Optional

class HttpClient:
    """HTTP请求客户端"""
    
    def __init__(self, gwsxwk_cookie: str, gongwen_cookie: str):
        self.gwsxwk_cookie = gwsxwk_cookie
        self.gongwen_cookie = gongwen_cookie
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
    
    def get_with_gwsxwk_cookie(self, url: str) -> Optional[str]:
        """使用思享公文网Cookie发送GET请求"""
        return self._get_with_cookie(url, self.gwsxwk_cookie)
    
    def get_with_gongwen_cookie(self, url: str) -> Optional[str]:
        """使用公文网Cookie发送GET请求"""
        return self._get_with_cookie(url, self.gongwen_cookie)
    
    def _get_with_cookie(self, url: str, cookie_value: str) -> Optional[str]:
        """带Cookie的GET请求"""
        try:
            headers = {
                "Cookie": cookie_value,
                "User-Agent": self.user_agent,
                "Accept": "application/json"
            }
            
            response = requests.get(
                url,
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                return response.text if response.text else ""
            else:
                print(f"请求失败，状态码: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"请求异常: {e}")
            return None
    
    def is_exist_in_gongwenwang(self, keyword: str) -> bool:
        """检查文章是否已存在于公文网"""
        q_param = quote(keyword)
        url = f"https://wx.06179.com/doc/search.html?q={q_param}"
        
        response = self.get_with_gongwen_cookie(url)
        if not response:
            return False
            
        from parsers import HtmlParser
        parser = HtmlParser()
        match_number = parser.extract_keyword_match_number_bs4(response)
        
        if match_number == -1:
            print("在对应的搜索结果的html中没有找到类名为so_bar的div")
        
        return match_number > 0 

if __name__ == "__main__":
    base_url= "https://www.gwsxwk.cn"
    date="20250904"
    gongwen_cookie = "PHPSESSID=hdolnrlil5qrpvua3g5e54bger; Hm_lvt_1f013c54a127ce2677327e03b2f2dcaf=1756777162,1756866814; HMACCOUNT=C8B0C3D372758140; gws_keeplogin=UlgJBlYAUgRKAwwBAxcMAQlJAwUACQUFSQQCAAICBgcGBQ1JBVIDBwsNXQBRDVBTUFAFAgRTV1NYVwZRBVsDAgRWAwUTCg___c___c; gws_search_history=BwwGUVAEA1NYAwoPQlwPBQpGDwQMCxfRjZ___aRj4___aQuLTUjIHTsavXt6YXAl0PBA5GCwYGChPViZ___adj4___aci6jRjZHQjIHXsaTTtobchpDRiKnTtY7TiqIWDlwPBw5HAwQEDxvSjrHTjrLWoa7SjY7Ria8XDkg___c; Hm_lpvt_1f013c54a127ce2677327e03b2f2dcaf=1757127965"
    gwsxwk_cookie = "Hm_lvt_17a6d79f196bd7dceed5aefb62507766=1756777343,1756816173; HMACCOUNT=C8B0C3D372758140; Hm_lvt_4e353b346bb9049b942dfe452e3934f8=1756777343,1756816173; PHPSESSID=gaf20mpeo449hianls3bok6u37; Hm_lpvt_17a6d79f196bd7dceed5aefb62507766=1757128113; Hm_lpvt_4e353b346bb9049b942dfe452e3934f8=1757128113"
    page = 1
    http_client = HttpClient(gwsxwk_cookie, gongwen_cookie)
    target_url = f"{base_url}/index/search/index.html?keyword={date}&search_type=10&page={page}"
    print(http_client.get_with_gwsxwk_cookie(target_url))
    