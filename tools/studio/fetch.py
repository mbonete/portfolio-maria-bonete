"""CC0 textures and models for the studio, from Poly Haven and ambientCG, into tools/studio/assets/
(gitignored). Every download is recorded in ASSETS.md (id, source page, licence) so the site can credit
them. Run with the system python3, not Blender's.

  python3 fetch.py search polyhaven textures wood      # ids, names and categories that match
  python3 fetch.py search polyhaven models plant
  python3 fetch.py search ambientcg fabric
  python3 fetch.py polyhaven <id> [2k] [Diffuse,Rough,nor_gl,Displacement]   # a texture's maps as jpg
  python3 fetch.py polyhaven-model <id> [2k]           # a model as .blend with its textures
  python3 fetch.py ambientcg <id> [2K]                 # a material's maps (zip, unpacked)
  python3 fetch.py polyhaven-hdri <id> [2k]            # an environment map (.hdr), for reflections
"""
import io, json, os, sys, urllib.request, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
LEDGER = os.path.join(HERE, "ASSETS.md")
UA = {"User-Agent": "studio-scene-fetch/1.0"}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return r.read()


def save(url, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        with open(path, "wb") as f:
            f.write(get(url))
    print("  ", os.path.relpath(path, HERE))


def record(source, ident, page):
    line = f"| {ident} | {source} | {page} | CC0 |\n"
    if not os.path.exists(LEDGER):
        with open(LEDGER, "w") as f:
            f.write("# Third-party assets in the studio scene\n\nAll CC0 (public domain): no attribution is required, "
                    "but the site's \"How this site was built\" page names them.\n\n| id | source | page | licence |\n|---|---|---|---|\n")
    if line not in open(LEDGER).read():
        with open(LEDGER, "a") as f:
            f.write(line)


def search(source, *terms):
    if source == "polyhaven":
        kind, q = terms[0], " ".join(terms[1:]).lower()
        data = json.loads(get(f"https://api.polyhaven.com/assets?t={kind}"))
        for k, v in data.items():
            hay = " ".join([k, v.get("name", ""), *v.get("categories", []), *v.get("tags", [])]).lower()
            if all(t in hay for t in q.split()):
                print(k, "|", v.get("name"), "|", ",".join(v.get("categories", [])))
    else:
        q = "+".join(terms)
        data = json.loads(get(f"https://ambientcg.com/api/v2/full_json?q={q}&type=Material&limit=40&include=tagData"))
        for a in data.get("foundAssets", []):
            print(a["assetId"], "|", a.get("displayName", ""), "|", ",".join(a.get("tags", [])[:8]))


def polyhaven(ident, res="2k", maps="Diffuse,Rough,nor_gl,Displacement"):
    files = json.loads(get(f"https://api.polyhaven.com/files/{ident}"))
    for m in maps.split(","):
        if m not in files:
            print("  (no", m, "- has:", ", ".join(k for k in files if k not in ("blend", "gltf", "mtlx")), ")")
            continue
        f = files[m][res]["jpg" if "jpg" in files[m][res] else "png"]
        save(f["url"], os.path.join(ASSETS, "polyhaven", ident, os.path.basename(f["url"])))
    record("Poly Haven", ident, f"https://polyhaven.com/a/{ident}")


def polyhaven_model(ident, res="2k"):
    files = json.loads(get(f"https://api.polyhaven.com/files/{ident}"))
    b = files["blend"][res]["blend"]
    root = os.path.join(ASSETS, "polyhaven", ident)
    save(b["url"], os.path.join(root, os.path.basename(b["url"])))
    for rel, inc in b.get("include", {}).items():
        save(inc["url"], os.path.join(root, rel))
    record("Poly Haven", ident, f"https://polyhaven.com/a/{ident}")


def polyhaven_hdri(ident, res="2k"):
    files = json.loads(get(f"https://api.polyhaven.com/files/{ident}"))
    f = files["hdri"][res]["hdr"]
    save(f["url"], os.path.join(ASSETS, "polyhaven", ident, os.path.basename(f["url"])))
    record("Poly Haven", ident, f"https://polyhaven.com/a/{ident}")


def ambientcg(ident, res="2K"):
    z = zipfile.ZipFile(io.BytesIO(get(f"https://ambientcg.com/get?file={ident}_{res}-JPG.zip")))
    root = os.path.join(ASSETS, "ambientcg", ident)
    os.makedirs(root, exist_ok=True)
    for n in z.namelist():
        if n.lower().endswith((".jpg", ".png")) and "/" not in n:
            with open(os.path.join(root, n), "wb") as f:
                f.write(z.read(n))
            print("  ", os.path.relpath(os.path.join(root, n), HERE))
    record("ambientCG", ident, f"https://ambientcg.com/view?id={ident}")


if __name__ == "__main__":
    cmd, *args = sys.argv[1:]
    {"search": search, "polyhaven": polyhaven, "polyhaven-model": polyhaven_model, "polyhaven-hdri": polyhaven_hdri, "ambientcg": ambientcg}[cmd](*args)
