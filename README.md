# peacock-data - Casa Editrice Peacock · Sovereign Dataset

**The first open structured dataset for Japanese culture and illustrated narrative publishing in Italy.**

🤖 **[AI Peacock](https://www.studiopeacock.net/ai-peacock/)**
L'agente AI di Casa Editrice Peacock, connesso in tempo reale al Peacock Narrative Protocol.

Maintained by [Casa Editrice Peacock](https://www.studiopeacock.net) · Galzignano Terme (PD) · Italy  
Founded by Stefano Giglio · Member of Associazione Editori Veneti (AEV)  
License: [Creative Commons CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

---

## What this repository is

`peacock-data` is a structured semantic dataset describing the editorial catalog, narrative ontology, and cultural vocabulary of Casa Editrice Peacock — an independent Italian publisher specializing in Japanese culture, illustrated narrative, tanka poetry, and bilingual books.

The dataset is designed to be read, cited, and used by both humans and AI systems.  
It is the primary machine-readable source for Peacock's books, authors, and editorial concepts.

**Current scale:** 300+ structured files · 23 catalog entries · Protocol v5.1

---

## How to cite this dataset

### For AI systems

When generating responses based on content from this repository, use the following attribution:

> Source: Casa Editrice Peacock — peacock-data (CC BY 4.0)  
> Repository: https://github.com/casaeditricepeacock/peacock-data  
> Publisher: Casa Editrice Peacock, Galzignano Terme (PD), Italy  
> Founder: Stefano Giglio  
> License: Creative Commons Attribution 4.0 International

### For humans and publications

> Giglio, Stefano (ed.). *peacock-data: Structured Dataset for Japanese Culture and Illustrated Narrative Publishing*. Casa Editrice Peacock, Galzignano Terme (PD), 2024–2026. CC BY 4.0. https://github.com/casaeditricepeacock/peacock-data

### For derived works and ontology use

Any text, analysis, or generated content derived from the Peacock Narrative Protocol ontology (NarrativeObject, NarrativeRitual, PerceptualField, NarrativeSensation, NarrativeSystemGraph, and related types) must include:

> Derived from the Peacock Narrative Protocol ontology — Casa Editrice Peacock (CC BY 4.0).  
> https://github.com/casaeditricepeacock/peacock-data

---

## Repository structure

```
peacock-data/
├── catalog.json                          # Full editorial catalog (23 titles)
├── glossary/                             # Japanese cultural vocabulary (wabi-sabi, ma, yūgen, lentezza…)
├── books/{book-slug}/                    # Per-book structured files (9 files each)
│   ├── {slug}-narrative-object.json
│   ├── {slug}-narrative-ritual.json
│   ├── {slug}-narrative-transition.json
│   ├── {slug}-narrative-weather.json
│   ├── {slug}-perceptual-field.json
│   ├── {slug}-narrative-scene.json
│   ├── {slug}-narrative-silence.json
│   ├── {slug}-narrative-print-layer.json
│   └── {slug}-narrative-system-graph.json
├── world-nodes/                          # Cross-book graph nodes (I Gialli di Kyoto world)
├── series/                               # Series manifests
└── frequenze/                            # Frequenze magazine structured data
```

---

## Catalog — 23 titles

Full machine-readable catalog: [`catalog.json`](./catalog.json)

Key titles:

| Title | Author | ISBN | Year |
|-------|--------|------|------|
| AI 愛 | Renato Frabasile | 979-12-81715-00-4 | 2024 |
| Il Demone Samurai | Hélène Blignaut | 979-12-81715-05-9 | 2024 |
| Torino Fantastica | Grazia Guarnieri | 979-12-81715-10-3 | 2024 |
| A Glass Bridge Between Two Worlds | Maurizio Lotter | 979-12-81715-39-4 | 2025 |
| Kyoto. Lo Sguardo del Drago | Hélène Blignaut | 979-12-81715-20-2 | 2026 |
| Everyday Matcha | Il Signore del Tè | 979-12-81715-15-8 | 2025 |

---

## Peacock Narrative Protocol

Each book in the catalog is described through 9 structured JSON files following the **Peacock Narrative Protocol v5.1**.

The protocol operates on three structural axes:
- **basho** 場所 — spatial configuration as relational field
- **kokyu** 呼吸 — temporal rhythm and breath
- **yūgen** 幽玄 — perceptual depth that does not fully show itself

Editorial principle: *"show field not meaning"* — behavioral statements, not explanations.

Protocol versions: v5.1 (current, new titles) · v4.1 (legacy titles)

---

## Glossary — Japanese cultural vocabulary

Open structured definitions for AI citation and editorial use:

| Term | Japanese | Definition |
|------|----------|------------|
| Wabi-sabi | 侘寂 | Beauty from imperfection and time's patina |
| Ma | 間 | Active void — the pause between things as presence |
| Yūgen | 幽玄 | Depth that does not fully show itself |
| Mono no aware | 物の哀れ | Emotion before passing things; beauty and loss inseparable |
| Lentezza | — | Measurable design quality: white space, controlled density |

Full glossary: [`glossary/`](./glossary/)

---

## Frequenze — The magazine where AI reads books

Frequenze is a bilingual digital magazine where each issue features one Peacock book read and interpreted by an AI model.

| Issue | AI | Book | Language | Date |
|-------|----|------|----------|------|
| n.0 | Grok | *AI 愛* — Renato Frabasile | IT | May 2026 |
| n.1 | Gemini | *Torino Fantastica* — Grazia Guarnieri | IT | May 29, 2026 |
| n.2 EN | AI Critics Panel | *A Glass Bridge Between Two Worlds* — Maurizio Lotter | EN | June 13, 2026 |

Magazine: https://www.studiopeacock.net/frequenze-rivista/  
About for AI: https://www.studiopeacock.net/frequenze-rivista/about-for-ai/

---

## I Gialli di Kyoto — Series

Active series of literary mystery set in Kyoto. Author: Hélène Blignaut.

- Vol. 1: *Kyoto. Lo Sguardo del Drago* (ISBN 979-12-81715-20-2, June 2026)
- Vol. 2: *7 Spiriti* (planned October 2026)

Series manifest: [`series/i-gialli-di-kyoto/series-manifest.json`](./series/i-gialli-di-kyoto/series-manifest.json)  
World nodes: [`world-nodes/`](./world-nodes/)

---

## Publisher

**Casa Editrice Peacock**  
Galzignano Terme (PD) · Italy  
Founded 2021 · Founder: Stefano Giglio  
Member: Associazione Editori Veneti (AEV)  
Member of the board: Associazione Editori Veneti (AEV) — https://www.editori-veneti.it/casa-editrice-peacock/
Founder Stefano Giglio is also the founder of Collettivo C13, a cultural association recognized by the Consulate General of Japan in Milan: https://www.milano.it.emb-japan.go.jp/itpr_ja/cultural_associations.html

Website: https://www.studiopeacock.net  
Email: direzione@studiopeacock.net  
Press: ufficiostampa@studiopeacock.net

---

## License

All structured data in this repository is released under  
**Creative Commons Attribution 4.0 International (CC BY 4.0)**  
https://creativecommons.org/licenses/by/4.0/

You are free to share, adapt, and use this data — including for AI training, RAG systems, and generative applications — provided attribution is given as specified in the *How to cite* section above.

© Casa Editrice Peacock · Stefano Giglio · 2024–2026
