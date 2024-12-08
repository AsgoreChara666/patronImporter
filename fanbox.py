from funcs import request, unixTime
import keys

from datetime import datetime, timedelta
import pytz
import urllib.parse

import json	

def datetimesEdit(datetimes, utf=-9):
    dates = datetimes.split("T")[0].split(" ")[0].split("-")
    times = datetimes.split("T")[-1].split("+")[0].split(" ")[-1].split(":")
    
    return unixTime.datetimeEdit(dates, times, -9)

def setCommentData(targetDict, data, replily=False):
    datetime = datetimesEdit(data["createdDatetime"])

    targetDict.append({
      "root": data["rootCommentId"],
      "id": data["id"],
      "text": data["body"],
      "datetime": datetime,
      "user": {
          "id": data["user"]["userId"],
          "name": data["user"]["name"],
          "icon": data["user"]["iconUrl"]
      }
    })

    if not replily: targetDict[-1].update({"replies": []})

def getPostsComments(id, index, targetDict=[]):
    data = request.fetch(f"https://api.fanbox.cc/post.listComments?postId={id}&offset={index}&limit=10", [], "json", cr)["body"]["items"]
    if len(data) <= 0: return False

    for i in data:
        setCommentData(targetDict, i)
        for l in i["replies"]: setCommentData(targetDict[-1]["replies"], l, True)
    
    return targetDict

def getPostsData(id):
    data = request.fetch(f"https://api.fanbox.cc/post.info?postId={id}", [], "json", cr)["body"]["body"]
    if not data: return None

    try: postContent = data["text"]
    except:
        postContent = []
        for i in data["blocks"]:
            if i["text"] == "":
                postContent.append("\n")
                continue
            postContent.append(i["text"])

    postContent = "".join(postContent)

    postMedia = []
    try:
        for i in data["images"]: postMedia.append(urllib.parse.unquote(i["originalUrl"]))
    except: pass


    postFiles = []
    try:
        for i in data["files"]:
            postFiles.append({
                "name": f"{i['name']}.{i['extension']}",
                "url": i["url"]
            })
    except: pass

    postComments = []
    detect = True
    i = 0
    while detect:
        detect = getPostsComments(id, i, postComments)
        i+=10
        
    postComments.reverse()

    return {
            "content": postContent,
            "media": postMedia,
            "files": postFiles,
            "comments": postComments,
        }

def appendList(list, b=[], passPaid=0):
    for i in list:
        match passPaid:
            case 0: pass
            case 1:
                if i["isRestricted"] == False: continue

        try: coverImg = i["cover"]["url"]
        except: coverImg = None
            
        temp = {
            "id": i["id"],
            "name": i["title"],
            "coverImg": coverImg,
            "public": i["isRestricted"],
            "data": getPostsData(i["id"]),
            "datetime": {
                 "upload": datetimesEdit(i["publishedDatetime"], -9),
                 "edit": datetimesEdit(i["updatedDatetime"], -9)
            }
        }
        
        b.append(temp)

def getPostsList(id, datetime=str(datetime.now(tz=pytz.timezone('Asia/Tokyo'))).split(".")[0]):
    return request.fetch(f"https://api.fanbox.cc/post.listCreator?creatorId={id}&maxPublishedDatetime={urllib.parse.quote_plus(datetime)}&maxId=2147483647&limit=10", [], "json", cr)
        
def getCreatorData(id):
    data = request.fetch(f"https://api.fanbox.cc/creator.get?creatorId={id}", [], "json", cr)["body"]
    if not data: return False

    return {
        "id": data["creatorId"],
        "desc": data["description"],
        "bg": data["coverImageUrl"],
        "user": {
            "id": data["user"]["userId"],
            "name": data["user"]["name"],
            "icon": data["user"]["iconUrl"]
        },
        "posts": []
    }

def run(id, key, type):
    global cr

    cr = request.requestUrlBr("https://www.fanbox.cc/favicon.ico", {"name": "FANBOXSESSID", "value": key})[1]

    a = getPostsList(id)
    b = getCreatorData(id)

    while len(a["body"]) > 1:
        appendList(a["body"], b["posts"], type)
        a = getPostsList(id, datetimesEdit(b["posts"][-1]["datetime"]["upload"], 9))
        del b["posts"][-1]
    
    return json.dumps(b, ensure_ascii=False)

if __name__ == "__main__":
    import asyncio
    
    a = run(
        "msmspc",
        keys.fanbox,
        0
    )
    print(a)
    with open("test.json", "w", encoding="utf-8") as f: f.write(a)