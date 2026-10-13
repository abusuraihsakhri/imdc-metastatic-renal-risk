# IMDC (Heng) Metastatic Renal Cell Carcinoma Risk Calculator

An implementation of the six-factor International Metastatic Renal Cell Carcinoma Database Consortium (IMDC/Heng) prognostic grouping for metastatic RCC. **It is not a tumor stage, emergency triage score, individual survival prediction, or treatment recommendation.**

## Published risk model

Each adverse factor scores one point:

| Clinical or laboratory factor | Adverse criterion |
| --- | --- |
| Karnofsky performance status | Below 80% |
| Diagnosis-to-systemic-treatment interval | Less than one year |
| Hemoglobin | Below local lower limit of normal (LLN) |
| Corrected serum calcium | Above local upper limit of normal (ULN) |
| Neutrophils | Above local ULN |
| Platelets | Above local ULN |

**0 factors = Favorable; 1–2 = Intermediate; 3–6 = Poor.**

All six factors must be explicitly assessed. Lab abnormality flags must be determined against appropriate local reference limits; this tool does not infer ranges or calculate corrected calcium from raw measurements.

**Primary reference:** Heng DYC et al. *J Clin Oncol.* 2009;27:5794–5799. [doi:10.1200/JCO.2008.21.4809](https://doi.org/10.1200/JCO.2008.21.4809). [PubMed PMID 19826129](https://pubmed.ncbi.nlm.nih.gov/19826129/).

## Browser application

The `web/` directory is a static, browser-side IMDC calculator. It supports single cases and CSV batch scoring with validation, de-identified case labels, result previews, and downloadable results. Scoring uses JavaScript directly; no Python runtime, Pyodide, server, login, or API keys are required. Serve `web/` as static files or open it through a verified GitHub Pages deployment.

**Privacy:** Scoring and CSV operations run locally in the browser. No data is transmitted to a backend, persisted in browser storage, or sent to analytics. **Do not enter identifiable patient information.** A browser-only tool is not itself a PHI-compliant clinical system.

The deployment workflow is at `.github/workflows/pages.yml`. To publish, enable **Settings → Pages → Build and deployment → Source: GitHub Actions**; GitHub Pages cannot be considered live until a successful deployment and browser smoke test confirm it.

## Python CLI

The clinical scoring engine (`imdc_risk.py`) requires Python 3.10+ and only the Python standard library.

Single-case example:

    python imdc_risk.py single \
      --kps-below-80 no \
      --diagnosis-to-treatment-lt-1yr yes \
      --hemoglobin-below-lln no \
      --corrected-calcium-above-uln no \
      --neutrophils-above-uln no \
      --platelets-above-uln yes

CSV example:

    python imdc_risk.py batch -i sample.csv -o results.csv

CSV must contain the six named snake_case criterion columns shown in `sample.csv`; optional de-identified metadata columns are allowed by the Python CLI. Accepted flag values are `yes/no`, `true/false`, or `1/0`. Missing and ambiguous inputs are rejected rather than interpreted as normal. Source CSV is never overwritten. Spreadsheet-formula-like metadata is escaped on export.

`cli.py batch` also recognizes the six-factor CSV schema; its legacy generic audit CSV format remains supported separately.

## Optional backend and audit demonstrations

Install the dependencies and launch FastAPI locally:

    python -m pip install -r requirements.txt
    python cli.py serve --host 127.0.0.1 --port 8000

`POST /api/imdc` accepts exactly six JSON Boolean criteria and returns a genuine IMDC score and risk group. The existing `/api/audit`, `/api/chat`, `/api/audit/logs`, `agents/`, `enrichment.py`, and `simulator.py` provide **separate generic demonstration utilities**. Their arbitrary alert thresholds and urgency categories are not validated IMDC criteria. The mock chat backend is not a medical inference service; other named LLM providers are not implemented.

Do not expose the demonstration API on a public network without authentication, privacy controls, and security review. For production audit-signing, configure a unique strong `AUDIT_SECRET_KEY` and `APP_ENV=production`; the production configuration refuses the development fallback. The Compose example binds port 8000 to localhost by default.

## Testing and development

    python -m pip install -r requirements.txt
    python -m compileall -q .
    python -m pytest -q
    node --check web/imdc.js && node --check web/app.js
    node --test tests/imdc-web.test.cjs

GitHub Actions runs Python 3.10–3.13 tests and JavaScript unit checks. The static application uses modern browser APIs; test in current Chromium, Firefox, and Safari. This software has not undergone formal clinical validation or regulatory review.

## License

MIT, see [LICENSE](LICENSE).
