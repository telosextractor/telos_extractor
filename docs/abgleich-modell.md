# Modell Dokumentenabgleich (Soll)

Abgleich von **Bestellung**, **Auftragsbestätigung**, **Rechnung** und
**Lieferschein** (was tatsächlich angekommen ist). Gleiches Prinzip wie bei der
Verzollung: Das ML **liest**, die Regeln **entscheiden**.

> Annahme: Die gelieferte Menge kommt aus dem Lieferschein bzw. der
> Wareneingangsmeldung. Fehlt dieses Dokument, wird die Mengenprüfung
> gegen die Lieferung übersprungen und als Warnung gemeldet.

## Grundregel

**Alles, was auf der Rechnung steht, muss bestellt worden sein.**
Umgekehrt gilt das nicht: Nicht alles, was bestellt wurde, muss auf dieser
Rechnung stehen.

| Fall | Beispiel | Bewertung |
|---|---|---|
| Vollständige Lieferung | Bestellt 10 A, 5 B – verrechnet 10 A, 5 B | ok |
| Artikel fehlt | Bestellt 10 A, 5 B – verrechnet nur 10 A (B nicht geliefert) | Hinweis, B bleibt offen |
| Teilmenge | Bestellt 10 A – geliefert und verrechnet 6 A | Hinweis, 4 A bleiben offen |
| Sammelrechnung | Rechnung enthält Bestellung 1 **und** Artikel aus Bestellung 2 | ok, wenn jede Position einer Bestellung zugeordnet werden kann |
| Nicht bestellt | Rechnung enthält Artikel C, der in keiner Bestellung vorkommt | **Fehler** |
| Zu viel verrechnet | Bestellt 10 A – verrechnet 12 A | **Fehler** |

**Fehler** blockieren die Freigabe und führen zur manuellen Prüfung.
**Hinweise** werden angezeigt, blockieren aber nicht.

## Gesamtablauf

```mermaid
flowchart TD
    A3[Rechnung] --> B
    A1[Bestellung/en] --> B
    A2[Auftragsbestätigung/en] --> B
    A4[Lieferschein/e] --> B

    B[Vision LLM<br/>Extraktion je Dokument] --> C{Schema gültig?<br/>Pydantic}
    C -->|nein| F1[Fehler<br/>EXTRACTION_INVALID]
    C -->|ja| D[Bestellnummern<br/>auf Rechnung ermitteln]
    D --> D2{Mehrere Bestellungen?<br/>Sammelrechnung}
    D2 -->|ja| D3[Alle referenzierten<br/>Bestellungen laden]
    D2 -->|nein| D4[Eine Bestellung laden]
    D3 --> E
    D4 --> E
    E{Alle Bestellungen<br/>gefunden?} -->|nein| F2[Fehler<br/>ORDER_NOT_FOUND]
    E -->|ja| K{Lieferant und<br/>Währung gleich?}
    K -->|nein| F3[Fehler<br/>HEADER_MISMATCH]
    K -->|ja| P[Positionsabgleich<br/>pro Rechnungsposition]

    P --> O{Bestellpositionen<br/>nicht oder nur teilweise<br/>verrechnet?}
    O -->|ja| H1[Hinweis<br/>ORDER_LINE_OPEN<br/>Restmenge bleibt offen]
    O -->|nein| T
    H1 --> T
    T{Summe Positionen =<br/>Rechnungstotal ±0.01?} -->|nein| F4[Fehler<br/>TOTAL_MISMATCH]
    T -->|ja| Q
    F4 --> Q

    Q{Fehler<br/>vorhanden?} -->|ja| M[Manuelle Prüfung<br/>mit Fehler- und Hinweisliste]
    Q -->|nein| OK[Rechnung freigeben]
    F1 --> M
    F2 --> M
    F3 --> M

    OK --> R{Restmengen<br/>offen?}
    R -->|ja| S1[Bestellung bleibt offen<br/>für weitere Lieferung]
    R -->|nein| S2[Bestellung abgeschlossen]

    subgraph ML [Machine Learning]
        B
    end
    subgraph KB [Wissensbasiert]
        D
        D2
        E
        K
        P
        O
        T
    end
```

## Positionsabgleich (pro Rechnungsposition)

