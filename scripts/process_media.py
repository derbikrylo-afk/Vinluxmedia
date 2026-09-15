import os
import json
import shutil

SIZES = [
    "152x10","152x20","152x30","152x40","152x50","152x60",
    "152x70","152x80","152x90","152x100","152x150",
    "200x152","250x152","300x152","350x152","400x152",
    "450x152","500x152","550x152","600x152","700x152",
    "800x152","900x152","1000x152"
]


def prepare_media(source, color):
    target = os.path.join("public", color)
    main = os.path.join(target, "main")
    common = os.path.join(target, "common")
    os.makedirs(main, exist_ok=True)
    os.makedirs(common, exist_ok=True)

    for index, size in enumerate(SIZES, start=1):
        src = os.path.join(source, f"{index:02}_{size}.png")
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(main, f"{size}.png"))

    for i in range(1, 13):
        src = os.path.join(source, f"общий {i}.png")
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(common, f"{i:02}.png"))

    video = os.path.join(source, "общее видео.MOV")
    if os.path.exists(video):
        shutil.copy2(video, os.path.join(target, "video.MOV"))

    manifest = {
        "color": color,
        "main": SIZES,
        "common": [f"{i:02}.png" for i in range(1,13)],
        "video": "video.MOV"
    }

    with open(os.path.join(target, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    prepare_media("input", "mat-serebro-temnoe")
