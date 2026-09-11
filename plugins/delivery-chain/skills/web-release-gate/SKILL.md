---
name: web-release-gate
description: Zbierz raporty jakości jednego kandydata aplikacji webowej, sprawdź bramkę maszynową, przygotuj zrozumiały raport gotowości i scenariusz ręczny, a następnie zapisz jawną decyzję człowieka. Użyj dopiero po testach, security review i code review; nie wdrażaj produktu.
---

# Web Release Gate

Ta faza nie dodaje kodu. Sprawdza, czy dowody wystarczają do decyzji człowieka.

## Gate maszynowy

1. Przeczytaj [kontrakt artefaktów](../safe-web-delivery/references/artifact-contract.md)
   i wszystkie pliki `docs/quality/00–05`.
2. Potwierdź, że raporty `02–05` dotyczą dokładnie tego samego kandydata oraz że
   kandydat nie zmienił się od czasu kontroli.
3. Uruchom:

```text
python3 "$DELIVERY_PLUGIN/skills/safe-web-delivery/scripts/check_release_gate.py" "$DELIVERY_PROJECT" --phase machine
```

4. Ręcznie sprawdź sens dowodów. Zielony skrypt waliduje kontrakt, ale nie
   dowodzi, że wybrane testy były adekwatne.

Jeśli bramka nie przechodzi, zapisz `06-release-readiness.md` ze statusem
`FAIL` lub `BLOCKED`, nazwij brak i wróć do właściwego etapu.

## Pakiet dla człowieka

Jeśli bramka przechodzi, utwórz:

- `06-release-readiness.md` ze statusem `PASS`;
- `07-human-approval.md` ze statusem `PENDING`.

Raport gotowości pokazuje prostym językiem: zakres, wynik każdej bramki,
findings `P2/P3`, ryzyko rezydualne, ograniczenia testów oraz 3–7 kroków testu
ręcznego. Kroki opisują widoczne zachowanie, np. „otwórz adres, wykonaj X,
zobacz Y”, a nie szczegóły kodu.

## Decyzja człowieka

Poproś o `APPROVED` albo `REJECTED` dla podanego identyfikatora. Człowiek nie
musi oceniać kodu; potwierdza zakres, działanie kluczowych ścieżek, treść,
wygląd i świadomą akceptację opisanych ryzyk.

Nie ustawiaj `APPROVED` na podstawie ciszy, „wygląda OK” bez wskazania
kandydata ani własnej oceny. Po jawnej decyzji zapisz osobę, datę, kandydat i
krótkie uzasadnienie w `07-human-approval.md`, a następnie uruchom:

```text
python3 "$DELIVERY_PLUGIN/skills/safe-web-delivery/scripts/check_release_gate.py" "$DELIVERY_PROJECT" --phase final
```

Zmiana kandydata unieważnia akceptację. Ustaw ponownie `PENDING` i przeprowadź
bramki zależne od kodu.

Nawet finalne `PASS` nie autoryzuje publikacji, wdrożenia, scalenia ani wysłania
wiadomości. To wymaga osobnej instrukcji użytkownika.

## Dziennik i interfejs pluginu

W pakiecie delivery-chain użyj [delivery-view](../delivery-view/SKILL.md) do
zapisania rozpoczęcia i wyniku tego etapu w aktywnym wykonaniu. Dziennik jest
uzupełnieniem raportów; nie nadaje uprawnień ani nie zastępuje dowodów.

W poleceniach `DELIVERY_PLUGIN` oznacza ustaloną absolutną ścieżkę katalogu
tego pluginu (zawierającego .codex-plugin), a `DELIVERY_PROJECT` katalog
projektu użytkownika. Ustaw je po rozpoznaniu środowiska; nie zakładaj istnienia
`.agents/skills` w projekcie. Skrypty i ich importy są częścią pakietu.
