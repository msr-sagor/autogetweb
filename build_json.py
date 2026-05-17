import json
import re
import requests

BASE = "https://footsters.livesports18.workers.dev/"
HEADERS = {"User-Agent": "Mozilla/5.0"}

OUTPUT = "data.json"


def get_html(url):
    return requests.get(url, headers=HEADERS, timeout=20).text


def extract_title(html):
    t = re.search(r"<title>(.*?)</title>", html)
    return t.group(1).split("—")[0].strip() if t else "Live Match"


def extract_streams(html):
    return re.findall(r'play=(\d+)&stream=(\d+)', html)


def extract_names(html):
    return re.findall(r'<div class="sr-t[^"]*">\s*(.*?)\s*</div>', html)


def build(play_id):

    html = get_html(f"{BASE}?play={play_id}")

    streams = extract_streams(html)
    names = extract_names(html)

    return {
        "play_id": play_id,
        "title": extract_title(html),
        "group": "Sports",
        "streams": [
            {
                "name": names[i] if i < len(names) else f"Source {i+1}",
                "stream": int(s),
                "mpd": "",              # will fill later if you have extractor
                "clearkey": {
                    "kid": "",
                    "key": ""
                }
            }
            for i, (_, s) in enumerate(streams)
        ]
    }


def main():

    play_ids = [312, 355, 367, 405, 406, 407]

    data = []

    for pid in play_ids:
        try:
            data.append(build(pid))
            print("OK", pid)
        except Exception as e:
            print("FAIL", pid, e)

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()