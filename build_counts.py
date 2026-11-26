#!/usr/bin/env python3
"""
build_counts.py — genera counts.json e changelog.json dalla situazione reale del repo.

Uso: dalla radice del repo, prima di ogni commit importante:
    python3 build_manifest.py && python3 build_counts.py

counts.json   conteggi misurati sui file, con data di misura e metodo.
changelog.json file aggiunti per mese e cartella (dalla storia git), per distinguere
              nodi nuovi da nodi rivisti. La storia git parte dal 26 maggio 2026.
Nessun valore e scritto a mano, tranne il numero di ancore verificate sul testo
(controllo manuale, con la data dell'ultimo controllo).
"""
import os, json, re, glob, subprocess, datetime, collections

ROOT = "."
ANCHOR = re.compile(r"textual_anchor_|poetic_anchor|anchor_it")
VERIFIED_ANCHOR_FILES = {"count": 9, "last_checked": "2026-10-14", "note": "Controllo manuale contro il testo del libro; non calcolato dallo script."}

def jsons():
    out = []
    for r, ds, fs in os.walk(ROOT):
        ds[:] = [d for d in ds if not d.startswith(".")]
        for f in fs:
            if f.endswith(".json"):
                out.append(os.path.join(r, f).replace("\\", "/")[2:])
    return sorted(out)

def counts():
    js = jsons()
    allfiles = []
    for r, ds, fs in os.walk(ROOT):
        ds[:] = [d for d in ds if not d.startswith(".")]
        allfiles += fs
    folders = collections.Counter()
    for p in js:
        folders[p.split("/")[0] if "/" in p else "(root)"] += 1
    anchors = 0
    for p in js:
        try:
            if ANCHOR.search(open(p, encoding="utf-8").read()):
                anchors += 1
        except Exception:
            pass
    cat = json.load(open("catalog.json", encoding="utf-8"))
    gi = json.load(open("glossary-index.json", encoding="utf-8"))
    books = [d for d in os.listdir("books") if os.path.isdir(os.path.join("books", d))]
    return {
        "measured_on": datetime.date.today().isoformat(),
        "generator": "build_counts.py",
        "method": "Conteggio dei file presenti nel repository al momento della misura. Ogni cifra e ricalcolabile con lo script.",
        "files_total": len(allfiles),
        "json_files": len(js),
        "json_files_by_folder": dict(sorted(folders.items(), key=lambda x: -x[1])),
        "catalog_entries": len(cat["catalog"]),
        "book_folders": len(books),
        "glossary_files": folders.get("glossario", 0),
        "glossary_published": gi.get("statistics", {}).get("published"),
        "json_files_declaring_anchor": anchors,
        "verified_anchor_files": VERIFIED_ANCHOR_FILES,
    }

def changelog():
    try:
        out = subprocess.check_output(
            ["git", "log", "--diff-filter=A", "--name-only", "--date=format:%Y-%m", "--format=@@%ad"],
            text=True, encoding="utf-8")
        commits = subprocess.check_output(["git", "log", "--date=format:%Y-%m", "--format=%ad"], text=True).split()
    except Exception:
        return {"error": "git history not available"}
    added = collections.defaultdict(collections.Counter)
    month = None
    for line in out.splitlines():
        if line.startswith("@@"):
            month = line[2:]
        elif line.strip() and line.endswith(".json") and month:
            added[month][line.split("/")[0] if "/" in line else "(root)"] += 1
    ncom = collections.Counter(commits)
    months = {}
    for mth in sorted(set(added) | set(ncom)):
        months[mth] = {"commits": ncom.get(mth, 0), "json_files_added_by_folder": dict(sorted(added[mth].items(), key=lambda x: -x[1]))}
    return {
        "generated_on": datetime.date.today().isoformat(),
        "generator": "build_counts.py",
        "note": "La storia git parte dal 26 maggio 2026, data della riorganizzazione del repository. I file aggiunti sono contati alla prima comparsa; le modifiche successive non sono elencate.",
        "months": months,
    }

if __name__ == "__main__":
    c = counts()
    json.dump(c, open("counts.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2); open("counts.json", "a").write("\n")
    ch = changelog()
    json.dump(ch, open("changelog.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2); open("changelog.json", "a").write("\n")
    print("counts.json:", c["json_files"], "JSON,", c["catalog_entries"], "catalog,", c["glossary_files"], "glossario")
    print("changelog.json:", len(ch.get("months", {})), "mesi")
