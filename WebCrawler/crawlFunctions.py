from bs4 import BeautifulSoup
import urllib.request
from urllib.request import Request, urlopen
import contextlib
import selenium.webdriver as wd
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.chrome.options import Options
import lxml.html.clean as clean
import os
import time
from urllib.parse import urljoin
import urllib.error


def scan_root_page(url):
    url_set = set()
    header = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) " +
                            "Chrome/93.0.4577.82 Safari/537.36", }
    req = urllib.request.Request(url=url, headers=header)
    html = urllib.request.urlopen(req).read()
    soup = BeautifulSoup(html, 'html.parser')
    soup = soup.find(id='articleContainer')
    links = soup.find_all('a')
    for link in links:
        s = str(link.get('href'))
        if s is None or s == "None" or s == '':
            continue
        if '#' in s:
            s = s[0:s.index('#')]
        if s.startswith('/'):
            url_set.add("https://www.gov.hk" + s)
        else:
            url_set.add(s)
    return url_set


def get_root_links(load_from_disk, links_file_name):
    urls = []
    if load_from_disk:
        with open(links_file_name, "r") as f:
            for line in f.readlines():
                line = line.strip('\n')
                urls.append(line)
        return urls
    else:
        url_set = scan_root_page("https://www.gov.hk/tc/about/govdirectory/govwebsite/")
        url_list = sorted(url_set)
        with open(links_file_name, "w") as f:
            for url in url_list:
                f.write(url)
                f.write('\n')
        print("Links in ./root_links.txt need filtering manually.")
        exit(1)


def get_absolute_url(current_url, relative_url):
    """
    if relative_url.startswith('/'):
        return current_url.split('/')[0] + "//" + current_url.split('/')[2] + relative_url
    elif relative_url.startswith("./"):
        return current_url.replace(current_url.split('/')[-1], relative_url[2:])
    elif relative_url.startswith("../"):
        pattern = re.compile(r'\.\./')
        length = len(pattern.findall(relative_url))
        return current_url.replace("".join(current_url.split('/')[0 - length - 1:]), relative_url[length * 3])
    """
    return urljoin(current_url, relative_url)


def scan_webpage(current_url):
    """
    "http://www.wsd.gov.hk/",
    "https://www.wsd.gov.hk/tc/water-safety/water-safety-in-buildings/index.html"
    """
    options = Options()
    # 隐藏chrome窗口
    options.add_argument('--headless')
    driver = wd.Chrome(options=options)
    with contextlib.closing(driver) as browser:
        browser.get(current_url)
        result = ec.alert_is_present()(browser)
        if result:
            print(result.text)
            result.accept()
        else:
            print("alert 未弹出！")

        content = browser.page_source
        time.sleep(8)
        cleaner = clean.Cleaner()
        content = cleaner.clean_html(content)
        # print("*" * 20 + "content" + "*" * 20) #debug
        # print(content) #debug
        """
        # extract words from clean_html
        import lxml.html as lh

        doc = lh.fromstring(content)
        ignore_tags = ('script', 'noscript', 'style')
        print("*" * 20 + "words" + "*" * 20)
        for elt in doc.iterdescendants():
            if elt.tag in ignore_tags:
                continue
            text = elt.text or ''
            tail = elt.tail or ''
            words = ' '.join((text, tail)).strip()
            if words:
                print(words)
        """
    return content


def skip_current_url(root_url, current_url):
    root_url = str(root_url)
    current_url = str(current_url)
    if current_url is None or current_url == '' or current_url == "None":
        return True
    if root_url.split('/')[2] == current_url.split('/')[2]:
        return False
    else:
        return True


def extract_content(root_url, current_url):
    print("********loop*********")
    # skip or not
    if skip_current_url(root_url, current_url):
        return set()
    # visited or not
    visited_urls = set()
    if not os.path.exists(root_url.replace("/", "@").replace(":", "$") + "_links.txt"):
        file = open(root_url.replace("/", "@").replace(":", "$") + "_links.txt", "w")
        file.close()
    with open(root_url.replace("/", "@").replace(":", "$") + "_links.txt", "r") as f:
        for line in f.readlines():
            line = line.strip('\n')
            visited_urls.add(line)
    if current_url.strip("/") in visited_urls or current_url in visited_urls:
        return set()
    content = scan_webpage(current_url)
    print(content)
    # raw html text -> .txt    w
    root_folder = "D:\\WebpageData"
    root_dir = "\\" + root_url.replace("/", "@").replace(":", "$")
    current_url_hash = str(hash(current_url))
    current_page_dir = "\\" + current_url_hash
    if not os.path.exists(root_folder + root_dir + current_page_dir):
        os.makedirs(root_folder + root_dir + current_page_dir)
    with open(root_folder + root_dir + current_page_dir + "\\html.txt", "w", encoding='utf-8') as f:
        f.write(content)
    with open(root_folder + root_dir + current_page_dir + "\\url.txt", "w", encoding='utf-8') as f:
        f.write(current_url)
    soup = BeautifulSoup(content, 'html.parser')
    links = soup.find_all('a')
    urls = set()
    files = set()
    for link in links:
        s = str(link.get('href'))
        print("解析出链接： " + s)
        # filter urls
        if s is None or s == '' or s == "None":
            continue
        if '/' not in s:
            continue
        if '@' in s:
            continue
        if '#' in s:
            s = s[0:s.index('#')]
        if "//" not in s:
            s = get_absolute_url(current_url, s)
        if skip_current_url(root_url, s):
            continue
        string = s.split("/")[-1]
        if "." in string and ".htm" not in string:
            files.add(s)
        else:
            print("urls.add() " + s)
            urls.add(s)
    with open(root_url.replace("/", "@").replace(":", "$") + "_links.txt", "a") as f:
        if current_url not in visited_urls:
            f.write(current_url)
            f.write('\n')
    visited_urls.add(current_url)
    # files: makedir -> download -> store in a proper folder
    if files:
        if not os.path.exists(root_folder + root_dir + current_page_dir + "\\documents"):
            os.makedirs(root_folder + root_dir + current_page_dir + "\\documents")
        for file_link in files:
            print(file_link)
            header = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                    + "Chrome/93.0.4577.82 Safari/537.36", }
            request = Request(file_link, headers=header)
            try:
                document = urllib.request.urlopen(request)
                file_name = file_link.split("/")[-1].replace("?", "_QuestionMark_")
                with open(root_folder + root_dir + current_page_dir + "\\documents\\" + file_name, "wb") as f:
                    f.write(document.read())
            except urllib.error.HTTPError as e:
                print('Error code:', e.code)

    print("root_url: " + root_url)
    print("current_url: " + current_url)
    print("links to visit: " + str(urls - visited_urls))
    print("files: " + str(files))
    return urls - visited_urls


def crawl_webpages(root_link, current_link):
    unvisited_link = extract_content(root_link, current_link)
    print(str(len(unvisited_link)) + " links unvisited")
    while len(unvisited_link) > 0:
        next_link = unvisited_link.pop()
        unvisited_link = unvisited_link | extract_content(root_link, next_link)
        print(str(len(unvisited_link)) + " links unvisited")

