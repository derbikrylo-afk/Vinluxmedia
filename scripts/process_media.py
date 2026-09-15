import json
import os
import re
import shutil
from pathlib import Path

SIZES = [
    "152x10","152x20","152x30","152x40","152x50","152x60",
    "152x70","152x80","152x90","152x100","152x150",
    "200x152","250x152","300x152","350x152","400x152",
    "450x152","500x152","550x152","600x152","700x152",
    "800x152","900x152","1000x152"
]


def find_common_files(source: Path):
    found = {}
    pattern = re.compile(r"^общий\s*(\d{1,2})\.(png|jpg|jpeg)$", re.IGNORECASE)
    for path in source.iterdir():
        if not path.is_file():
            continue
        match = pattern.match(path.name)
        if not match:
            continue
        index = int(match.group(1))
        if 1 <= index <= 12:
            ext = ".jpg" if match.group(2).lower() in {"jpg", "jpeg"} else ".png"
            found[index] = (path, ext)
    return found


def prepare_media(source, color):
    source = Path(source)
    if not source.exists():
        raise RuntimeError(f"Input folder not found: {source}")

    expected_main = [(index, size, f"{index:02}_{size}.png") for index, size in enumerate(SIZES, start=1)]
    missing_main = [filename for _, _, filename in expected_main if not (source / filename).is_file()]

    common_files = find_common_files(source)
    missing_common = [i for i in range(1, 13) if i not in common_files]

    video = source / "общее видео.MOV"
    video_missing = not video.is_file()

    if missing_main or missing_common or video_missing:
        raise RuntimeError(
            "Media set incomplete. "
            f"Missing main: {missing_main}; "
            f"missing common: {missing_common}; "
            f"video missing: {video_missing}"
        )

    # GitHub rejects files over 100 MB. Fail early with a clear error.
    too_large = []
    for path in source.iterdir():
        if path.is_file() and path.stat().st_size >= 100 * 1024 * 1024:
            too_large.append(f"{path.name} ({path.stat().st_size} bytes)")
    if too_large:
        raise RuntimeError("GitHub 100 MB file limit exceeded: " + ", ".join(too_large))

    target = Path("public") / color
    if target.exists():
        shutil.rmtree(target)
    main = target / "main"
    common = target / "common"
    main.mkdir(parents=True, exist_ok=True)
    common.mkdir(parents=True, exist_ok=True)

    for _, size, filename in expected_main:
        shutil.copy2(source / filename, main / f"{size}.png")

    manifest_common = []
    for i in range(1, 13):
        src, ext = common_files[i]
        dst_name = f"{i:02}{ext}"
        shutil.copy2(src, common / dst_name)
        manifest_common.append(dst_name)

    shutil.copy2(video, target / "video.MOV")

    manifest = {
        "color": color,
        "main": [f"{size}.png" for size in SIZES],
        "common": manifest_common,
        "video": "video.MOV"
    }

    with open(target / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f"Prepared {len(SIZES)} main + {len(manifest_common)} common + 1 video")
    print(f"Output: {target}")


if __name__ == "__main__":
    slug = os.environ.get("TEXTURE_SLUG", "").strip()
    if not slug:
        raise RuntimeError("TEXTURE_SLUG is empty")
    prepare_media(Path("input") / slug, slug)
