#!/usr/bin/env python3
"""
build_manifest.py — genera manifest.json dalla struttura reale del repo peacock-data.

Uso: dalla radice del repo, esegui
    python3 build_manifest.py

Rigenera manifest.json leggendo i file che esistono davvero. E la fonte unica
dei percorsi per il RAG: non si scrive a mano, si rigenera. Dopo aver aggiunto o
tolto file, lancia questo script e committa il manifest aggiornato.
"""
import os, re, json, datetime, sys, unicodedata

RAW = "https://raw.githubusercontent.com/casaeditricepeacock/peacock-data/main"
THEMATIC = ["conceptual", "sensorial", "datasets", "cities", "series", "saggistica",
            "authors", "events", "places", "itineraries", "maps", "rituals", "collaborations", "organizations", "media"]


# Corrispondenze dichiarate per i libri il cui titolo nel grafo non coincide con il catalogo
CATALOG_TITLE = {
    "kyoto-sguardo-del-drago": "Kyoto. Lo Sguardo del Drago",
    "ratata-lascia-cadere-la-pioggia": "Ra-ta-ta. Lascia cadere la pioggia",
}
# Fusioni di nome file dichiarate: file tematici il cui nome non contiene lo slug del libro
NAME_ALIASES = {
    "ratata-lascia-cadere-la-pioggia": ["ratata"],
    "la-locanda-nakamura": ["nakamura"],
    "bukku": ["the-unhoused-book"],
    "demone-samurai": ["demon-samurai"],
    "padova-fantastica": ["fantastic-padova"],
    "ai-natura-algoritmi": ["frabasile-ai-natura"],
    "everyday-matcha": ["matcha-sensoriale-paolo", "matcha-pratica-resistenza"],
}
BOOK_KEYS = ("book", "related_book", "target_book", "related_books", "books", "primary_book", "primary_books")

def _titles_in(data):
    """Titoli di libri dichiarati in campi strutturati (book, related_book, ...) di un file."""
    out = set()
    def add(v):
        if isinstance(v, str) and v:
            out.add(_norm(v))
        elif isinstance(v, dict):
            for k in ("title", "title_it", "title_en"):
                if isinstance(v.get(k), str):
                    out.add(_norm(v[k]))
            if isinstance(v.get("isbn"), str):
                digits = re.sub(r"\D", "", v["isbn"])
                if len(digits) == 13:
                    out.add("isbn:" + digits)
        elif isinstance(v, list):
            for x in v:
                add(x)
    def walk(o):
        if isinstance(o, dict):
            has_book = any(k in BOOK_KEYS for k in o)
            if has_book and isinstance(o.get("isbn"), str):
                digits = re.sub(r"\D", "", o["isbn"])
                if len(digits) == 13:
                    out.add("isbn:" + digits)
            for k, v in o.items():
                if k in BOOK_KEYS:
                    add(v)
                walk(v)
        elif isinstance(o, list):
            for x in o:
                walk(x)
    walk(data)
    return out

# Libri con un punto di partenza dedicato (dataset) invece del grafo di sistema
CUSTOM_START = {
    "pixel-in-japan": {
        "description": "Pixel in Japan, guida ai videogiochi giapponesi di Francesco Verni (2025, 140 pagine, 80 giochi dal 1979 al 2024). Comincia dal dataset dei giochi.",
        "start_here": "datasets/pixel-in-japan-games-dataset.json",
        "then": "datasets/pixel-in-japan-come-si-gioca-dataset.json",
    }
}

def _norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")

