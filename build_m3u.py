import json

INPUT = "data.json"
OUTPUT = "playlist.m3u"


def main():

    with open(INPUT, "r", encoding="utf-8") as f:
        data = json.load(f)

    lines = ["#EXTM3U"]

    for match in data:
        title = match["title"]
        play_id = match["play_id"]

        for s in match["streams"]:

            name = f'{title} | {s["name"]}'
            url = f"https://footsters.livesports18.workers.dev/?play={play_id}&stream={s['stream']}"

            lines.append(f'#EXTINF:-1,{name}')
            lines.append(url)

    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("DONE M3U")


if __name__ == "__main__":
    main()
