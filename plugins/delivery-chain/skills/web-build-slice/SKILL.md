---
name: web-build-slice
description: Implementuj jeden mały, sprawdzalny fragment strony lub aplikacji webowej na podstawie gotowego briefu i planu, dodając adekwatne testy i zapis dowodów w build logu. Użyj podczas właściwej budowy lub naprawy findings; nie używaj do samej recenzji.
---

# Web Build Slice

Buduj pionowy fragment produktu, który można uruchomić i sprawdzić. Nie rozszerzaj
zakresu tylko dlatego, że dodatkowa funkcja wydaje się łatwa.

## Przed zmianą

1. Przeczytaj instrukcje repozytorium, `00-project-brief.md`,
   `01-delivery-plan.md` i [kontrakt artefaktów](../safe-web-delivery/references/artifact-contract.md).
2. Sprawdź stan Git i zachowaj niepowiązane zmiany użytkownika.
3. Nazwij jeden rezultat fragmentu, dotknięte pliki, kryteria odbioru i testy,
   które powinny zmienić wynik z czerwonego na zielony.

## Implementacja

- Najpierw dodaj albo doprecyzuj test odtwarzający wymagane zachowanie, jeśli
  rodzaj zmiany na to pozwala.
- Wprowadź najmniejszą spójną zmianę realizującą rezultat. Zachowaj istniejące
  wzorce repozytorium, zamiast równolegle tworzyć nową architekturę.
- Obsłuż stan ładowania, pusty, sukces i błąd tam, gdzie użytkownik może je
  zobaczyć.
- Waliduj dane na granicy zaufania. Sekretów i uprawnień nie przenoś do klienta.
- Nie usuwaj testu, nie rozluźniaj asercji i nie wyłączaj reguły bez zapisania
  konkretnej przyczyny oraz wpływu na gate.
- Uruchom testy skupione na fragmencie oraz wymagane szybkie kontrole
  repozytorium. Napraw przyczynę, nie tylko symptom.

## Artefakt

Aktualizuj `docs/quality/02-build-log.md`. Dla każdego fragmentu zapisz:

- rezultat i powiązane kryteria odbioru;
- zmienione zachowanie i najważniejsze pliki;
- dokładne polecenia testowe z wynikiem;
- nieudane próby, jeśli zmieniły decyzję;
- znane ograniczenia i następny krok.

Podczas pracy używaj `status: IN_PROGRESS` i `candidate: unfrozen`. Gdy zakres
kandydata jest gotowy do pełnych bramek, wylicz identyfikator poleceniem:

```text
python3 "$DELIVERY_PLUGIN/skills/safe-web-delivery/scripts/fingerprint_candidate.py" "$DELIVERY_PROJECT"
```

Wpisz wynik do raportu i ustaw `PASS` tylko po przejściu testów fragmentów.
Każda późniejsza zmiana wymaga nowego identyfikatora.


## Dziennik i interfejs pluginu

W pakiecie delivery-chain użyj [delivery-view](../delivery-view/SKILL.md) do
zapisania rozpoczęcia i wyniku tego etapu w aktywnym wykonaniu. Dziennik jest
uzupełnieniem raportów; nie nadaje uprawnień ani nie zastępuje dowodów.

W poleceniach `DELIVERY_PLUGIN` oznacza ustaloną absolutną ścieżkę katalogu
tego pluginu (zawierającego .codex-plugin), a `DELIVERY_PROJECT` katalog
projektu użytkownika. Ustaw je po rozpoznaniu środowiska; nie zakładaj istnienia
`.agents/skills` w projekcie. Skrypty i ich importy są częścią pakietu.
