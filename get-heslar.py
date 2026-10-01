#!/usr/bin/env python3
"""Stahování heslářů z AMČR přes OAI-PMH API.

Použití:
    get-heslar.py list
    get-heslar.py get <nazev-heslare> [-o soubor.txt]
"""
import argparse
import sys
import xml.etree.ElementTree as ET

import requests

endpoint = "https://api.aiscr.cz/2.2/oai"

NS = {
    "oai": "http://www.openarchives.org/OAI/2.0/",
    "amcr": "https://api.aiscr.cz/schema/amcr/2.2/",
}
PREFIX = "heslo:"


def oai_request(params):
    """Pošle dotaz na OAI-PMH endpoint a vrátí kořen XML; chyby OAI hlásí."""
    r = requests.get(endpoint, params=params, timeout=60)
    r.raise_for_status()
    root = ET.fromstring(r.content)
    err = root.find("oai:error", NS)
    if err is not None:
        sys.exit(f"Chyba API ({err.get('code')}): {(err.text or '').strip()}")
    return root


def oai_pages(params, container):
    """Projde všechny stránky odpovědi podle resumptionToken."""
    while True:
        root = oai_request(params)
        node = root.find(f"oai:{container}", NS)
        if node is None:
            return
        yield node
        token = node.find("oai:resumptionToken", NS)
        if token is None or not (token.text or "").strip():
            return
        params = {"verb": params["verb"], "resumptionToken": token.text.strip()}


def list_heslare():
    """Vrátí seznam (nazev, ceske jmeno) všech heslářů."""
    result = []
    for page in oai_pages({"verb": "ListSets"}, "ListSets"):
        for s in page.findall("oai:set", NS):
            spec = s.findtext("oai:setSpec", "", NS)
            if not spec.startswith(PREFIX):
                continue
            name = s.findtext("oai:setName", "", NS)
            # "Heslář: Počasí / Vocabulary: Weather" -> "Počasí"
            name = name.split(" / ")[0].removeprefix("Heslář:").strip()
            result.append((spec.removeprefix(PREFIX), name))
    return sorted(result)


def get_heslar(nazev):
    """Vrátí česká hesla daného hesláře seřazená podle pole razeni."""
    params = {
        "verb": "ListRecords",
        "metadataPrefix": "oai_amcr",
        "set": PREFIX + nazev,
    }
    hesla = []
    for page in oai_pages(params, "ListRecords"):
        for h in page.iterfind(".//amcr:amcr/amcr:heslo", NS):
            text = (h.findtext("amcr:heslo", "", NS)).strip()
            razeni = h.findtext("amcr:razeni", "", NS)
            if text:
                hesla.append((int(razeni) if razeni else 0, text))
    return [text for _, text in sorted(hesla)]


def main():
    p = argparse.ArgumentParser(description="Stahování heslářů z AMČR.")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list", help="vypíše dostupné hesláře")
    g = sub.add_parser("get", help="stáhne heslář do txt (heslo = řádek)")
    g.add_argument("nazev", help="název hesláře, např. pocasi")
    g.add_argument("-o", "--output", help="výstupní soubor (výchozí <nazev>.txt)")
    args = p.parse_args()

    if args.cmd == "list":
        for nazev, jmeno in list_heslare():
            print(f"{nazev:28} {jmeno}")
        return

    nazev = args.nazev.removeprefix(PREFIX)
    hesla = get_heslar(nazev)
    if not hesla:
        sys.exit(f"Heslář '{nazev}' nenalezen nebo je prázdný "
                 "(seznam: get-heslar.py list).")
    output = args.output or f"{nazev}.txt"
    with open(output, "w", encoding="utf-8") as f:
        f.write("\n".join(hesla) + "\n")
    print(f"{len(hesla)} hesel -> {output}")


if __name__ == "__main__":
    main()
