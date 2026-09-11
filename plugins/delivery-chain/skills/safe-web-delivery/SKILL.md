---
name: safe-web-delivery
description: Prowadź publiczną stronę lub aplikację webową przez pełny chain specyfikacji, małych wdrożeń, testów, evali, security review, code review i ludzkiej akceptacji. Użyj przy budowie lub ocenie kandydata produkcyjnego; nie uruchamiaj pełnego chainu dla pojedynczego wyjaśnienia albo jawnie jednorazowego prototypu.
---

# Safe Web Delivery

Koordynuj budowę tak, aby gotowość wynikała z dowodów zapisanych w
`docs/quality/`, a nie z pewności agenta.

## Najpierw

1. Przeczytaj instrukcje repozytorium oraz istniejące pliki produktu, designu i
   jakości.
2. Przeczytaj [kontrakt artefaktów](references/artifact-contract.md).
3. Ustal aktualny etap na podstawie plików i kodu. Nie powtarzaj zaliczonych
   etapów, jeśli dowody nadal dotyczą aktualnego zakresu i kandydata.
4. Wybierz profil `prototype`, `public-standard` albo `high-risk`. Publiczny
   produkt domyślnie ma profil `public-standard`. Logowanie, płatności, dane
   osobowe, dzieci, mikrofon/kamera, uploady albo działania AI podnoszą profil.

## Chain

Stosuj instrukcje sibling skills w tej kolejności:

1. `../web-spec-and-plan/SKILL.md`
2. `../web-build-slice/SKILL.md`
3. po zamrożeniu kandydata:
   - `../web-verify/SKILL.md`
   - `../web-security-review/SKILL.md`
   - `../web-code-review/SKILL.md`
4. `../web-release-gate/SKILL.md`

Trzy kontrole kandydata mogą działać równolegle wyłącznie wtedy, gdy
delegowanie jest dostępne i użytkownik je autoryzował. W przeciwnym razie
wykonaj je kolejno. Dla release gate code review musi powstać w świeżym zadaniu
albo przez niezależnego agenta. Self-review może pomóc podczas budowy, ale nie
jest bramką wydania.

## Reguły przejścia

- Nie implementuj przed gotowym briefem i planem, poza bezpieczną diagnostyką.
- Buduj małymi fragmentami. Po każdym uruchom testy adekwatne do zmiany.
- Przed pełną weryfikacją zamroź kandydat jako `git:<sha>` albo
  `snapshot:sha256:<hash>` przy użyciu dołączonego skryptu.
- Wszystkie raporty kandydata muszą wskazywać ten sam identyfikator.
- Każda zmiana kodu, konfiguracji, zależności lub istotnych zasobów unieważnia
  raporty od `02-build-log.md` wzwyż. Zamroź nowego kandydata i powtórz bramki.
- `FAIL`, `BLOCKED`, `SKIPPED`, brak dowodu albo nieuzasadnione
  `NOT_APPLICABLE` zatrzymują chain.
- Nie ukrywaj błędów przez osłabienie testu, wyłączenie reguły, catch-all,
  fallback bez sygnału albo zmianę kryterium po zobaczeniu wyniku.
- Nie instaluj narzędzia tylko dlatego, że znajduje się na checkliście. Najpierw
  nazwij brak dowodu, który narzędzie ma uzupełnić.

## Zakończenie

Przekaż człowiekowi `06-release-readiness.md` i krótki scenariusz ręczny.
Nigdy nie ustawiaj `APPROVED` w jego imieniu. Zatwierdzenie dotyczy dokładnego
identyfikatora kandydata.

Nie publikuj, nie wdrażaj, nie scalaj i nie wysyłaj zmian bez osobnej jawnej
instrukcji użytkownika. Po akceptacji poinformuj, że produkt jest kandydatem do
wdrożenia, a nie że został wdrożony.

## Narzędzia deterministyczne

- Zamrożenie snapshotu bez commita:
  `python3 "$DELIVERY_PLUGIN/skills/safe-web-delivery/scripts/fingerprint_candidate.py" "$DELIVERY_PROJECT"`
- Kontrola raportów maszynowych:
  `python3 "$DELIVERY_PLUGIN/skills/safe-web-delivery/scripts/check_release_gate.py" "$DELIVERY_PROJECT" --phase machine`
- Kontrola finalna po decyzji człowieka:
  `python3 "$DELIVERY_PLUGIN/skills/safe-web-delivery/scripts/check_release_gate.py" "$DELIVERY_PROJECT" --phase final`

## Dziennik i interfejs pluginu

W pakiecie delivery-chain użyj [delivery-view](../delivery-view/SKILL.md) do
zapisania rozpoczęcia i wyniku tego etapu w aktywnym wykonaniu. Dziennik jest
uzupełnieniem raportów; nie nadaje uprawnień ani nie zastępuje dowodów.

Rozpoczynając nowe wykonanie, zainicjalizuj dziennik delivery-view. Po każdym
etapie zapisz zdarzenie i zaktualizuj podgląd. Używaj wspólnego run dla agentów;
wyniki kontroli muszą wskazywać zamrożonego kandydata.

W poleceniach `DELIVERY_PLUGIN` oznacza ustaloną absolutną ścieżkę katalogu
tego pluginu (zawierającego .codex-plugin), a `DELIVERY_PROJECT` katalog
projektu użytkownika. Ustaw je po rozpoznaniu środowiska; nie zakładaj istnienia
`.agents/skills` w projekcie. Skrypty i ich importy są częścią pakietu.
