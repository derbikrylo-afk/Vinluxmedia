import os
import json


def report(folder):
    files=[]
    for root, _, names in os.walk(folder):
        for name in names:
            files.append(os.path.join(root,name))

    result={
        "folder": folder,
        "files": len(files),
        "status": "ready"
    }

    with open("media_report.json","w",encoding="utf-8") as f:
        json.dump(result,f,ensure_ascii=False,indent=2)


if __name__ == "__main__":
    report("public")
