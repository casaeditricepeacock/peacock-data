#!/usr/bin/env python3
"""
validate.py — guardiano dello standard del grafo peacock-data.

Uso: dalla radice del repo, esegui
    python3 validate.py

Esce con codice 0 se tutto e a posto, 1 se trova ERRORI. Pensato per girare
prima di ogni commit (a mano, in un hook git, o come GitHub Action) cosi un
file fuori standard non rientra piu nel grafo.

Cosa controlla, diviso tra ERRORI (bloccanti) e AVVISI (informativi):

ERRORI
- file dentro books/ con estensione diversa da .json (es. i vecchi .jso rotti)
- nomi file prefissati con lo slug o comunque fuori dal set consentito
- qualunque file .json nel repo che non si parsa
- manifest.json mancante o non allineato ai libri realmente presenti

AVVISI
- libro a cui manca uno dei file canonici (alcuni libri variano legittimamente)
"""
import os, json, sys

CANONICAL = {
    "narrative-object", "narrative-scene", "narrative-silence", "narrative-ritual",
    "narrative-transition", "narrative-weather", "narrative-system-graph",
    "perceptual-field", "print-layer",
}
# estensioni di protocollo dichiarate e ammesse oltre ai 9 canonici
ALLOWED_EXTRA = {
    "narrative-system-kernel", "reader-companion", "narrative-system-variation",
    "narrative-knowledge-field",
}
ALLOWED = CANONICAL | ALLOWED_EXTRA

errors = []
warnings = []

def check_books(root):
    booksdir = os.path.join(root, "books")
    if not os.path.isdir(booksdir):
        errors.append("cartella books/ assente")
        return
    for slug in sorted(os.listdir(booksdir)):
        d = os.path.join(booksdir, slug)
        if not os.path.isdir(d):
            continue
        stems = set()
        for f in os.listdir(d):
            p = os.path.join(d, f)
            if not os.path.isfile(p):
                continue
            if not f.endswith(".json"):
                errors.append(f"books/{slug}/{f}: estensione non .json")
                continue
            stem = f[:-5]
            stems.add(stem)
            if stem not in ALLOWED:
                errors.append(f"books/{slug}/{f}: nome fuori standard (prefisso slug o refuso). Atteso uno di: {sorted(ALLOWED)}")
        # avvisi: canonici mancanti (padova usa knowledge-field al posto di object: non e errore)
        missing = CANONICAL - stems
        if "narrative-object" in missing and "narrative-knowledge-field" in stems:
            missing = missing - {"narrative-object"}
        if missing:
            warnings.append(f"books/{slug}: manca {sorted(missing)}")

def check_json_valid(root):
    for r, _, files in os.walk(root):
        if os.sep + ".git" in r:
            continue
        for f in files:
            if f.endswith(".json"):
                p = os.path.join(r, f)
                try:
                    json.load(open(p, encoding="utf-8"))
                except Exception as e:
                    rel = os.path.relpath(p, root).replace(os.sep, "/")
                    errors.append(f"{rel}: JSON non valido ({e})")

def check_manifest(root):
    mp = os.path.join(root, "manifest.json")
    if not os.path.isfile(mp):
        errors.append("manifest.json assente nella radice")
        return
    try:
        m = json.load(open(mp, encoding="utf-8"))
    except Exception as e:
        errors.append(f"manifest.json non valido ({e})")
        return
    booksdir = os.path.join(root, "books")
    on_disk = {s for s in os.listdir(booksdir) if os.path.isdir(os.path.join(booksdir, s))} if os.path.isdir(booksdir) else set()
    in_manifest = set(m.get("books", {}).keys())
    if on_disk != in_manifest:
        solo_disco = sorted(on_disk - in_manifest)
        solo_manifest = sorted(in_manifest - on_disk)
        msg = "manifest.json non allineato ai libri su disco."
        if solo_disco:
            msg += f" Su disco ma non nel manifest: {solo_disco}."
        if solo_manifest:
            msg += f" Nel manifest ma non su disco: {solo_manifest}."
        msg += " Rigenera con: python3 build_manifest.py"
        errors.append(msg)

if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    check_books(root)
    check_json_valid(root)
    check_manifest(root)

    if warnings:
        print("AVVISI (" + str(len(warnings)) + "):")
        for w in warnings:
            print("  ! " + w)
        print()
    if errors:
        print("ERRORI (" + str(len(errors)) + "):")
        for e in errors:
            print("  X " + e)
        print("\nVALIDAZIONE FALLITA. Correggi gli errori prima di committare.")
        sys.exit(1)
    print("VALIDAZIONE OK. Il grafo rispetta lo standard.")
    sys.exit(0)
