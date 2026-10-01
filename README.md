# get-heslar

Stahování heslářů z AMČR přes
[OAI-PMH API](https://arup-cas.github.io/aiscr-api-home/oai-pmh/)
(endpoint `https://api.aiscr.cz/2.2/oai`). Hesláře jsou veřejné, přihlášení
není potřeba.

## Požadavky

Python 3.9+ a knihovna `requests`.

## Použití

Seznam dostupných heslářů (název a český popis):

```
python3 get-heslar.py list
```

Stažení hesláře do `<nazev>.txt` v aktuálním adresáři:

```
python3 get-heslar.py get pocasi
python3 get-heslar.py get heslo:obdobi -o obdobi.txt
```

## Výstup

Textový soubor v UTF-8, jedno heslo na řádek. Obsahuje jen česká hesla
(pole `heslo`), seřazená podle pole `razeni`, tedy v pořadí jako v AMČR.
Hierarchie heslářů se nezachovává, seznam je plochý.
