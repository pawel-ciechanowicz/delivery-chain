---
name: delivery-view
description: Zapisuj i pokazuj przebieg wykonania delivery chaina jako lokalny dziennik oraz interaktywny graf HTML. Użyj podczas chaina lub przy przeglądzie jego historii; nie zastępuje testów ani bramek jakości.
---

# Delivery View

CLI jest w [scripts/delivery.py](../../scripts/delivery.py), względem katalogu
pluginu. Używaj absolutnej ścieżki po ustaleniu miejsca instalacji; projekt
użytkownika jest osobnym katalogiem, nigdy katalogiem cache pluginu.
Instrukcja poleceń i model danych: [journal.md](../../references/journal.md).

## Podczas pracy

1. Dla nowego wykonania uruchom `init --project ABS --run-id SLUG --title TYTUŁ`.
   Jeśli kontynuujesz istniejące wykonanie, użyj jego `--run`, nie twórz kopii.
2. Zapisz `event` przy rozpoczęciu etapu oraz po ustaleniu wyniku. Podaj krótką
   notatkę i ścieżkę raportu / polecenie z exit code. Nie zapisuj sekretów,
   pełnych logów, danych klientów ani poleceń zawierających tokeny.
3. Przed kontrolami zamroź kandydata przez `freeze`; `PASS` dla etapów kontroli
   wiąż z nim. Zmiana produktu wymaga nowego `freeze`, także po poprawkach.
4. Wpisuj rzeczywisty wynik: `FAIL`, `BLOCKED`, `PARTIAL` lub `SKIPPED` pozostają
   widoczne. Nie używaj PASS dla „etap się zakończył” ani przy brakujących dowodach.
5. Zapis decyzji `decision` wymaga rzeczywistej wypowiedzi użytkownika o tym
   kandydacie. Nie traktuj zgody na głos, plan albo wdrożenie jako APPROVED całego
   produktu. Skrypt kontroluje strukturę, nie autentyczność zgody.
6. Jeśli użytkownik zmienia kolejność (np. testy na produkcji), zapisz zakres
   tej decyzji w notatce. Odnotuj publikację w `deploy`, zachowując otwarte
   etapy odbioru. Widok pokaże odstępstwo; nie podmieniaj nim reguł chaina.

Każdy zapis generuje `index.html` w katalogu wykonania. Otwórz go przez narzędzie
podglądu plików lub przeglądarkę; przekaż klikalny link. Przy pracy pokaż adres
po inicjalizacji i po istotnych zmianach. Otwarte okno wymaga odświeżenia.
Nie uruchamiaj serwera, nie wdrażaj widoku ani nie instaluj pluginu bez potrzeby
wynikającej ze zlecenia. To interfejs po zdarzeniu, nie automatyczna telemetria.

## Odtworzenie starszej pracy

Użyj `init --mode reconstructed`. Odtwarzaj tylko potwierdzone zdarzenia z
raportów i rozmowy, podając źródło. `recorded_at` jest czasem rekonstrukcji,
nie czasem historycznego wykonania. Nie dopisuj brakującej zgody ani fikcyjnych
czasów. Wyraźnie zaznacz niepewność kolejności w notatce.

## Odczyt

`show` pokazuje źródłowy dziennik, `render` odbudowuje HTML po naprawie pliku
widoku. Suwak pokazuje stan po wybranym zdarzeniu; kliknięcie etapu odsłania
wynik i dowody. Stare wyniki zachowują historię i oznaczenie NIEAKTUALNE.
