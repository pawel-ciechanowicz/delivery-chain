---
name: web-verify
description: Zweryfikuj zamrożonego kandydata strony lub aplikacji webowej przez testy statyczne, unit, integracyjne, end-to-end, wizualne, responsive, dostępnościowe, wydajnościowe i evale produktu. Użyj przed wydaniem lub po naprawie; nie zastępuj brakujących dowodów opinią.
---

# Web Verify

Udowodnij obserwowalne zachowanie dokładnego kandydata. Nie zmieniaj kodu w
trakcie tej fazy. Jeśli znajdziesz błąd, zapisz `FAIL` i wróć do etapu budowy.

## Przygotowanie

1. Przeczytaj instrukcje repozytorium, brief, plan, build log i
   [kontrakt artefaktów](../safe-web-delivery/references/artifact-contract.md).
2. Potwierdź identyfikator kandydata. Jeśli kod zmienił się po zamrożeniu,
   zatrzymaj weryfikację.
3. Odkryj polecenia i środowisko z repozytorium; nie zgaduj nazw skryptów.

## Warstwy dowodu

Wykonaj adekwatne kontrole i zapisz jawne `NOT_APPLICABLE` dla niepasujących:

- format, lint, typecheck i produkcyjny build;
- testy unit oraz integracyjne zmienionej logiki i granic danych;
- end-to-end dla każdej krytycznej ścieżki, w tym błędu i ponowienia;
- przegląd działającej aplikacji w realnej przeglądarce;
- szerokości mobile, tablet i desktop oraz brak overflow;
- klawiatura, fokus, etykiety, kontrast i automatyczne a11y;
- wydajność i rozmiar zasobów względem budżetu z planu;
- błędne dane, wolna sieć, przerwanie żądania i bezpieczne komunikaty błędu;
- obsługiwane przeglądarki;
- scenariusze akceptacyjne z `00-project-brief.md`.

## Evale

Dla każdego zachowania trudnego do objęcia zwykłą asercją utwórz powtarzalny
zestaw: wejście, oczekiwany wynik, grader lub regułę, próg i wynik bieżący.
Dla funkcji AI uwzględnij typowe przypadki, krawędzie, regresje, niebezpieczne
wejścia i stabilność formatu. Zapisz seed, model i konfigurację, jeśli mają
wpływ. Jeśli produkt nie używa AI, evale nadal mogą być tabelą scenariuszy
produktowych.

## Raport

Zapisz `docs/quality/03-verification-report.md`. Każdy wiersz ma kontrolę,
oczekiwanie, polecenie lub scenariusz, wynik i lokalizację dowodu. Ustaw `PASS`
tylko wtedy, gdy wszystkie kryteria wysokiego znaczenia mają pozytywny dowód,
a brakujące kontrole są rzeczywiście nieadekwatne i uzasadnione.

Sekcja `Czego ten raport nie dowodzi` jest obowiązkowa. Testy nie są dowodem
zachowań, których nie wykonano.


## Dziennik i interfejs pluginu

W pakiecie delivery-chain użyj [delivery-view](../delivery-view/SKILL.md) do
zapisania rozpoczęcia i wyniku tego etapu w aktywnym wykonaniu. Dziennik jest
uzupełnieniem raportów; nie nadaje uprawnień ani nie zastępuje dowodów.