```mermaid
flowchart TD
    A[Rechnungsposition] --> B{Bestellnr. auf<br/>Position angegeben?}
    B -->|ja| C1[In dieser Bestellung suchen]
    B -->|nein| C2[In allen Bestellungen<br/>der Rechnung suchen]
    C1 --> Z
    C2 --> Z
    Z{Artikelnr. oder<br/>GE EAN gefunden?} -->|nein| X[Fehler<br/>LINE_NOT_ORDERED]
    Z -->|ja| D[Bestellposition zuordnen]

    D --> Q1{Menge Rechnung ≤<br/>offene Bestellmenge?}
    Q1 -->|nein| F1[Fehler<br/>QUANTITY_OVER_ORDERED]
    Q1 -->|ja| Q2{Menge Rechnung =<br/>offene Bestellmenge?}
    Q2 -->|nein, weniger| H1[Hinweis<br/>PARTIAL_QUANTITY]
    Q2 -->|ja| L
    F1 --> L
    H1 --> L

    L{Lieferschein<br/>vorhanden?} -->|nein| W0[Warnung<br/>DELIVERY_NOTE_MISSING]
    L -->|ja| L2{Menge Rechnung ≤<br/>Menge geliefert?}
    L2 -->|nein| F2[Fehler<br/>QUANTITY_NOT_DELIVERED]
    L2 -->|ja| P1
    W0 --> P1
    F2 --> P1

    P1{Preis Rechnung =<br/>Preis Auftragsbestätigung?} -->|nein| F3[Fehler<br/>PRICE_MISMATCH]
    P1 -->|ja| P2
    F3 --> P2

    P2{Preis Auftragsbestätigung =<br/>Preis Bestellung?} -->|nein| H2[Hinweis<br/>PRICE_CHANGED_BY_SUPPLIER]
    P2 -->|ja| J[Position geprüft<br/>Menge vormerken]
    H2 --> J
```

## Regeln

| Regel | Vergleich | Code | Stufe |
|---|---|---|---|
| Verknüpfung | Jede Bestellnummer auf der Rechnung existiert | `ORDER_NOT_FOUND` | Fehler |
| Kopfdaten | Lieferant und Währung auf allen Dokumenten gleich | `HEADER_MISMATCH` | Fehler |
| Bestellt | Jede Rechnungsposition gehört zu einer Bestellposition (Artikelnr. zuerst, GE EAN als Fallback, bei Sammelrechnung über alle Bestellungen) | `LINE_NOT_ORDERED` | Fehler |
| Übermenge | Verrechnete Menge ≤ offene Bestellmenge | `QUANTITY_OVER_ORDERED` | Fehler |
| Teilmenge | Verrechnete Menge < offene Bestellmenge | `PARTIAL_QUANTITY` | Hinweis |
| Lieferung | Verrechnete Menge ≤ gelieferte Menge | `QUANTITY_NOT_DELIVERED` | Fehler |
| Lieferschein | Lieferschein fehlt, Lieferprüfung übersprungen | `DELIVERY_NOTE_MISSING` | Warnung |
| Preis | Rechnung gegen Auftragsbestätigung (verbindlicher Preis) | `PRICE_MISMATCH` | Fehler |
| Preisänderung | Auftragsbestätigung gegen Bestellung | `PRICE_CHANGED_BY_SUPPLIER` | Hinweis |
| Offene Positionen | Bestellt, aber (noch) nicht oder nur teilweise verrechnet | `ORDER_LINE_OPEN` | Hinweis |
| Total | Summe der Positionen = Rechnungstotal, Toleranz ±0.01 | `TOTAL_MISMATCH` | Fehler |

**Offene Bestellmenge** = bestätigte Menge (laut Auftragsbestätigung, sonst
Bestellmenge) − bereits auf früheren Rechnungen verrechnete Menge.
Damit funktionieren auch mehrere Teilrechnungen zur selben Bestellung:
Erst bei der Freigabe bucht eine Rechnung ihre vorgemerkten Mengen auf die
Bestellpositionen,
bis die Restmenge 0 ist.

Toleranzen (Preis, Total) sind Parameter und werden in den Stammdaten
gepflegt, nicht im Code.

## Offene Punkte

- Lieferschein bestätigen oder durch anderes Dokument ersetzen, sobald die
  Trainingsdaten vorliegen.
- Felder des Datenmodells (`models.py`) für Bestellung, Auftragsbestätigung
  und Lieferschein aus den Beispieldokumenten ableiten.
- Prüfen, ob Sammelrechnungen die Bestellnummer pro Position angeben oder
  nur im Kopf.
- Klären, ab wann eine offene Restmenge als Warnung gilt (z.B. nach X Tagen
  ohne Lieferung).
