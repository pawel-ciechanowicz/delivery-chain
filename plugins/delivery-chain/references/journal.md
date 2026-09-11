# Kontrakt dziennika v1

Python 3.10+ na macOS/Linux, bez zależności sieciowych. `CLI` poniżej oznacza
absolutną ścieżkę `scripts/delivery.py` w pluginie; `RUN` to katalog zwrócony
przez init (bez końcowego index.html).

```bash
python3 CLI init --project /abs/project --run-id lesson-01 --title 'Lekcja 01'
python3 CLI event --run RUN --stage plan --execution running
python3 CLI event --run RUN --stage plan --outcome PASS --evidence 'docs/quality/01-delivery-plan.md'
python3 CLI event --run RUN --stage build --execution running
python3 CLI freeze --run RUN --note 'Kod gotowy do kontroli'
python3 CLI event --run RUN --stage build --outcome PASS --evidence 'npm test: exit 0; docs/quality/02-build-log.md'
python3 CLI event --run RUN --stage review --outcome FAIL --evidence 'docs/quality/05-code-review.md' --note 'Błąd ponowienia'
python3 CLI render --run RUN
python3 CLI show --run RUN
```

Etapy: plan, build, freeze (osobna komenda), verify, security, review, machine,
human (osobna komenda), final, deploy, smoke. Zamrożenie bez `--candidate`
oblicza fingerprint katalogu projektu dołączonym skryptem. Można podać
`--candidate git:SHA` lub `snapshot:sha256:HASH` tylko z rzeczywistego źródła.

Wykonanie: pending/running/done. Wynik: NONE/PASS/FAIL/BLOCKED/PARTIAL/SKIPPED.
Zakończenie etapu nie oznacza PASS. Brak eventu oznacza pending/NONE.
Każdy event jest dopisywany pod blokadą pliku, a JSON i HTML zapisywane przez
atomic replace. JSON jest źródłem prawdy: po awarii renderera uruchom render.
Identyfikator run nie może nadpisać istniejącego katalogu. Powtórzenia etapów
pozostają w historii. Cofnięcie suwaka nie modyfikuje dziennika.

`decision --run RUN --decision APPROVED|REJECTED --actor IMIĘ --statement
'Dosłowna decyzja użytkownika' --candidate ID --evidence 'źródło decyzji'`
rejestruje osobno decyzję o kandydacie. CLI nie uwierzytelnia aktora; wymaga
rzetelnej obsługi przez agenta. Nie jest narzędziem do zbierania podpisów.

`machine PASS` wymaga build/verify/security/review PASS dla tego samego
kandydata. `final PASS` wymaga dodatkowo machine PASS i human APPROVED.
To kontrola spójności dziennika. Wykonaj też rzeczywisty check_release_gate.py
z raportami, nie używaj dziennika jako zamiennika bramki ani niezależnego review.

Nowy freeze oznacza poprzednie wyniki dla innych kandydatów jako stale.
Plan pozostaje niezależny od kandydata. Publikacja przed final/approval jest
rejestrowana jako odstępstwo, nigdy jako automatyczne zamknięcie chaina.

## Lokalizacja i przenoszenie

`PROJECT/docs/quality/delivery-runs/RUN-ID/{run.json,index.html,.lock}`.
Dziennik i HTML są wyłączone z fingerprintu jako docs/quality. Nie przenoś ich
w zakres hashowanego produktu. Snapshot pomija także test-results,
playwright-report, .vercel i *.tsbuildinfo. Plik run.json zawiera lokalną ścieżkę
projektu, HTML jej nie eksportuje. Przy przenoszeniu między komputerami do
oglądania wystarczy index.html; kontynuowanie starego run wymaga prawidłowej
ścieżki project w JSON. Jest to jawny lokalny format, nie plik odporny na edycję.

Wszystkie notatki i evidence są wyświetlane jako tekst, bez wykonywania HTML
ani otwierania adresów. Widok nie pobiera żadnych zasobów z sieci.

Ponowienie build unieważnia późniejsze kontrole; ponowienie verify/security/review
unieważnia machine/human/final także dla tego samego hasha. Powtórny freeze
tego samego hasha nie odświeża starych zgód. Wykonaj ponownie właściwe bramki.
