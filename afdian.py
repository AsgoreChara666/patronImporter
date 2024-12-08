from funcs import request, unixTime
import keys

import asyncio

from datetime import datetime, timedelta

import json	

def getJson(url):
    return asyncio.run(request.requestUrl(url, cookies))

def setCommentData(targetDict, data, replily=False):
    targetDict.append({
      "id": data["comment_id"],
      "text": data["content"],
      "datetime": unixTime.datetimeToString(data["publish_time"]),
      "datetimeNumberMS": data["publish_sn"],
      "user": {
          "id": data["user"]["user_id"],
          "name": data["user"]["name"],
          "icon": data["user"]["avatar"]
      }
    })

    if not replily: targetDict[-1].update({"replies": []})

def getCommentSubReplies(id, rootID, datetime=0, targetDict=[]):
    data = getJson(f"https://afdian.com/api/comment/get-sub-list?post_id={id}&root_comment_id={rootID}&publish_sn={datetime}")["data"]["list"]
    if len(data) <= 0: return False
    
    for i in data: setCommentData(targetDict, i, True)
    
    return targetDict

def getPostsComments(id, datetime=0, targetDict=[]):
    data = getJson(f"https://afdian.com/api/comment/get-list?post_id={id}&publish_sn={datetime}")["data"]["list"]
    if len(data) <= 0: return False
    
    for i in data:
        setCommentData(targetDict, i)
        for l in i["sub_comments"]: setCommentData(targetDict[-1]["replies"], l, True)
            
        detect = True
        while detect:
            try: postDatetime = targetDict[-1]["replies"][-1]["datetimeNumberMS"]
            except: postDatetime = 0
                
            detect = getCommentSubReplies(id, i["comment_id"], postDatetime, targetDict[-1]["replies"])
    
        targetDict[-1]["replies"].reverse()
    
    return targetDict

def getPostsData(id):
    try: data = getJson(f"https://afdian.com/api/post/get-detail?post_id={id}&type=old")["data"]["post"]
    except: return None
        
    postContent = data["content"]
    if postContent == "": return None
    
    postMedia = []
    for i in data["pics"]: postMedia.append(i)
    
    postFiles = []
    postFiles.append(data["audio"])
    postFiles.append(data["video"])
    postFiles = list(filter(None, postFiles))
    
    postComments = []
    detect = True
    while detect:
        try: commentID = postComments[-1]["datetimeNumberMS"]
        except: commentID = 0
            
        detect = getPostsComments(id, commentID, postComments)
        
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
                if i["is_public"] == 1: continue
        
        try:
            coverImg = i["cover"]
            if coverImg == "":
                coverImg = None
                coverImg = i["pics"][0]
        except:
            pass

        temp = {
            "id": i["post_id"],
            "name": i["title"],
            "coverImg": coverImg,
            "public": i["is_public"],
            "top": i["user_top"],
            "datetime": unixTime.datetimeToString(i["publish_time"]),
            "datetimeNumberMS": i["publish_sn"],
            "data": getPostsData(i["post_id"])
        }
        
        b.append(temp)

def getPostsList(id, datetime=0):
    return getJson(f"https://afdian.com/api/post/get-list?user_id={id}&type=old&publish_sn={datetime}&per_page=10")["data"]["list"]

def getCreatorData(id):
    data = getJson(f"https://afdian.com/api/user/get-profile-by-slug?url_slug={id}&type=old")["data"]["user"]
    
    return {
        "id": data["url_slug"],
        "desc": data["creator"]["detail"],
        "bg": data["cover"],
        "user": {
            "id": data["user_id"],
            "name": data["name"],
            "icon": data["avatar"]
        },
        "posts": []
    }

def run(id, type, key=keys.afdian):
    global cookies
    
    cookies = {"auth_token": key}
    
    a = getCreatorData(id)
    b = getPostsList(a["user"]["id"])

    while len(b) > 0:
        appendList(b, a["posts"], type)
        b = getPostsList(a["user"]["id"], a["posts"][-1]["datetimeNumberMS"])
    
    return json.dumps(a, ensure_ascii=False)
    
if __name__ == "__main__":
    a = run(
        "AMFIG",
        0
    )
    print(a)
    with open("test.json", "w", encoding="utf-8") as f: f.write(a)