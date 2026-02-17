import requests
import json
import os
from datetime import datetime

USERNAME = "m1alsan"
API = "https://api.hive.blog"

def hive_call(method, params):
    response = requests.post(API, json={
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1
    }).json()

    if "result" not in response:
        print("Hive API error:", response)
        return []

    return response["result"]

def get_posts():
    return hive_call(
        "bridge.get_account_posts",
        {
            "account": USERNAME,
            "sort": "blog",
            "limit": 100
        }
    )

def load_json(path, default):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return default

def save_json(path, data):
    with open(path,"w") as f:
        json.dump(data,f,indent=2)

def extract_images(body):
    images = []
    for part in body.split("![]("):
        if ")" in part:
            url = part.split(")")[0]
            if url.startswith("http"):
                images.append(url)
    return images

def main():
    images_data = load_json("gallery/images.json", [])
    last_checked = load_json("gallery/last_checked.json", {"last_run": None})

    last_run = last_checked["last_run"]
    posts = get_posts()
    now = datetime.utcnow().isoformat()

    processed = False

    for post in posts:
        last_update = post.get("updated") or post.get("created")

        if last_run and last_update <= last_run:
            continue

        imgs = extract_images(post.get("body",""))
        if imgs:
            images_data = [p for p in images_data if p["permlink"] != post["permlink"]]
            images_data.append({
                "author": post["author"],
                "permlink": post["permlink"],
                "title": post["title"],
                "created": post["created"],
                "last_update": last_update,
                "images": imgs
            })
            processed = True

    if not processed and posts:
        oldest = posts[-1]
        imgs = extract_images(oldest.get("body",""))
        if imgs:
            images_data.append({
                "author": oldest["author"],
                "permlink": oldest["permlink"],
                "title": oldest["title"],
                "created": oldest["created"],
                "last_update": oldest.get("updated") or oldest["created"],
                "images": imgs
            })

    save_json("gallery/images.json", images_data)
    save_json("gallery/last_checked.json", {"last_run": now})

if __name__ == "__main__":
    main()
