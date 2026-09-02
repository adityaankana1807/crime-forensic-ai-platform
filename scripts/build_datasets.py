"""Build compact research datasets from verified public sources.

The saved files are deliberately small enough for a paper prototype repository.
They preserve provenance in data/processed/dataset_manifest.json.
"""

from __future__ import annotations

import csv
import json
import shutil
import sys
import urllib.error
import urllib.request
from io import StringIO
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "processed"
PUBLIC = ROOT / "public" / "data"


INDIA_CYBERCRIME_ROWS = [
    ("Andhra Pradesh", 1875, 2341, 2341),
    ("Arunachal Pradesh", 47, 14, 24),
    ("Assam", 4846, 1733, 909),
    ("Bihar", 1413, 1621, 4450),
    ("Chhattisgarh", 352, 439, 473),
    ("Goa", 36, 90, 86),
    ("Gujarat", 1536, 1417, 1995),
    ("Haryana", 622, 681, 751),
    ("Himachal Pradesh", 70, 77, 127),
    ("Jharkhand", 953, 967, 1079),
    ("Karnataka", 8136, 12556, 21889),
    ("Kerala", 626, 773, 3295),
    ("Madhya Pradesh", 589, 826, 685),
    ("Maharashtra", 5562, 8249, 8103),
    ("Manipur", 67, 18, 3),
    ("Meghalaya", 107, 75, 64),
    ("Mizoram", 30, 1, 31),
    ("Nagaland", 8, 4, 2),
    ("Odisha", 2037, 1983, 2348),
    ("Punjab", 551, 697, 511),
    ("Rajasthan", 1504, 1833, 2435),
    ("Sikkim", 0, 26, 12),
    ("Tamil Nadu", 1076, 2082, 4121),
    ("Telangana", 10303, 15297, 18236),
    ("Tripura", 24, 30, 36),
    ("Uttar Pradesh", 8829, 10117, 10794),
    ("Uttarakhand", 718, 559, 494),
    ("West Bengal", 513, 401, 309),
    ("A&N Islands", 8, 28, 47),
    ("Chandigarh", 15, 27, 23),
    ("D&N Haveli and Daman & Diu", 5, 5, 6),
    ("Delhi", 356, 685, 407),
    ("Jammu & Kashmir", 154, 173, 185),
    ("Ladakh", 5, 3, 1),
    ("Lakshadweep", 1, 1, 1),
    ("Puducherry", 0, 64, 147),
]


FORENSIC_CAPACITY_ROWS = [
    ("Arunachal Pradesh", 0.865, 0.865, "0"),
    ("Assam", 1.125, 1.125, "0"),
    ("Chhattisgarh", 2.183, 3.683, "3,51,59,931"),
    ("Gujarat", 0.6075, 1.8225, "1,15,57,661"),
    ("Himachal Pradesh", 0.0, 7.29, "7,29,00,000"),
    ("Jharkhand", 1.6625, 4.9875, "3,26,79,489"),
    ("Karnataka", 0.0, 13.96, "0"),
    ("Kerala", 1.625, 6.455, "4,82,93,502"),
    ("Meghalaya", 1.7715, 1.9365, "1,77,15,000"),
    ("Mizoram", 0.0, 4.19, "4,19,00,000"),
    ("Nagaland", 2.725, 5.45, "5,45,00,000"),
    ("Odisha", 3.1425, 9.4275, "9,30,60,819"),
    ("Punjab", 0.0, 7.98, "3,99,00,000"),
    ("Rajasthan", 0.0, 6.28, "6,27,96,750"),
    ("Telangana", 2.98, 2.98, "1,76,49,403"),
    ("Tripura", 0.0, 2.11, "2,11,00,000"),
    ("Uttar Pradesh", 0.0, 7.75, "7,06,81,508"),
    ("Uttarakhand", 2.48, 2.48, "2,48,00,000"),
    ("A & N Islands", 2.18, 2.28, "1,59,68,474"),
    ("Puducherry", 3.395, 6.9, "6,05,33,389"),
]


SOURCES = {
    "pib_cybercrime": "https://www.pib.gov.in/PressReleasePage.aspx?PRID=2241339&lang=1&reg=3",
    "world_bank_homicide": "https://api.worldbank.org/v2/country/IND;USA;GBR;BRA;ZAF;JPN/indicator/VC.IHR.PSRC.P5?format=json&per_page=20000",
    "uk_police_last_updated": "https://data.police.uk/api/crime-last-updated",
    "uk_police_street": "https://data.police.uk/api/crimes-street/all-crime?lat=51.5074&lng=-0.1278",
    "bjs_nibrs_violent_incidents": "https://api.ojp.gov/bjsdataset/v1/r32q-bdaw.csv?%24limit=250",
}


