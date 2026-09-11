---
name: web-security-review
description: "Oceń bezpieczeństwo zamrożonego kandydata strony lub aplikacji webowej: threat model, sekrety, zależności, walidację, auth, dane, granice klient-serwer, konfigurację i nadużycia. Użyj przed publicznym wydaniem albo po zmianie powierzchni ataku; nie nazywaj skanu gwarancją bezpieczeństwa."
---

# Web Security Review

Przeprowadź kontrolę read-only dokładnego kandydata. Nie naprawiaj findings w
tej fazie; naprawa tworzy nowego kandydata i wymaga ponownej kontroli.

## Workflow

1. Przeczytaj brief, plan bezpieczeństwa, aktualny kod, konfigurację wdrożenia,
   zależności i [kontrakt artefaktów](../safe-web-delivery/references/artifact-contract.md).
2. Potwierdź identyfikator kandydata i profil ryzyka.
3. Zaktualizuj threat model na podstawie kodu: aktywa, aktorzy, dane, punkty
   wejścia, granice zaufania, integracje i możliwości nadużycia.
4. Wykonaj dostępne skany sekretów, zależności i analizę statyczną. Zapisz
   dokładny zakres oraz ograniczenia narzędzi.
5. Sprawdź ręcznie obszary adekwatne do produktu:
   - rozdzielenie klienta i serwera oraz ekspozycję sekretów;
   - uwierzytelnianie, autoryzację i izolację danych między użytkownikami;
   - walidację wejść i wyjść, XSS, injection, CSRF, SSRF, redirecty i uploady;
   - cookies, sesje, CORS, CSP i pozostałe nagłówki;
   - rate limiting, brute force, kosztowe nadużycia i limity API;
   - logi, analitykę, dane osobowe, retencję i komunikaty błędów;
   - supply chain, skrypty buildowe i zewnętrzne zasoby;
   - bezpieczne zachowanie przy awarii zależności.
6. Dla `high-risk` wskaż wymagany przegląd specjalistyczny, którego obecne
   narzędzia nie zastępują.

## Raport i gate

Zapisz `docs/quality/04-security-review.md` z findings `P0–P3`, dowodami i
ryzykiem rezydualnym. `P0`, `P1`, znaleziony sekret oraz niewyjaśniona kontrola
dostępu są twardym `FAIL`. `P2` wymaga naprawy albo jawnej decyzji opisanej w
release gate; nie może zniknąć z raportu.

Używaj sformułowania „nie znaleziono w sprawdzonym zakresie”, nigdy „produkt
jest bezpieczny”. Brak narzędzia nie jest pozytywnym wynikiem.

## Dziennik i interfejs pluginu

W pakiecie delivery-chain użyj [delivery-view](../delivery-view/SKILL.md) do
zapisania rozpoczęcia i wyniku tego etapu w aktywnym wykonaniu. Dziennik jest
uzupełnieniem raportów; nie nadaje uprawnień ani nie zastępuje dowodów.
