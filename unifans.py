from funcs import request, unixTime
import keys

from datetime import datetime, timedelta

import json

def setCommentData(targetDict, data, replily=False):
    root = 0
    if len(data["parent"]) >= 1:
        for i in targetDict:
            if i["id"] == data["parent"]["parentCommentId"]:
                targetDict = i["replies"]
                replily = True
                root = data["parent"]["parentCommentId"]
                break

    try: userName = data["accountNickname"]
    except: userName = ""

    try: userIcon = data["accountAvatar"]
    except: userIcon = ""

    targetDict.append({
      "root": root,
      "id": data["commentId"],
      "text": data["content"],
      "datetime": unixTime.datetimeToString(data["createTime"]),
      "user": {
          "id": data["accountDomainName"],
          "name": userName,
          "icon": userIcon
      }
    })

    if not replily: targetDict[-1].update({"replies": []})

def getPostsComments(id, index, targetDict=[]):
    data = request.fetch(
        f"https://api.unifans.io/common/getCommentsByPostId?postId={id}&skip={index}&limit=10&_t=0&order=0",
        ["get", {"authorization": cookie}],
        "json", cr
    )["data"]
    if len(data) <= 0: return None
    
    for i in data["comments"]: setCommentData(targetDict, i)
    
    return targetDict

def getPostsData(id):
    data = request.fetch(
        f"https://api.unifans.io/common/getPostsDetail",
        ["post", {"Content-Type": "application/json"}, {"posts": [id]}],
        "json", cr
    )["data"]["posts"][0]
        
    postContent = data["text"]
    
    postMedia = []
    for i in data["attachments"]: postMedia.append(i["address"])
    
    postFiles = []
    
    i=0
    detect = True
    postComments = []
    while detect:
        detect = getPostsComments(id, i, postComments)
        i+=10

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
                if i["locked"] == False: continue

        try: coverImg = i["attachments"][0]["address"]
        except: coverImg = None

        temp = {
            "id": i["postId"],
            "name": i["title"],
            "coverImg": coverImg,
            "public": not i["locked"],
            "data": getPostsData(i["postId"]),
            "datetime": {
                 "upload": unixTime.datetimeToString(i["createTime"]),
                 "edit": unixTime.datetimeToString(i["updateTime"])
            }
        }
        
        b.append(temp)
    
def getPostsList(id, index=0):
    return request.fetch(f"https://api.unifans.io/creator/posts?domainName={id}&skip={index}&limit=10&_t=0", [], "json", cr)

def getCreatorData(id):
    data = request.fetch(f"https://api.unifans.io/common/getPersonalInfo?domainName={id}&_t=0", [], "json", cr)["data"]
    if not data: return False

    return {
        "id": data["domainName"],
        "desc": data["creatingDes"],
        "bg": data["cover"],
        "user": {
            "name": data["homeName"],
            "icon": data["avatar"]
        },
        "posts": []
    }

def run(id, type, key=keys.unifans):
    global cr
    global cookie
    
    cr = request.requestUrlBr("https://app.unifans.io")[1]
    request.runJS(f"localStorage.setItem('token', '{key}')", cr)
    
    cookie = key
    
    a = getCreatorData(id)
    b = getPostsList(a["id"])
    
    i=10
    while True:
        try: b["data"]["posts"]
        except: break
            
        appendList(b["data"]["posts"], a["posts"], type)
        b = getPostsList(a["id"], i)
        i+=10
    
    return json.dumps(a, ensure_ascii=False)
    
if __name__ == "__main__":
    import asyncio
    
    a = run(
        "jingmiantu",
        0
    )
    print(a)
    with open("test.json", "w", encoding="utf-8") as f: f.write(a)