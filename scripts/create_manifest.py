import json
import os


def create_manifest(folder, color):
    data = {
        "color": color,
        "main": sorted(os.listdir(os.path.join(folder, "main"))) if os.path.exists(os.path.join(folder, "main")) else [],
        "common": sorted(os.listdir(os.path.join(folder, "common"))) if os.path.exists(os.path.join(folder, "common")) else [],
        "video": "video.MOV" if os.path.exists(os.path.join(folder, "video.MOV")) else None
    }

    with open(os.path.join(folder, "manifest.json"), "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    create_manifest("public/mat-serebro-temnoe", "mat-serebro-temnoe")
