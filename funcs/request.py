from bs4 import BeautifulSoup
import lxml

import aiohttp
import aiodns
import cchardet

try: import brotlicffi as brotli
except ImportError: import brotli

from selenium.webdriver import Chrome, ChromeOptions

cr = None
def requestUrlBr(url, cookies={}, soup=False):
    global cr
    if cr == None:
        opts = ChromeOptions()
        opts.add_experimental_option("detach", True)
        opts.add_experimental_option("prefs", {"profile.default_content_setting_values": {
            "images": 2
        }})
        opts.add_argument('--headless')
        opts.add_argument('--disable-gpu')
        opts.add_argument("--log-level=3")
        opts.add_argument("--disable-blink-features=AutomationControlled")

        cr = Chrome(options=opts)

    cr.get(url)
    
    if cookies: cr.add_cookie(cookies)
        
    html = cr.page_source

    if soup: html = BeautifulSoup(html, "lxml")

    return html, cr


headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Cafari/537.36'}
async def requestUrl(url, cookies={}, soup=False, headers=headers):
    async with aiohttp.ClientSession(headers=headers, cookies=cookies, connector=aiohttp.TCPConnector()) as s:
        try: getHtml = await s.get(url)
        except Exception as e:
            print(e)
            if e == "Session is closed": await requestUrl(url, cookie, soup)
                
            return False
            
        if "json" in getHtml.headers["Content-Type"]:
            html = await getHtml.json()
            soup = False
        else: html = await getHtml.text()
            
        if soup:
            html = BeautifulSoup(html, "lxml")
            html.url = url
    
    return html
    
    
    
    
async def querySelectorAll(css, soup=None, url=None, cookies={}):
    if not url and not soup: return False

    if not soup: soup = await requestUrl(url, cookies, True)

    return soup.select(css)

async def querySelector(css, soup=None, url=None, cookies={}):
    try: goal = (await querySelectorAll(css, soup, url, cookies))[0]
    except: goal = None

    return goal
    
    

    
def runJS(js, cr=None, url=None, cookies={}, soup=False):
    if cr == None:
        if url == None: return False
        requestUrlBr(url, cookies, soup)[1]

    return cr.execute_script(f"return {js}")
    
def fetch(url, methods=[], then="", cr=None, crUrl=None, cookies={}, soup=False):
    if cr == None:
        if crUrl == None: return False
        requestUrlBr(crUrl, cookies, soup)[1]
    
    if methods != []:
        try: methods[0]
        except: methods.append("get")
        try: methods[1]
        except: methods.append({})
        try: methods[2]
        except: methods.append({})
        
        method = ["{", f"method: '{methods[0]}'", "}"]
        if methods[1] != {}: method.insert(-1, f", headers: {str(methods[1])}")
        if methods[2] != {}: method.insert(-1, f", body: JSON.stringify({str(methods[2])})")
        
        methods = "".join(method)
    
    return runJS(f"await fetch('{url}', {methods}).then(r => r.{then}())", cr)