# Pfad B · Piyush · Externe Evidenz (Web)

> Seit Sa 14:50 macht Piyush diesen Pfad neben dem Lead (nur 4 Personen). Die Eval-Zahl ist zu Aditya gewandert ([`PFAD-A.md`](PFAD-A.md) A9/A10).

**Ziel:** Wettbewerb und Trends aus dem Web holen. Jede Aussage hat **URL, Abrufdatum, Vertrauensstufe**. Trends ohne interne Belege sind **Annahmen** (Evidenzstufe D).
**Schreibt in:** `src/backend/evidence_external/`, `tests/pfad_b/`.
**Liefert:** `web_evidence.json`, `web_signals.json` (über `pipeline.py --stage web`).
**Vertrag (nie ändern):** `research(scenario, signals) -> tuple[list[Evidence], list[Signal]]`.

## Regeln

- **Kein Webbeleg ohne URL.** Nur Vertrauen high/medium kommt in Befunde. Preise/Business-Case sind out of scope: nicht danach fragen.
- Alles über `core/llm.py` (Cache!). Nach dem ersten Lauf geht die Demo offline.
- Webbeleg-`meta`: `trust`, `publisher`, `published`, `stance` (`supports`/`contradicts`/`neutral`), `supports_signal_id` (interner Befund, falls passend). Dennis liest `trust`.

## Tickets

### [x] B1 · Websuche-Probe (30 min, 15:30-16:00)
**Prompt:**
> Ich baue Pfad B, Ticket B1. Wir nutzen die OpenAI-Websuche über `core.llm.ask_json(..., tools=[{"type": "web_search"}])` statt eigenem Scraping,
> weil sie Quellen-URLs mitliefert und in 24 h kein Scraper robust wird. Verworfen: Testmagazine scrapen (Paywalls, fragil).
> Lege in `evidence_external/` ein Pydantic-Schema `Claims` an (Liste von `Claim`: text, url, publisher, published, stance, about) und `ask_claims(question) -> list[Claim]`.
> Claims ohne URL oder mit URL, die nicht mit http beginnt, werden verworfen. Test mit Fake-`ask_json`. Dann **ein** echter Aufruf:
> „How do the Mercedes-Benz E-Class and Audi A6 e-tron (2025/2026) handle physical controls vs. touch controls?“
- **Fertig, wenn:** Test grün · echte Frage liefert ≥ 3 Claims mit echter URL.
- **Wenn es hakt:** Websuche + Schema zusammen geht nicht → zweistufig: erst Websuche als Freitext, dann `ask_json` ohne Tools, das den Text ins Schema bringt; URLs nur übernehmen, wenn sie wörtlich im Freitext vorkamen.

### [x] B2 · Fragen + Vertrauen (60 min, 16:00-17:00)
**Prompt:**
> Ticket B2. (1) `questions.py`: aus den Top-8-Befunden der Art complaint/unmet_need (bis zur echten Datei: `src/shared/beispiele/stufen/signals.json`)
> und `scenario.competitors` je eine Wettbewerbsfrage; dazu 5 feste Trendfragen für 2028-2031 im Segment und Markt des Szenarios (Laden/Reichweite, Software/Apps, Bedienung, Innenraum, Assistenz).
> (2) `trust.py`: Vertrauen per Regel aus der Domain: Hersteller, Testmagazine (caranddriver, motortrend, edmunds, autobild, whatcar), Studien/Institute (jdpower, consumerreports, mckinsey, deloitte) = high;
> Fachpresse/Nachrichten = medium; Foren, Reddit, YouTube, unbekannt = low. Tests mit 6 URLs.
- **Fertig, wenn:** 13 Fragen für G60-US · Trust-Test grün · `sync`.

### [x] B3 · `research()` v1 (45 min, 17:00-17:45)
**Prompt:**
> Ticket B3. `research()` in `web_research.py`: alle Fragen → Claims → `Evidence(source_type="web", id="EV-<szenario>-WEB-<nn>", url, retrieved_at, source_name=publisher)` mit Meta (siehe Regeln in `docs/pfade/PFAD-B.md`).
> Wettbewerbsfragen mit ≥ 1 Claim high/medium → `Signal(kind="competitor_advantage")`, Trendfragen → `Signal(kind="trend")`, IDs `SIG-<szenario>-WEB-<nn>`, Kategorie aus der Frage.
> Doppelte URLs zusammenführen. Test mit Fake-`ask_claims`.
- **Fertig, wenn:** `pipeline.py --scenario G60-US --stage web` → **≥ 5 Webbelege mit URL** · `sync`.

### [x] B4 · Triangulation Web ↔ intern (60 min, 19:30-20:30)
**Prompt:**
> Ticket B4. Webbelege sollen interne Befunde stützen können, weil zwei unabhängige Quellenarten die Evidenzstufe heben (Regel in `evidence_level.py`).
> Bei Wettbewerbsfragen ist der auslösende interne Befund bekannt → `meta["supports_signal_id"]` + `stance`. In `pipeline.py` (Stufe requirements): für jeden Webbeleg mit
> `stance=supports` die ID an `evidence_ids` des internen Befunds hängen und `web` zu `source_types` hinzufügen. `contradicts` wird nicht angehängt, aber als Gegenbeleg für die Challenge mitgegeben.
> Test in `tests/pfad_b/` mit 2 Befunden und 3 Webbelegen.
- **Fertig, wenn:** ≥ 3 interne Befunde haben `web` in `source_types` · `sync`.

### [x] B5 · F70-EU (30 min, Nacht)
- `pipeline.py --scenario F70-EU --stage web` (andere Wettbewerber in der Config). Cache prüfen: zweiter Lauf ohne Netz.
- **Ergebnis B5:** F70-EU: 99 Webbelege (alle mit URL), 9 Web-Befunde, 14 Befunde mit `web`. Zweiter Lauf mit `DEMO_MODUS=true` gibt dieselben Zahlen ohne Netz.

---

## Welle 2 (Sa 21:00 bis So 07:30)

Prompt zum Kopieren für jede Karte: [`docs/UPGRADE_WELLE2.md`](../UPGRADE_WELLE2.md) §2.

- [x] **W-L5** · Web-Fragen aus Config: Horizont aus `successor_horizon`, G68-CN bis 8 Trendfragen (`questions.py`) · 01:30–02:00
- [x] **W-L6** · NHTSA-Beschwerden als zweite Kundenquelle für US (neue Datei `nhtsa.py`, Cache committen) · 02:00–03:00
- [x] *(kann)* **W-L10** · fueleconomy.gov-Connector (Reichweite Wettbewerber)
