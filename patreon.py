from funcs import request, unixTime
import keys

from datetime import datetime, timedelta
import pytz
import urllib.parse

import asyncio
import json	

async def getJson(url):
    return await request.requestUrl(url, cookies)

async def getPostsComments(link=None, id=None):
    if link == None:
        link = "".join([
            f"https://www.patreon.com/api/posts/{id}/comments2",
            "?include=first_reply,commenter",
            "&fields[comment]=body,created,is_by_creator",
            "&fields[user]=image_url,full_name,url",
            "&page[count]=10",
            "&sort=created"
        ])
    
    data = await getJson(link)
    if not data: return None

async def appendList(list, b=[], passPaid=0):
    mediaData = {}
    for i in list["included"]:
        try: mediaData.update({i["id"]: i["attributes"]["image_urls"]["url"]})
        except: pass
    
    for i in list["data"]:
        attributes = i["attributes"]
        public = True if attributes["min_cents_pledged_to_view"] != None else False
    
        match passPaid:
            case 0: pass
            case 1:
                if public: continue
        
        try: coverImg = attributes["image"]["url"]
        except: coverImg = attributes["share_images"]["landscape"]["url"]

        try:
            attributes["edited_at"]
            datetime = {
                 "upload": unixTime.unsplitedDatetimeEdit(attributes["created_at"]),
                 "edit": unixTime.unsplitedDatetimeEdit(attributes["edited_at"])
            }
        except: datetime = unixTime.unsplitedDatetimeEdit(attributes["created_at"])

        try: content = attributes["content"]
        except: content = None

        media = []
        files = []
        comments = []
        
        if content != None:
            for l in i["relationships"]["media"]["data"]: media.append(mediaData[l["id"]])

        temp = {
            "id": i["id"],
            "name": attributes["title"],
            "coverImg": coverImg,
            "public": public,
            "datetime": datetime,
            "data": {
                "content": content,
                "media": media,
                "files": files,
                "comments": comments,
            }
        }
        
        b.append(temp)

async def getPostsList(link=None, id=None):
    if link == None:
        link = "".join([
            "https://www.patreon.com/api/posts",
            "?include=media",
            "&fields[post]=content,created_at,edited_at,title,image,share_images,min_cents_pledged_to_view",
            "&fields[media]=id,image_urls",
            "&sort=-published_at",
            f"&filter[campaign_id]={id}"
        ])
    
    return await getJson(link)

async def getCreatorData(id):
    data = (await getJson(f"https://www.patreon.com/api/campaigns/{id}"))["data"]
    
    return {
        "id": data["relationships"]["creator"]["data"]["id"],
        "desc": data["attributes"]["summary"],
        "bg": data["attributes"]["cover_photo_url"],
        "user": {
            "name": data["attributes"]["name"],
            "icon": data["attributes"]["avatar_photo_url"]
        },
        "posts": []
    }

async def run(id, type, key=keys.afdian):
    global cookies
    
    cookies = {"session_id": key}
    
    html = await request.requestUrl(f"https://www.patreon.com/{id}", cookies, True)
    if "Not found" in str(html.title): html = await request.requestUrl(f"https://www.patreon.com/user?u={id}", cookies, True)
    
    id = (await request.querySelector("source", html))["srcset"].split("campaign/")[-1].split("/")[0]
    
    a = await getCreatorData(id)
    b = await getPostsList(None, id)

    await appendList(b, a["posts"], type)
    
    #while len(b) > 0:
    #    appendList(b, a["posts"], type)
    #    b = getPostsList(a["user"]["id"], a["posts"][-1]["datetimeNumberMS"])
    
    return json.dumps(a, ensure_ascii=False)

if __name__ == "__main__":
    a = asyncio.run(run(
        "yamaori",
        0
    ))
    print(a)
    with open("test.json", "w", encoding="utf-8") as f: f.write(a)