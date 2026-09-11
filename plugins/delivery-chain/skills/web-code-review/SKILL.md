---
name: web-code-review
description: Wykonaj findings-first code review zamrożonego kandydata aplikacji webowej, szukając błędów, regresji, niespełnionych kryteriów, martwego kodu, przypadkowej złożoności i testów dających fałszywą pewność. Użyj jako osobnej bramki przed wydaniem; nie implementuj poprawek podczas recenzji.
---

# Web Code Review

Recenzuj jak osoba odpowiedzialna za znalezienie problemu, a nie za obronę
implementacji. Faza jest read-only.

## Zakres

1. Przeczytaj instrukcje repozytorium, brief, plan, diff i pełne call sites
   zmienionego kodu. Potwierdź identyfikator kandydata.
2. Zapisz `reviewer_mode`: `independent-agent`, `fresh-task`, `separate-pass` albo
   `author-self-review`. Nie udawaj niezależności. Dla kandydata publicznego
   tylko dwa pierwsze tryby mogą otrzymać `PASS`; pozostałe kończą się
   `BLOCKED` i instrukcją uruchomienia recenzji w świeżym zadaniu.
3. Prześledź dane i sterowanie od wejścia użytkownika do skutku. Sprawdź happy
   path, błędy, concurrency, ponowienia, cleanup i granice komponentów.
4. Porównaj implementację z każdym kryterium odbioru oraz threat modelem.
5. Oceń testy: czy mogą przejść przy zepsutej funkcji, czy mockują właściwą
   granicę i czy obejmują regresję.
6. Szukaj slopu, który ma skutek: duplikacji źródeł prawdy, martwych fallbacków,
   nieużywanego kodu, przypadkowych abstrakcji, niespójnych stanów UI,
   hardkodowanych danych, ukrytych błędów i zależności dodanych bez potrzeby.

## Findings

Raportuj tylko problem z obserwowalnym skutkiem. Każdy finding ma priorytet
`P0–P3`, warunki wystąpienia, skutek, dowód, konkretną lokalizację i najwęższy
kierunek naprawy. Jeśli nie ma findings, opisz sprawdzone ścieżki i ograniczenia
recenzji zamiast samego „LGTM”.

Zapisz `docs/quality/05-code-review.md` według
[kontraktu artefaktów](../safe-web-delivery/references/artifact-contract.md).
Nierozwiązany `P0` lub `P1` oznacza `FAIL`. `P2` musi trafić do release gate i
mieć decyzję; `P3` nie blokuje, ale pozostaje widoczny.

Po raporcie wróć do `web-build-slice`, jeśli potrzebna jest poprawka. Nie
modyfikuj kodu w tej samej fazie recenzji, bo zatarłoby to granicę dowodu.

## Dziennik i interfejs pluginu

W pakiecie delivery-chain użyj [delivery-view](../delivery-view/SKILL.md) do
zapisania rozpoczęcia i wyniku tego etapu w aktywnym wykonaniu. Dziennik jest
uzupełnieniem raportów; nie nadaje uprawnień ani nie zastępuje dowodów.