def fetch_json(url: str, timeout: int = 25) -> Any:
    request = urllib.request.Request(url, headers={"User-Agent": "crime-ai-research-prototype/1.0"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_text(url: str, timeout: int = 25) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "crime-ai-research-prototype/1.0"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8")


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def build_india_cybercrime() -> dict[str, Any]:
    rows = []
    for state, y2021, y2022, y2023 in INDIA_CYBERCRIME_ROWS:
        change = None if y2021 == 0 else round(((y2023 - y2021) / y2021) * 100, 2)
        rows.append(
            {
                "state_ut": state,
                "cases_2021": y2021,
                "cases_2022": y2022,
                "cases_2023": y2023,
                "pct_change_2021_2023": change,
                "source": "PIB release citing NCRB Crime in India",
            }
        )
    path = OUT / "india_cybercrime_ncrb_pib_2021_2023.csv"
    write_csv(path, list(rows[0]), rows)
    return dataset_entry(
        path,
        "India NCRB cybercrime cases by State/UT, 2021-2023",
        SOURCES["pib_cybercrime"],
        "State/UT",
        "Public aggregate table from PIB release citing NCRB Crime in India. It cannot identify incidents, suspects, victims, or forensic artifacts.",
        len(rows),
    )


def build_india_forensic_capacity() -> dict[str, Any]:
    rows = []
    for state, recent, total, uc in FORENSIC_CAPACITY_ROWS:
        rows.append(
            {
                "state_ut": state,
                "release_fy_2022_23_to_2024_25_crore": recent,
                "release_since_fy_2018_19_crore": total,
                "uc_received_gfr_12c": uc,
                "scheme": "Strengthening of DNA Analysis and Cyber Forensic Capacities in State FSLs",
                "source": "PIB release, Annexure-II",
            }
        )
    path = OUT / "india_cyber_forensic_capacity_pib_2022_2025.csv"
    write_csv(path, list(rows[0]), rows)
    return dataset_entry(
        path,
        "India cyber-forensic capacity funding by State/UT",
        SOURCES["pib_cybercrime"],
        "State/UT",
        "Funding/capacity proxy only. It does not measure lab throughput, backlog, tool quality, or conviction impact.",
        len(rows),
    )


def build_world_bank_homicide() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    try:
        payload = fetch_json(SOURCES["world_bank_homicide"])
        records = payload[1] if isinstance(payload, list) and len(payload) > 1 else []
        for item in records:
            value = item.get("value")
            if value is None:
                continue
            rows.append(
                {
                    "country_iso3": item.get("countryiso3code"),
                    "country": item.get("country", {}).get("value"),
                    "year": item.get("date"),
                    "intentional_homicide_rate_per_100k": value,
                    "source": "World Bank WDI indicator VC.IHR.PSRC.P5, sourced from UNODC",
                }
            )
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        rows.append({"country_iso3": "FETCH_FAILED", "country": str(exc), "year": "", "intentional_homicide_rate_per_100k": "", "source": SOURCES["world_bank_homicide"]})
    path = OUT / "global_homicide_wb_unodc_selected_countries.csv"
    write_csv(path, ["country_iso3", "country", "year", "intentional_homicide_rate_per_100k", "source"], rows)
    return dataset_entry(
        path,
        "Global intentional homicide rates for selected countries",
        SOURCES["world_bank_homicide"],
        "Country-year",
        "Cross-country aggregate rates support macro comparison only. They do not encode modus operandi, language, evidence, or offender linkage.",
        len(rows),
    )


def build_uk_police_sample() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    date = ""
    try:
        date = fetch_json(SOURCES["uk_police_last_updated"]).get("date", "")
        payload = fetch_json(f"{SOURCES['uk_police_street']}&date={date[:7]}")
        for item in payload[:250]:
            rows.append(
                {
                    "category": item.get("category"),
                    "month": item.get("month"),
                    "latitude": item.get("location", {}).get("latitude"),
                    "longitude": item.get("location", {}).get("longitude"),
                    "street": item.get("location", {}).get("street", {}).get("name"),
                    "outcome": (item.get("outcome_status") or {}).get("category"),
                    "source": "UK Police street-level API sample around central London",
                }
            )
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        rows.append({"category": "FETCH_FAILED", "month": date, "latitude": "", "longitude": "", "street": str(exc), "outcome": "", "source": SOURCES["uk_police_street"]})
    path = OUT / "uk_police_london_street_crime_sample.csv"
    write_csv(path, ["category", "month", "latitude", "longitude", "street", "outcome", "source"], rows)
    return dataset_entry(
        path,
        "UK Police street-level crime sample, central London",
        SOURCES["uk_police_street"],
        "Street-month sample",
        "Useful for schema comparison and geospatial UI testing. Do not treat a small coordinate sample as a city-wide crime baseline.",
        len(rows),
    )


def build_bjs_nibrs_sample() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    try:
        text = fetch_text(SOURCES["bjs_nibrs_violent_incidents"])
        reader = csv.DictReader(StringIO(text))
        for item in reader:
            rows.append(
                {
                    "indicator_name": item.get("indicator_name"),
                    "estimate": item.get("estimate"),
                    "estimate_type": item.get("estimate_type"),
                    "estimate_type_detail": item.get("estimate_type_detail"),
                    "estimate_geographic_location": item.get("estimate_geographic_location"),
                    "relative_standard_error": item.get("relative_standard_error"),
                    "source": "BJS/FBI NIBRS National Estimates API, violent incidents dataset",
                }
            )
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        rows.append({"indicator_name": "FETCH_FAILED", "estimate": str(exc), "estimate_type": "", "estimate_type_detail": "", "estimate_geographic_location": "", "relative_standard_error": "", "source": SOURCES["bjs_nibrs_violent_incidents"]})
    path = OUT / "us_bjs_nibrs_violent_incidents_sample.csv"
    write_csv(path, ["indicator_name", "estimate", "estimate_type", "estimate_type_detail", "estimate_geographic_location", "relative_standard_error", "source"], rows)
    return dataset_entry(
        path,
        "US BJS/FBI NIBRS violent incidents national estimates sample",
        SOURCES["bjs_nibrs_violent_incidents"],
        "National incident-estimate table sample",
        "NIBRS estimates are nationally representative public estimates, not raw case files. They are useful for schema and evaluation-design comparison.",
        len(rows),
    )


def dataset_entry(path: Path, title: str, source_url: str, granularity: str, limitations: str, rows: int) -> dict[str, Any]:
    public_path = PUBLIC / path.name
    if path.exists():
        public_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, public_path)
    return {
        "id": path.stem,
        "title": title,
        "file": path.relative_to(ROOT).as_posix(),
        "public_file": f"data/{path.name}",
        "source_url": source_url,
        "granularity": granularity,
        "limitations": limitations,
        "rows": rows,
    }


def build_dashboard(manifest: list[dict[str, Any]]) -> None:
    india_path = OUT / "india_cybercrime_ncrb_pib_2021_2023.csv"
    cyber_rows = list(csv.DictReader(india_path.open(encoding="utf-8")))
    top_growth = sorted(
        [r for r in cyber_rows if r["pct_change_2021_2023"] not in ("", "None")],
        key=lambda r: float(r["pct_change_2021_2023"]),
        reverse=True,
    )[:8]
    write_json(
        PUBLIC / "dashboard.json",
        {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "datasets": manifest,
            "india_cybercrime_top_growth": top_growth,
            "research_gaps": [
                "Public Indian crime tables are mostly aggregate, while behaviour linkage needs incident-level narratives, MO, time, location, and evidence fields.",
                "Cyber complaint portals expose citizen workflows and suspect-identifier reporting, but public complaint-to-FIR conversion datasets are not available from official APIs in this prototype.",
                "Digital-forensic capacity funding is not the same as lab performance, backlog, chain-of-custody integrity, or evidentiary success in court.",
                "Multilingual NLP requires domain-tuned Hindi and Indian-language corpora; English-only models will miss transliterated abuse, local slang, and mixed-script complaints.",
            ],
        },
    )


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    PUBLIC.mkdir(parents=True, exist_ok=True)
    manifest = [
        build_india_cybercrime(),
        build_india_forensic_capacity(),
        build_world_bank_homicide(),
        build_uk_police_sample(),
        build_bjs_nibrs_sample(),
    ]
    generated = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "datasets": manifest,
        "notes": [
            "No personally identifiable operational police data is included.",
            "Datasets are saved for research prototyping and paper-method discussion, not operational deployment.",
            "Fetched API datasets may change over time; rerun scripts/build_datasets.py before final paper submission.",
        ],
    }
    write_json(OUT / "dataset_manifest.json", generated)
    write_json(PUBLIC / "dataset_manifest.json", generated)
    build_dashboard(manifest)
    print(f"Built {len(manifest)} datasets in {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
