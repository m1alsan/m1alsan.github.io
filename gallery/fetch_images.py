import requests
import json
import os
import re
from datetime import datetime, timezone

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
            "limit": 20
        }
    )


def load_json(path, default):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return default


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def extract_images(body):
    """
    Sadece markdown içinde ![gitX...](url) formatını alır.
    """
    pattern = r'!\[(git[0-9][^\]]*)\]\((https?://.*?)\)'
    matches = re.findall(pattern, body, re.IGNORECASE)

    images = []

    for alt_text, url in matches:
        alt_text = alt_text.lower()
        category_code_match = re.match(r'(git[0-9]+)', alt_text)
        category_code = category_code_match.group(1) if category_code_match else "unknown"

        images.append({
            "url": url,
            "category_code": category_code
        })

    return images


def main():
    images_data = load_json("gallery/images.json", [])
    categories = load_json("gallery/categories.json", {})
    last_checked = load_json("gallery/last_checked.json", {"last_run": None})

    last_run = last_checked["last_run"]
    now = datetime.now(timezone.utc).isoformat()

    posts = get_posts()
    processed = False

    for post in posts:
        last_update = post.get("updated") or post.get("created")

        if last_run and last_update <= last_run:
            continue

        imgs = extract_images(post.get("body", ""))

        if imgs:
            images_data = [p for p in images_data if p["permlink"] != post["permlink"]]

            formatted_images = []
            for img in imgs:
                category_obj = categories.get(img["category_code"], {})
                category_name = category_obj.get("name", None)

                formatted_images.append({
                    "url": img["url"],
                    "category_code": img["category_code"],
                    "category_name": category_name
                })

            images_data.append({
                "author": post["author"],
                "permlink": post["permlink"],
                "created": post["created"],
                "last_update": last_update,
                "images": formatted_images
            })

            processed = True

    if not processed and posts:
        oldest = posts[-1]
        imgs = extract_images(oldest.get("body", ""))

        if imgs:
            formatted_images = []
            for img in imgs:
                category_obj = categories.get(img["category_code"], {})
                category_name = category_obj.get("name", None)

                formatted_images.append({
                    "url": img["url"],
                    "category_code": img["category_code"],
                    "category_name": category_name
                })

            images_data.append({
                "author": oldest["author"],
                "permlink": oldest["permlink"],
                "created": oldest["created"],
                "last_update": oldest.get("updated") or oldest["created"],
                "images": formatted_images
            })

    save_json("gallery/images.json", images_data)
    save_json("gallery/last_checked.json", {"last_run": now})


if __name__ == "__main__":
    main()
