---
name: web-spec-and-plan
description: "Zdefiniuj publiczną stronę lub aplikację webową przed implementacją: cel, odbiorcę, kryteria odbioru, zakres, ryzyka, threat model, plan małych etapów i macierz testów. Użyj przy rozpoczęciu produktu albo istotnej zmianie zakresu."
---

# Web Spec and Plan

Przygotuj wystarczający kontrakt do budowy i oceny produktu. Nie implementuj
funkcji w tym etapie.

## Wejście

- instrukcje repozytorium i istniejąca dokumentacja;
- opis celu użytkownika;
- aktualny kod, jeśli projekt już istnieje;
- [kontrakt artefaktów](../safe-web-delivery/references/artifact-contract.md).

## Workflow

1. Oddziel informacje potwierdzone od założeń. Pytaj tylko o brak, który
   materialnie zmienia produkt, dane, bezpieczeństwo, koszt albo publikację.
2. Zapisz odbiorcę, problem, podstawową ścieżkę i mierzalny wynik. Dodaj jawny
   `out of scope`.
3. Sformułuj kryteria odbioru jako obserwowalne scenariusze, najlepiej
   `Given / When / Then`. Uwzględnij stan pusty, błąd i ponowienie.
4. Ustal profil ryzyka. Zmapuj aktywa, dane, role użytkowników, granice zaufania,
   integracje oraz możliwe nadużycia.
5. Podziel pracę na małe etapy, z których każdy kończy się funkcją możliwą do
   uruchomienia i sprawdzenia.
6. Zbuduj macierz testów proporcjonalną do ryzyka: statyczne, unit, integracja,
   end-to-end, wizualne/responsive, dostępność, wydajność, odporność,
   bezpieczeństwo oraz evale zachowania. Oznacz `NOT_APPLICABLE` tylko z
   uzasadnieniem.
7. Zapisz `docs/quality/00-project-brief.md` i
   `docs/quality/01-delivery-plan.md` według kontraktu.

## Gate

Ustaw `PASS` tylko wtedy, gdy każda funkcja wysokiego znaczenia ma kryterium
odbioru, plan testu i właściciela decyzji. Ustaw `BLOCKED`, jeśli brakująca
decyzja człowieka zmieniłaby architekturę, dane, płatność, prywatność albo
publiczny zakres.

W odpowiedzi pokaż wyłącznie wynik, założenia o największym wpływie, blokery i
najbliższy mały etap.

## Dziennik i interfejs pluginu

W pakiecie delivery-chain użyj [delivery-view](../delivery-view/SKILL.md) do
zapisania rozpoczęcia i wyniku tego etapu w aktywnym wykonaniu. Dziennik jest
uzupełnieniem raportów; nie nadaje uprawnień ani nie zastępuje dowodów.
