# Data Sources and Provenance

This prototype uses public aggregate datasets and small API samples only. It does not include operational police records, victim identities, device images, chat dumps, call-detail records, bank statements, or private forensic artifacts.

## India Sources

1. Press Information Bureau release citing NCRB Crime in India tables for State/UT cybercrime cases in 2021, 2022, and 2023.
2. The same PIB release includes Annexure-II funding releases for the scheme "Strengthening of DNA Analysis and Cyber Forensic Capacities in State FSLs."
3. NCRB, CCTNS, I4C, National Cyber Crime Reporting Portal, and Digital Police are treated as agency/platform context. Public aggregate sources do not expose the incident-level evidence schema needed for suspect linkage.

## Global Comparison Sources

1. World Bank WDI indicator `VC.IHR.PSRC.P5`, sourced from UNODC, is fetched for selected country-year intentional homicide rates.
2. UK Police street-level crime API is sampled around central London for schema and geospatial comparison.
3. FBI Crime Data API national estimates are sampled for US aggregate comparison.

## Research Limits

Aggregate tables can support trend, hotspot, and cross-country comparison. They cannot prove behavioural linkage, identify suspects, measure chain-of-custody quality, or validate digital-forensic admissibility. A paper should therefore present this platform as a research decision-support prototype, not an autonomous investigative system.
