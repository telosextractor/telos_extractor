# Modell Dokumentenabgleich (Soll)

Abgleich von **Bestellung**, **Auftragsbestätigung**, **Rechnung** und
**Lieferschein** (was tatsächlich angekommen ist). Gleiches Prinzip wie bei der
Verzollung: Das ML **liest**, die Regeln **entscheiden**.

> Annahme: Die gelieferte Menge kommt aus dem Lieferschein bzw. der
> Wareneingangsmeldung. Fehlt dieses Dokument, wird die Mengenprüfung
> gegen die Lieferung übersprungen und als Warnung gemeldet.

## Gesamtablauf

```mermaid
flowchart TD
    A1[Bestellung] --> B
    A2[Auftragsbestätigung] --> B
    A3[Rechnung] --> B
    A4[Lieferschein] --> B

    B[Vision LLM<br/>Extraktion je Dokument] --> C{Schema gültig?<br/>Pydantic}
    C -->|nein| W1[Warnung<br/>EXTRACTION_INVALID]
    C -->|ja| D{Dokumente über<br/>Bestellnummer verknüpft?}
    D -->|nein| W2[Warnung<br/>DOCUMENT_LINK_MISSING]
    D -->|ja| E{Lieferant und<br/>Währung gleich?}
    E -->|nein| W3[Warnung<br/>HEADER_MISMATCH]
    E -->|ja| F[Positionsabgleich<br/>pro Rechnungsposition]
    W3 --> F
    F --> G{Bestellte Positionen<br/>ohne Rechnung?}
    G -->|ja| W5[Warnung<br/>LINE_NOT_INVOICED]
    G -->|nein| H{Summe Positionen =<br/>Rechnungstotal ±0.01?}
    W5 --> H
    H -->|nein| W4[Warnung<br/>TOTAL_MISMATCH]
    H -->|ja| I{Warnungen<br/>vorhanden?}
    W4 --> I
    I -->|nein| OK[Abgleich ok<br/>Rechnung freigeben]
    I -->|ja| M[Manuelle Prüfung<br/>mit Warnliste]
    W1 --> M
    W2 --> M

    subgraph ML [Machine Learning]
        B
    end
    subgraph KB [Wissensbasiert]
        D
        E
        F
        G
        H
    end
```

## Positionsabgleich (pro Rechnungsposition)

```mermaid
flowchart TD
    A[Rechnungsposition] --> B{Artikelnr. in<br/>Bestellung?}
    B -->|ja| D[Position zuordnen]
    B -->|nein| C{GE EAN in<br/>Bestellung?}
    C -->|ja| D
    C -->|nein| X[Warnung<br/>LINE_NOT_ORDERED]

    D --> E{Lieferschein<br/>vorhanden?}
    E -->|nein| W0[Warnung<br/>DELIVERY_NOTE_MISSING]
    E -->|ja| F{Menge Rechnung ≤<br/>Menge geliefert?}
    F -->|nein| W1[Warnung<br/>QUANTITY_NOT_DELIVERED]
    F -->|ja| G
    W0 --> G
    W1 --> G

    G{Menge geliefert ≤<br/>Menge bestätigt?} -->|nein| W2[Warnung<br/>QUANTITY_OVER_CONFIRMED]
    G -->|ja| H
    W2 --> H

    H{Preis Rechnung =<br/>Preis Auftragsbestätigung?} -->|nein| W3[Warnung<br/>PRICE_MISMATCH]
    H -->|ja| I
    W3 --> I

    I{Preis Auftragsbestätigung =<br/>Preis Bestellung?} -->|nein| W4[Hinweis<br/>PRICE_CHANGED_BY_SUPPLIER]
    I -->|ja| J[Position geprüft]
    W4 --> J
```

## Regeln

| Regel | Vergleich | Code bei Abweichung |
|---|---|---|
| Verknüpfung | Bestellnummer auf Auftragsbestätigung, Rechnung und Lieferschein | `DOCUMENT_LINK_MISSING` |
| Kopfdaten | Lieferant und Währung auf allen Dokumenten gleich | `HEADER_MISMATCH` |
| Zuordnung | Artikelnummer zuerst, GE EAN als Fallback (wie Verzollung) | `LINE_NOT_ORDERED` |
| Lieferung | Verrechnete Menge ≤ gelieferte Menge | `QUANTITY_NOT_DELIVERED` |
| Bestätigung | Gelieferte Menge ≤ bestätigte Menge | `QUANTITY_OVER_CONFIRMED` |
| Preis | Rechnung gegen Auftragsbestätigung (verbindlicher Preis) | `PRICE_MISMATCH` |
| Preisänderung | Auftragsbestätigung gegen Bestellung (nur Hinweis) | `PRICE_CHANGED_BY_SUPPLIER` |
| Offene Positionen | Bestellt, aber nicht verrechnet (Teillieferung) | `LINE_NOT_INVOICED` |
| Total | Summe der Positionen = Rechnungstotal, Toleranz ±0.01 | `TOTAL_MISMATCH` |

Toleranzen (Preis, Total) sind Parameter und werden in den Stammdaten
gepflegt, nicht im Code.

## Offene Punkte

- Lieferschein bestätigen oder durch anderes Dokument ersetzen, sobald die
  Trainingsdaten vorliegen.
- Felder des Datenmodells (`models.py`) für Bestellung, Auftragsbestätigung
  und Lieferschein aus den Beispieldokumenten ableiten.
- Klären, ob Teillieferungen erlaubt sind oder immer eine Warnung auslösen.