def _load(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return None

def book_meta(root, slug, catalog):
    """Metadati del libro: solo dati presenti nel grafo (system-graph) e nel catalogo."""
    sg = _load(os.path.join(root, "books", slug, "narrative-system-graph.json")) or {}
    b = sg.get("book")
    if isinstance(b, str):
        b = {"title": b}
    b = b if isinstance(b, dict) else {}
    title = b.get("title") or b.get("title_en") or b.get("title_it")
    ct = CATALOG_TITLE.get(slug) or title
    cat = None
    if ct:
        n = _norm(ct)
        cat = catalog.get(n) or next((v for k, v in catalog.items() if len(k) > 6 and (k.startswith(n) or n.startswith(k))), None)
        if slug == "burn-out-pandemic":
            cat = catalog.get(_norm("Burn Out Pandemic")) or cat
    cat = cat or {}
    if not title or _norm(title) == _norm(slug):
        title = cat.get("title") or title
    meta = {"title": title}
    for k in ("author", "illustrator"):
        v = b.get(k) or cat.get(k)
        if isinstance(v, str) and v:
            meta[k] = v
    for k in ("isbn", "year"):
        v = b.get(k) or cat.get(k)
        if v:
            meta[k] = v
    return meta

def build_topics(root, m):
    cat_list = (_load(os.path.join(root, "catalog.json")) or {}).get("catalog", [])
    catalog = {_norm(b["title"]): b for b in cat_list if isinstance(b, dict) and b.get("title")}
    slugs = sorted(m["books"].keys())
    # indice dei file tematici: percorso -> testo
    texts = {}
    declared = {}
    for folder, paths in m["resources"].items():
        for pth in paths:
            try:
                with open(os.path.join(root, pth), encoding="utf-8") as fh:
                    texts[pth] = fh.read()
                declared[pth] = _titles_in(json.loads(texts[pth]))
            except Exception:
                texts[pth] = texts.get(pth, "")
                declared[pth] = set()
    def slug_in_name(slug, base):
        # corrispondenza sul nome del file; vince lo slug piu lungo (es. -borsetta, pandemic)
        for variant in {slug, slug.replace("-", "_")}:
            i = base.find(variant)
            while i != -1:
                end = i + len(variant)
                nxt = base[end:end + 1]
                if not (nxt.isalnum()):
                    others = [o for o in slugs if o != slug and len(o) > len(slug)
                              and base.find(o, max(0, i - 0)) == i]
                    if not others:
                        return True
                i = base.find(variant, i + 1)
        return False
    topics = {}
    for slug in slugs:
        meta = book_meta(root, slug, catalog)
        core = ["books/%s/%s" % (slug, f) for f in m["books"][slug]]
        linked = []
        for pth, txt in texts.items():
            base = os.path.basename(pth)
            nb = base.replace("_", "-")
            tn = _norm(meta.get("title") or "")
            by_title = bool(tn) and len(tn) >= 8 and any(d == tn or d.startswith(tn) or tn.startswith(d) and len(d) >= 12 for d in declared.get(pth, ()))
            isbn_d = re.sub(r"\D", "", str(meta.get("isbn", "")))
            by_title = by_title or (len(isbn_d) == 13 and ("isbn:" + isbn_d) in declared.get(pth, ()))
            if (slug_in_name(slug, base) or ("books/%s/" % slug) in txt or by_title
                    or any(a in nb for a in NAME_ALIASES.get(slug, []))):
                linked.append(pth)
        # scheda autore
        auth = meta.get("author", "")
        for part in re.split(r"\s*(?:,|&|\be\b|\band\b)\s*", auth):
            if part:
                ap = "authors/AuthorProfile_%s.json" % _norm(part)
                if os.path.isfile(os.path.join(root, ap)) and ap not in linked:
                    linked.append(ap)
                # file tematici che portano il nome dell'autore (es. hara-rota)
                an = _norm(part)
                if len(an) >= 8:
                    for pth in texts:
                        if pth not in linked and not pth.startswith("authors/") and an in os.path.basename(pth).replace("_", "-").lower():
                            linked.append(pth)
        start = "books/%s/narrative-system-graph.json" % slug
        then = "books/%s/narrative-scene.json" % slug
        if start not in core:
            start = core[0] if core else None
        if then not in core:
            then = core[1] if len(core) > 1 else None
        desc = "%s" % (meta.get("title") or slug)
        if meta.get("author"):
            desc += " di %s" % meta["author"]
        if meta.get("year"):
            desc += " (%s)" % meta["year"]
        desc += "."
        entry = {"title": meta.get("title") or slug, "description": desc}
        for k in ("author", "illustrator", "isbn", "year"):
            if k in meta:
                entry[k] = meta[k]
        entry["start_here"] = start
        entry["then"] = then
        # i file narrativi sono gia elencati in "books": qui solo la cartella e i file collegati
        entry["narrative_folder"] = "books/%s/" % slug
        entry["files"] = sorted(set(linked))
        # file che citano il titolo del libro senza essere collegati per nome o percorso
        ttl = meta.get("title") or ""
        if len(ttl) >= 8:
            ment = sorted(pth for pth, txt in texts.items() if ttl in txt and pth not in entry["files"])
            ment = [x for x in ment if not x.startswith("datasets/")]
            if ment:
                entry["also_mentioned_in"] = ment
        if slug in CUSTOM_START:
            entry.update(CUSTOM_START[slug])
            entry["files"] = sorted(set(entry["files"]) | set(
                p for v in m["resources"].values() for p in v if slug in os.path.basename(p)))
            entry.pop("also_mentioned_in", None)
        topics[slug] = entry
    return topics

MARK_START = "<!-- BOOK-ROUTES:START (generato da build_manifest.py: non modificare a mano) -->"
MARK_END = "<!-- BOOK-ROUTES:END -->"

def update_llms(root, m):
    """Riscrive il blocco BOOK-ROUTES di llms.txt se i marcatori sono presenti."""
    path = os.path.join(root, "llms.txt")
    if not os.path.isfile(path):
        return False
    with open(path, encoding="utf-8") as fh:
        txt = fh.read()
    if MARK_START not in txt or MARK_END not in txt:
        return False
    lines = [MARK_START,
             "## BOOK ROUTES: ONE ENTRY PER BOOK",
             "",
             "For ANY book, do not guess file names. Find the title below, open its starting file, then open manifest.json: its \"topics\" section has an entry for every book (key = slug) with the full list of files (narrative layers, sensory cards, events, authors, places, media).",
             "Starting file pattern: %s/books/<slug>/narrative-system-graph.json" % RAW,
             ""]
    for slug, t in sorted(m["topics"].items(), key=lambda kv: _norm(kv[1]["title"])):
        who = " (%s)" % t["author"] if t.get("author") else ""
        lines.append("- %s%s | slug: %s | start: %s/%s | %d files" % (t["title"], who, slug, RAW, t["start_here"], len(t["files"])))
    lines += ["", MARK_END]
    block = "\n".join(lines)
    new = txt[:txt.index(MARK_START)] + block + txt[txt.index(MARK_END) + len(MARK_END):]
    if new != txt:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(new)
    return True

def build(root="."):
    m = {
        "_meta": {
            "generated": datetime.date.today().isoformat(),
            "generator": "build_manifest.py",
            "note": "Mappa dei percorsi reali del grafo. Fonte unica per il routing. Titoli e ISBN in catalog.json.",
            "topics_howto": "Ogni libro ha una voce in topics (chiave = slug della cartella in books/). Comincia da start_here, poi then; i 9 file narrativi sono in narrative_folder (elenco in books), gli altri file collegati (schede sensoriali, eventi, autori, luoghi, media, saggi) sono in files; also_mentioned_in elenca file che citano il titolo senza essere collegati."
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
    # indice per argomento: dove cominciare a leggere (una voce per ogni libro)
    m["topics"] = build_topics(root, m)
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
    if update_llms(root, m):
        print("llms.txt: blocco BOOK-ROUTES aggiornato")
    print(f"manifest.json scritto: {len(m['books'])} libri, {len(m['glossary'])} termini glossario, {count(m)} percorsi totali")
