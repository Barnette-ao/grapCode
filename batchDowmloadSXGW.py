import argparse 
from core_sxgw import GWSXWK_ArticleDownloader

gongwen_cookie = "PHPSESSID=hdolnrlil5qrpvua3g5e54bger; Hm_lvt_1f013c54a127ce2677327e03b2f2dcaf=1756777162,1756866814; HMACCOUNT=C8B0C3D372758140; gws_keeplogin=UlgJBlYAUgRKAwwBAxcMAQlJAwUACQUFSQQCAAICBgcGBQ1JBVIDBwsNXQBRDVBTUFAFAgRTV1NYVwZRBVsDAgRWAwUTCg___c___c; gws_search_history=BwwGUVAEA1NYAwoPQlwPBQpGDwQMCxfRjZ___aRj4___aQuLTUjIHTsavXt6YXAl0PBA5GCwYGChPViZ___adj4___aci6jRjZHQjIHXsaTTtobchpDRiKnTtY7TiqIWDlwPBw5HAwQEDxvSjrHTjrLWoa7SjY7Ria8XDkg___c; Hm_lpvt_1f013c54a127ce2677327e03b2f2dcaf=1757127965"
gwsxwk_cookie = "Hm_lvt_17a6d79f196bd7dceed5aefb62507766=1756777343,1756816173; HMACCOUNT=C8B0C3D372758140; Hm_lvt_4e353b346bb9049b942dfe452e3934f8=1756777343,1756816173; PHPSESSID=gaf20mpeo449hianls3bok6u37; Hm_lpvt_17a6d79f196bd7dceed5aefb62507766=1757128113; Hm_lpvt_4e353b346bb9049b942dfe452e3934f8=1757128113"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="思享公文文章下载器")
    parser.add_argument("--gwsxwk_cookie",required=True, type=str, help="思享公文认证Cookie")
    parser.add_argument("--gongwen_cookie",required=True, type=str, help="公文网认证Cookie")
    
    args = parser.parse_args()

    sxgw_downloader = GWSXWK_ArticleDownloader(args.gwsxwk_cookie, args.gongwen_cookie)
    sxgw_downloader.batch_download()