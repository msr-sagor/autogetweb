import json
import re
import requests
from pathlib import Path

BASE = "https://footsters.livesports18.workers.dev/"
OUT = "playlist.m3u"

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})


def get(url):
    return session.get(url, timeout=20).text


def get_matches(html):
    return re.findall(r'href="(\?play=\d+)"', html)


def parse(html, base_title):

    blocks = re.findall(
        r'<a class="sr" href="(\?play=\d+&stream=\d+)".*?<div class="sr-t[^"]*">\s*(.*?)\s*</div>',
        html,
        re.S
    )

    base = re.search(r'(https?://[^/]+)', BASE).group(1)

    keys = re.findall(r'"([a-fA-F0-9]{32})":"([a-fA-F0-9]{32})"', html)
    key_id, key = (keys[0] if keys else (None, None))

    items = []

    for path, name in blocks:

        url = base + "/" + path

        items.append({
            "title": f"{base_title} | {name}",
            "url": url,
            "key_id": key_id,
            "key": key
        })

    return items


def main():

    home = get(BASE)
    matches = get_matches(home)

    lines = ["#EXTM3U"]

    for m in matches:

        url = BASE + m
        html = get(url)

        title = re.search(r"<title>(.*?)</title>", html).group(1)

        items = parse(html, title)

        for i in items:

            lines.append(
                f'#EXTINF:-1 tvg-name="{i["title"]}",{i["title"]}'
            )

            if i["key_id"] and i["key"]:
                lines.append(
                    f'#KODIPROP:inputstream.adaptive.license_key={i["key_id"]}:{i["key"]}'
                )

            lines.append(i["url"])

    Path(OUT).write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
