# Kontrakt artefaktów jakości

Przeczytaj ten plik przed utworzeniem lub oceną zawartości `docs/quality/`.

## Statusy

- `IN_PROGRESS` — etap trwa i nie otwiera następnej bramki.
- `PASS` — wszystkie wymagane kontrole etapu mają dowód.
- `FAIL` — wynik przeczy wymaganiu albo istnieje nieusunięty blocker.
- `BLOCKED` — kontroli nie da się wykonać bez brakującej decyzji, dostępu lub
  środowiska.
- `NOT_APPLICABLE` — dozwolone tylko dla pojedynczej kontroli z uzasadnieniem;
  nie jest statusem całego raportu.
- `PENDING`, `APPROVED`, `REJECTED` — wyłącznie decyzja człowieka w
  `07-human-approval.md`.

Brak wyniku i `SKIPPED` nie oznaczają `PASS`.

## Frontmatter

Każdy raport zaczyna się od:

```yaml
---
artifact: quality/verification
schema_version: 1
status: IN_PROGRESS
candidate: unfrozen
updated: YYYY-MM-DD
---
```

Pliki `00` i `01` mogą używać `candidate: planning`. Od `02` do `07` kandydat
ma postać:

- `git:<7-40 znaków SHA>`; albo
- `snapshot:sha256:<64 znaki hex>`.

Wartości `TODO`, `TBD`, puste pola i przykładowe hashe nie przechodzą bramki.

## Standard czytelnego raportu

Każdy raport musi zaczynać się od sekcji `## W skrócie`, zawierającej:

- decyzję etapu w jednym zdaniu;
- maksymalnie pięć najważniejszych faktów;
- blokery i następny krok.

Dalej podawaj tabelę dowodów. Każdy pozytywny wynik musi wskazywać co najmniej
jedno z poniższych:

- dokładne polecenie i kod wyjścia;
- scenariusz, środowisko i obserwowany wynik;
- ścieżkę do zrzutu, logu lub raportu narzędzia;
- plik i linie kodu potwierdzające właściwość statyczną.

Nie wklejaj wielkich logów do raportu. Zapisz ich lokalizację i krótki fragment
wyjaśniający decyzję. `PASS` nie może opierać się na „wygląda dobrze”, samym
istnieniu testu albo braku znalezionych wyników z nieadekwatnego wyszukiwania.

## Wymagane pliki i sekcje

### `00-project-brief.md`

Frontmatter: `artifact: quality/project-brief`.

Sekcje: `W skrócie`, `Cel i odbiorca`, `Zakres`, `Kryteria odbioru`,
`Ryzyka`, `Decyzje człowieka`.

### `01-delivery-plan.md`

Frontmatter: `artifact: quality/delivery-plan`.

Sekcje: `W skrócie`, `Plan małych etapów`, `Macierz testów`,
`Plan bezpieczeństwa`, `Definition of Done`.

### `02-build-log.md`

Frontmatter: `artifact: quality/build-log`.

Sekcje: `W skrócie`, `Zmiany`, `Testy podczas budowy`, `Znane ograniczenia`.
Dodawaj kolejne fragmenty chronologicznie. Nie usuwaj historii nieudanych prób,
jeśli wpłynęły na decyzję.

### `03-verification-report.md`

Frontmatter: `artifact: quality/verification`.

Sekcje: `W skrócie`, `Dowody techniczne`, `Scenariusze akceptacyjne`, `Evale`,
`Czego ten raport nie dowodzi`.

### `04-security-review.md`

Frontmatter: `artifact: quality/security-review`.

Sekcje: `W skrócie`, `Threat model`, `Findings`, `Dowody`, `Ryzyko rezydualne`.

### `05-code-review.md`

Frontmatter: `artifact: quality/code-review`.

Pole `reviewer_mode` musi mieć wartość `independent-agent` albo `fresh-task`,
aby raport mógł przejść release gate. `separate-pass` i `author-self-review` są
pomocniczą kontrolą autora, nie niezależną recenzją.

Sekcje: `W skrócie`, `Findings`, `Dowody`, `Utrzymywalność`,
`Ograniczenia recenzji`.

### `06-release-readiness.md`

Frontmatter: `artifact: quality/release-readiness`.

Sekcje: `W skrócie`, `Podsumowanie bramek`, `Blockery`, `Ryzyko rezydualne`,
`Scenariusz testu człowieka`.

### `07-human-approval.md`

Frontmatter rozszerzone o osobę i czas:

```yaml
---
artifact: quality/human-approval
schema_version: 1
status: PENDING
candidate: snapshot:sha256:...
updated: YYYY-MM-DD
approved_by:
approved_at:
---
```

Sekcje: `W skrócie`, `Kandydat`, `Kontrole ręczne`, `Decyzja`.

Agent przygotowuje plik ze statusem `PENDING`. Może zmienić go na `APPROVED`
albo `REJECTED` tylko po jawnej decyzji użytkownika dotyczącej tego kandydata.
Po zmianie kandydata wraca do `PENDING`, a pola zatwierdzenia są czyszczone.

## Findings i priorytety

- `P0` — aktywna możliwość utraty danych, przejęcia systemu, poważnego kosztu
  lub niedziałający główny produkt. Twardy blocker.
- `P1` — prawdopodobny istotny błąd, luka albo regresja głównej funkcji. Twardy
  blocker.
- `P2` — ograniczony błąd lub istotny dług, który wymaga naprawy albo jawnej
  decyzji przed wydaniem.
- `P3` — małe usprawnienie, które nie blokuje wydania.

Finding podaje: priorytet, obserwowalny skutek, warunki wystąpienia, dowód,
lokalizację oraz najwęższy sensowny kierunek naprawy. Nie raportuj czysto
stylistycznych preferencji jako błędów.

## Unieważnienie dowodów

Zmiana kodu, konfiguracji, zależności, migracji, polityk bezpieczeństwa albo
istotnych assetów tworzy nowego kandydata. Raporty starego kandydata zachowaj
jako historię albo nadpisz dopiero po ponownym wykonaniu kontroli. Nigdy nie
zmieniaj samego pola `candidate`, pozostawiając stare wyniki.
