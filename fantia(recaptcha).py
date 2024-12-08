from funcs import request, unixTime
import keys

import asyncio
import time

from datetime import datetime, timedelta

import json

def getJson(url, soup=False, headers={}):
    return asyncio.run(request.requestUrl(url, cookies, soup, headers))

def datetimesEdit(datetimeNumber, utf=-9):
    try:
        yr = datetimeNumber.split(" ")[3]
        mth = datetimeNumber.split(" ")[2]
        day = datetimeNumber.split(" ")[1]
        times = datetimeNumber.split(" ")[4].split(":")
    
        match mth:
            case "Jan": mth = 1
            case "Feb": mth = 2
            case "Mar": mth = 3
            case "Apr": mth = 4
            case "May": mth = 5
            case "Jun": mth = 6
            case "Jul": mth = 7
            case "Aug": mth = 8
            case "Sep": mth = 9
            case "Oct": mth = 10
            case "Nov": mth = 11
            case "Dec": mth = 12
            
        dates = []
        dates.append(yr)
        dates.append(mth)
        dates.append(day)
    except:
        dates = datetimeNumber.split("T")[0].split("-")
        times = datetimeNumber.split("T")[-1].split(".")[0].split(":")
        
    return unixTime.datetimeEdit(dates, times, utf)

def setCommentData(targetDict, data, replily=False):
    targetDict.append({
      "id": data["id"],
      "text": data["text"],
      "datetime": datetimesEdit(data["posted_at"]),
      "user": {
          "id": data["contributor"]["identify_token"],
          "name": data["contributor"]["name"],
          "icon": data["contributor"]["icon"]
      }
    })

    if not replily: targetDict[-1].update({"replies": []})

def setPostsData(data, b, passPaid=0):
    match passPaid:
        case 0: pass
        case 1:
            if data["foreign_plan_price"] == 0: return

    try: b["content"].append(data["comment"])
    except: pass
    
    media = []
    try:
        for i in data["post_content_photos"]: media.append(i["url"]["original"])
        b["media"].append(media)
    except: pass
        
    if data["post_content_comment_data"]["comments"][0] == []: return False
    
    for i in data["post_content_comment_data"]["comments"][0]:
        setCommentData(b["comments"], i)
        
        for l in i["replies"]: setCommentData(b["comments"][-1]["replies"], l)
        b["comments"][-1]["replies"].reverse()

def appendList(data, b=[], passPaid=0):
    for i in data:
        i = i["post"]
        
        try: coverImg = i["thumb"]["main"]
        except: coverImg = None

        temp = {
            "id": i["id"],
            "name": i["title"],
            "coverImg": coverImg,
            "datetime": datetimesEdit(i["posted_at"]),
            "data": {
                "content": [i["comment"]],
                "media": [],
                "files": [],
                "comments": []
            },
        }
        
        tempData = temp["data"]
        for l in i["post_comments"][0][1][0]:
            setCommentData(tempData["comments"], l)
            for o in l["replies"]: etCommentData(tempData["comments"][-1]["replies"], o)
            
            tempData["comments"][-1]["replies"].reverse()
        
        for l in i["post_contents"]: setPostsData(l, tempData, passPaid)
        
        tempData["content"] = list(filter(None, tempData["content"]))
        
        for l in range(len(tempData["comments"]) - 1):
            for o in range(len(tempData["comments"]) - 1 - l):
                try: tempData["comments"][o+1] = tempData["comments"][o+1][0]
                except: pass
                
                if int(tempData["comments"][o]["id"]) > int(tempData["comments"][o+1]["id"]):
                    tempData["comments"][o], tempData["comments"][o+1] = tempData["comments"][o+1], tempData["comments"][o]
                    
        b.append(temp)
        
        time.sleep(5)

def getPostsList(id, page=1):
    data = getJson(f"https://fantia.jp/fanclubs/{id}/posts?page={page}", True)
    
    postsList = []
    for i in data.select(".row-eq-height .col-lg-3 a.link-block"):
        a = getJson(
            f"https://fantia.jp/api/v1/posts/{i['href'].split('/')[-1]}",
            False, {
                "x-csrf-token": "oYZDRCVTWD5T1auzixwVA7TI6TW2O7euWne4GeC2CKu_TYQD1LRYLYvOdj0sD8MshybhMGNa80Oo6bDMa_-e_Q",
                "x-requested-with": "XMLHttpRequest"
        })
        if "429" in a: break
        postsList.append(a)
        
    return postsList

def getCreatorData(id):
    data = getJson(f"https://fantia.jp/api/v1/fanclubs/{id}")["fanclub"]
    
    return {
        "id": data["id"],
        "desc": data["title"],
        "bg": data["cover"]["main"],
        "user": {
            "id": data["user"]["id"],
            "name": data["name"],
            "icon": data["icon"]["main"]
        },
        "posts": []
    }

def run(id, key, type):
    global cookies
    
    cookies = {"_session_id": key}
    
    a = getCreatorData(id)
    b = getPostsList(a["id"])
    
    i = 2
    while True:
        appendList(b, a["posts"], type)
        
        if len(b) < 20: break
        b = getPostsList(a["id"], i)
        i+=1
    
    return json.dumps(a, ensure_ascii=False)

if __name__ == "__main__":
    a = run(
        491908,
        keys.fantia,
        0
    )
    print(a)
    with open("test.json", "w", encoding="utf-8") as f: f.write(a)