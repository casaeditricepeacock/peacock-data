#!/usr/bin/env python3
"""
build_manifest.py — genera manifest.json dalla struttura reale del repo peacock-data.

Uso: dalla radice del repo, esegui
    python3 build_manifest.py

Rigenera manifest.json leggendo i file che esistono davvero. E la fonte unica
dei percorsi per il RAG: non si scrive a mano, si rigenera. Dopo aver aggiunto o
tolto file, lancia questo script e committa il manifest aggiornato.
"""
import os, json, datetime, sys

RAW = "https://raw.githubusercontent.com/casaeditricepeacock/peacock-data/main"
THEMATIC = ["conceptual", "sensorial", "datasets", "cities", "series", "saggistica",
            "authors", "events", "places", "itineraries", "maps", "rituals", "collaborations", "organizations", "media"]

def build(root="."):
    m = {
        "_meta": {
            "generated": datetime.date.today().isoformat(),
            "generator": "build_manifest.py",
            "note": "Mappa dei percorsi reali del grafo. Fonte unica per il routing. Titoli e ISBN in catalog.json."
        },
        "raw_base": RAW,
        "books": {}, "glossary": [], "resources": {}, "root": []
    }
    booksdir = os.path.join(root, "books")
    if os.path.isdir(booksdir):
        for slug in sorted(os.listdir(booksdir)):
            d = os.path.join(booksdir, slug)
            if os.path.isdir(d):
                m["books"][slug] = sorted(f for f in os.listdir(d) if f.endswith(".json"))
    gdir = os.path.join(root, "glossario")
    if os.path.isdir(gdir):
        for f in sorted(os.listdir(gdir)):
            if f.endswith(".json"):
                m["glossary"].append({"term": f[:-5], "path": "glossario/" + f})
    for folder in THEMATIC:
        fabs = os.path.join(root, folder)
        if os.path.isdir(fabs):
            paths = []
            for r, _, files in os.walk(fabs):
                for f in sorted(files):
                    if f.endswith(".json"):
                        paths.append(os.path.relpath(os.path.join(r, f), root).replace(os.sep, "/"))
            m["resources"][folder] = sorted(paths)
    for f in sorted(os.listdir(root)):
        if os.path.isfile(os.path.join(root, f)) and f.endswith(".json") and f != "manifest.json":
            m["root"].append(f)
    # indice per argomento: dove cominciare a leggere
    pj = sorted(
        [p for v in m["resources"].values() for p in v if "pixel-in-japan" in p]
        + ["books/pixel-in-japan/" + f for f in m["books"].get("pixel-in-japan", [])]
    )
    if pj:
        m["topics"] = {
            "pixel-in-japan": {
                "description": "Pixel in Japan, guida ai videogiochi giapponesi di Francesco Verni (2025, 140 pagine, 80 giochi dal 1979 al 2024). Comincia dal dataset dei giochi.",
                "start_here": "datasets/pixel-in-japan-games-dataset.json",
                "then": "datasets/pixel-in-japan-come-si-gioca-dataset.json",
                "files": pj,
            }
        }
    return m

def count(m):
    n = sum(len(v) for v in m["books"].values())
    n += len(m["glossary"])
    n += sum(len(v) for v in m["resources"].values())
    n += len(m["root"])
    return n

if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    m = build(root)
    out = os.path.join(root, "manifest.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(m, fh, ensure_ascii=False, indent=2)
    print(f"manifest.json scritto: {len(m['books'])} libri, {len(m['glossary'])} termini glossario, {count(m)} percorsi totali")
