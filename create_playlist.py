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


def extract_title(html):

    t = re.search(r"<title>(.*?)</title>", html)
    return t.group(1).split("—")[0].strip() if t else "Live Match"


def parse_streams(html, match_title):

    results = []

    blocks = re.findall(
        r'<a class="sr" href="(\?play=\d+&stream=\d+)".*?<div class="sr-t[^"]*">\s*(.*?)\s*</div>',
        html,
        re.S
    )

    base = re.search(r'(https?://[^/]+)', BASE).group(1)

    # 🔑 ClearKey extract
    keys = re.findall(r'"([a-fA-F0-9]{32})":"([a-fA-F0-9]{32})"', html)
    key_id, key = (keys[0] if keys else (None, None))

    # 🎬 MPD extract (important)
    mpd = re.findall(r'(https?://[^"]+\.mpd[^"]*)', html)

    for i, (path, name) in enumerate(blocks):

        url = mpd[i] if i < len(mpd) else ""

        if not url:
            continue

        results.append({
            "title": f"{match_title} | {name}",
            "mpd": url,
            "key_id": key_id,
            "key": key
        })

    return results


def main():

    home = get(BASE)
    matches = get_matches(home)

    lines = ["#EXTM3U"]

    for m in matches:

        html = get(BASE + m)

        title = extract_title(html)

        items = parse_streams(html, title)

        for i in items:

            lines.append(
                f'#EXTINF:-1 tvg-name="{i["title"]}",{i["title"]}'
            )

            if i["key_id"] and i["key"]:
                lines.append("#KODIPROP:inputstream.adaptive.stream_type=dash")
                lines.append("#KODIPROP:inputstream.adaptive.license_type=clearkey")
                lines.append(f'#KODIPROP:inputstream.adaptive.license_key={i["key_id"]}:{i["key"]}')

            lines.append(i["mpd"])

    Path(OUT).write_text("\n".join(lines), encoding="utf-8")

    print("DONE")


if __name__ == "__main__":
    main()