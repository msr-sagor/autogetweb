import re
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = "https://footsters.livesports18.workers.dev/"
OUT = "playlist.m3u"


def get_page(url):

    mpd_links = []
    keys = {}

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        def handle_response(response):
            try:
                if ".mpd" in response.url:
                    mpd_links.append(response.url)
            except:
                pass

        page.on("response", handle_response)

        page.goto(url, timeout=60000)
        page.wait_for_timeout(5000)

        html = page.content()

        browser.close()

    return html, mpd_links


def extract_streams(html):

    return re.findall(
        r'<a class="sr" href="(\?play=\d+&stream=\d+)".*?<div class="sr-t[^"]*">\s*(.*?)\s*</div>',
        html,
        re.S
    )


def extract_title(html):

    t = re.search(r"<title>(.*?)</title>", html)
    return t.group(1).split("—")[0].strip() if t else "Live Match"


def main():

    html, _ = get_page(BASE)

    matches = re.findall(r'href="(\?play=\d+)"', html)

    lines = ["#EXTM3U"]

    for m in matches:

        page_url = BASE + m

        html, mpds = get_page(page_url)

        title = extract_title(html)

        streams = extract_streams(html)

        # key (optional)
        key = re.findall(r'"([a-fA-F0-9]{32})":"([a-fA-F0-9]{32})"', html)
        key_id, key_val = (key[0] if key else (None, None))

        for i, (path, name) in enumerate(streams):

            if i >= len(mpds):
                continue

            mpd = mpds[i]

            full_name = f"{title} | {name}"

            lines.append(f'#EXTINF:-1,{full_name}')

            if key_id and key_val:
                lines.append("#KODIPROP:inputstream.adaptive.stream_type=dash")
                lines.append("#KODIPROP:inputstream.adaptive.license_type=clearkey")
                lines.append(f'#KODIPROP:inputstream.adaptive.license_key={key_id}:{key_val}')

            lines.append(mpd)

    Path(OUT).write_text("\n".join(lines), encoding="utf-8")

    print("DONE")


if __name__ == "__main__":
    main()