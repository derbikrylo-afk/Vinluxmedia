import json
import os
import shutil
from pathlib import Path

SIZES = [
    "152x10","152x20","152x30","152x40","152x50","152x60",
    "152x70","152x80","152x90","152x100","152x150",
    "200x152","250x152","300x152","350x152","400x152",
    "450x152","500x152","550x152","600x152","700x152",
    "800x152","900x152","1000x152"
]


def prepare_media(source, color):
    source = Path(source)
    target = Path('public') / color
    main = target / 'main'
    common = target / 'common'
    main.mkdir(parents=True, exist_ok=True)
    common.mkdir(parents=True, exist_ok=True)

    missing = []
    for index, size in enumerate(SIZES, start=1):
        src = source / f'{index:02}_{size}.png'
        if src.exists():
            shutil.copy2(src, main / f'{size}.png')
        else:
            missing.append(src.name)

    for i in range(1, 13):
        found = None
        for ext in ['png','jpg','jpeg']:
            candidate = source / f'общий {i}.{ext}'
            if candidate.exists():
                found = candidate
                break
        if found:
            shutil.copy2(found, common / found.name.replace(f'общий {i}', f'{i:02}'))

    video = source / 'общее видео.MOV'
    if video.exists():
        shutil.copy2(video, target / 'video.MOV')

    manifest = {
        'color': color,
        'main': [f'{x}.png' for x in SIZES],
        'common': sorted([x.name for x in common.iterdir() if x.is_file()]),
        'video': 'video.MOV' if (target / 'video.MOV').exists() else None,
        'missing_main': missing
    }

    with open(target / 'manifest.json','w',encoding='utf-8') as f:
        json.dump(manifest,f,ensure_ascii=False,indent=2)


if __name__ == '__main__':
    slug = os.environ.get('TEXTURE_SLUG','mat-serebro-temnoe')
    prepare_media(Path('input') / slug, slug)
