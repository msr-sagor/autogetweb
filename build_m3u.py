import json

INPUT = "data.json"
OUTPUT = "playlist.m3u"


def main():

    with open(INPUT, "r", encoding="utf-8") as f:
        data = json.load(f)

    lines = ["#EXTM3U"]

    for match in data:

        title = match["title"]

        for s in match["streams"]:

            name = f'{title} | {s["name"]}'
            url = f'https://footsters.livesports18.workers.dev/?play={match["play_id"]}&stream={s["stream"]}'

            lines.append(f'#EXTINF:-1 tvg-name="{name}",{name}')

            # Only add DRM if available
            if s["mpd"] and s["clearkey"]["kid"] and s["clearkey"]["key"]:

                lines.append("#KODIPROP:inputstream.adaptive.stream_type=dash")
                lines.append("#KODIPROP:inputstream.adaptive.license_type=clearkey")
                lines.append(
                    f'#KODIPROP:inputstream.adaptive.license_key={s["clearkey"]["kid"]}:{s["clearkey"]["key"]}'
                )

                lines.append(s["mpd"])
            else:
                lines.append(url)

    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("M3U DONE")


if __name__ == "__main__":
    main()