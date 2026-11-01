# Ist-Prozess Verzollung (manuell)

Notation: BPMN 2.0 · ADONIS: Geschäftsprozessdiagramm

## Beteiligte

| Pool / Lane | Rolle |
|---|---|
| Pool «Kunde» (extern, zugeklappt) | sendet Vorbereitungs- und Verzollungsmail, beantwortet Rückfragen |
| Pool «Zolldienstleister», Lane «Sachbearbeiter» | alle internen Schritte (keine feste Rollenverteilung) |
| Systeme (als Datenspeicher) | Outlook, L-Base, e-dec, Kundenliste (CPRS), TARES, Archiv |

## Phase 1 – Vorbereitung

| ID | Typ | Beschriftung | Weiter zu |
|---|---|---|---|
| E1 | Start (Nachricht) | Vorbereitungsmail eingetroffen (Ordner «Vorbereitung», ~60/Tag) | T1 |
| T1 | Aufgabe | Dokumente drucken und zu Dossier bündeln | T2 |
| T2 | Aufgabe | Dossier nach Datum ins Fach «unbearbeitet» legen | T3 |
| T3 | Aufgabe | Ca. 10 älteste Dossiers holen | G1 |
| G1 | XOR | Deckblatt Lieferant vorhanden? | ja: T4a / nein: T4b |
| T4a | Aufgabe | Deckblattdaten vom Lieferanten-Deckblatt nehmen | G2 |
| T4b | Aufgabe | Deckblattdaten von der Rechnung nehmen | G2 |
| G2 | XOR (Zusammenführung) | – | T5 |
| T5 | Aufgabe | Deckblatt in L-Base erfassen (Sendungsnr. Kunde, Kolli, Gewicht, Lieferant) → interne Nummer, automatische Übergabe an e-dec | T6 |
| T6 | Teilprozess | Positionen in e-dec erfassen (Kundenliste, Aufteilung, Karton, Rundung) | T7 |
| T7 | Aufgabe | Präferenznachweis vorhanden? vermerken (UE / EUR.1 / keiner) | T8 |
| T8 | Aufgabe | Dossier ins Fach «erfasst» legen | Z1 |
| Z1 | Zwischenereignis (Nachricht, wartend) | Verzollungsmail eingetroffen (Ordner «Verzollung», Tag X) | T9 |

## Phase 2 – Verzollung

| ID | Typ | Beschriftung | Weiter zu |
|---|---|---|---|
| T9 | Aufgabe | Anmeldenummer und T1/T2/nTV eintragen | T10 |
| T10 | Aufgabe | Anhänge mit Vorbereitung abgleichen | G3 |
| G3 | XOR | Stimmt überein? | ja: G4 / nein: T15 |
| G4 | XOR | Präferenznachweis vermerkt? | nein: T12 / ja: G5 |
| G5 | XOR | Ermächtigter Ausführer? | ja: T12 / nein: T11 |
| T11 | Aufgabe (Regel) | Nachweis prüfen: gültig/vorhanden, UE nur bis 6000 EUR (darüber EUR.1 nötig), Präferenz laut TARES möglich | G6 |
| G6 | XOR | Nachweis gültig? | ja: T12 / nein: T15 |
| T12 | Aufgabe | Sendung verzollen | T13 |
| T13 | Aufgabe | EL und BS empfangen und an Kunden senden (Archiv in BCC) | T14 |
| T14 | Aufgabe | Dossier ablegen, am Tagesende scannen | E2 |
| E2 | Ende | Sendung verzollt und archiviert | – |
| T15 | Aufgabe | Rückfrage beim Kunden | T10 |

## Wissensquellen

| Quelle | Inhalt | Verwendet in |
|---|---|---|
| Kundenliste (CPRS, Excel) | Artikelnummer, verbindliche Tarifnummer, Präferenz ja/nein, MWST-Code | T6, T11 |
| TARES | Kontrolle Präferenzmöglichkeit und MWST-Code | T6, T11 |

## Schmerzpunkte

1. Medienbruch: PDF → Papier → Abtippen → Scan
2. Positionen in e-dec von Hand erfassen und rechnen (T6)
3. Status nur über physische Fächer sichtbar
4. Manueller Abgleich Auftrag ↔ Vorbereitung (T10)
5. Präferenzprüfung von Hand, finanzielles Risiko (T11)
6. Doppelte Archivierung (Scan und BCC)

## Ansatzpunkte telos

- Kern: T6 (Extraktion + Regelschicht)
- Erweiterung: T10 (automatischer Abgleich mit Warnsignal), T11 (Präferenzregeln, z.B. 6000-EUR-Grenze)
