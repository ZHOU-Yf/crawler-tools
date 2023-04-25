from crawlFunctions import crawl_webpages


if __name__ == "__main__":
    # crawl_webpages("https://www.vtc.edu.hk/html/tc/", "https://www.vtc.edu.hk/html/tc/") urllib.error.URLError: <urlopen error [SSL: DH_KEY_TOO_SMALL] dh key too small (_ssl.c:997)>
    # crawl_webpages("https://www.swd.gov.hk/", "https://www.swd.gov.hk/") http.client.IncompleteRead: IncompleteRead(1095764 bytes read, 280364 more expected)
    # OSError: [Errno 22] Invalid argument: 'D:\\WebpageData\\https$@@www.ogcio.gov.hk@tc@\\7527679475770827866\\documents\\securimage_play.php?id=63e7ca4819e09'
    # crawl_webpages("https://www.qef.org.hk/", "https://www.qef.org.hk/")  有弹窗
    crawl_webpages("https://www.lcsd.gov.hk", "https://www.lcsd.gov.hk/en/index.html")
    # crawl_webpages("https://www.smokefree.hk", "https://www.smokefree.hk/?lang=tc") 文件名有“？”
    # crawl_webpages("https://www.lad.gov.hk/index.html", "https://www.lad.gov.hk/index.html") http.client.IncompleteRead: IncompleteRead(110135762 bytes read, 154391218 more expected)
    # crawl_webpages("https://www.judiciary.hk", "https://www.judiciary.hk")
