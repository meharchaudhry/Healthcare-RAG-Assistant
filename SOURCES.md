# Official Healthcare Document Sources

To scale your RAG system with authentic medical knowledge, download documents from these official repositories. You can drop PDF, TXT, or CSV files into the `data/` directory, and the system will ingest them.

## 1. Clinical Practice Guidelines
*Target: 200-300 documents*

- **ECRI Guidelines Trust**: [guidelines.ecri.org](https://guidelines.ecri.org/) (Requires free account)
- **CDC Clinical Guidance**: [cdc.gov/clinical-guidance](https://www.cdc.gov/)
    - Search for: "Diabetes", "Hypertension", "Sepsis", "Stroke"
- **NICE Guidelines (UK)**: [nice.org.uk/guidance](https://www.nice.org.uk/guidance)
    - Excellent, structured PDF guidelines.
- **AHA/ACC (Cardiology)**: [professional.heart.org](https://professional.heart.org/)

## 2. Drug Information
*Target: 150-250 documents*

- **FDA Label Search**: [labels.fda.gov](https://labels.fda.gov/)
    - Download "Package Inserts" (PI) for common drugs (Metformin, Lisinopril, Atorvastatin).
- **DailyMed**: [dailymed.nlm.nih.gov](https://dailymed.nlm.nih.gov/)
    - Provides structured SPL files and PDFs.

## 3. Medical Coding & Terminology
*Target: 100-150 documents*

- **ICD-10-CM Guidelines**: [cms.gov](https://www.cms.gov/medicare/coding-billing/icd-10-codes)
    - Download the "Official Guidelines for Coding and Reporting" PDF.
- **LOINC (Lab Codes)**: [loinc.org](https://loinc.org/)

## 4. Patient Education & Lifestyle
*Target: 100-150 documents*

- **MedlinePlus**: [medlineplus.gov](https://medlineplus.gov/)
    - Health topics pages can be saved as PDFs.
- **CDC Patient Materials**: [cdc.gov](https://www.cdc.gov/)

## 5. De-identified Patient Notes (Real-World Data)
*Target: 200-300 documents*

- **MIMIC-III / MIMIC-IV**: [physionet.org/content/mimiciv](https://physionet.org/content/mimiciv/)
    - *Note*: Requires credentialing/training to access. Contains thousands of real de-identified discharge summaries.
- **MTSamples**: [mtsamples.com](https://mtsamples.com/)
    - Free collection of transcribed medical reports across specialties. You can scrape/copy these for testing.

## Instructions
1.  Download PDFs/Text files.
2.  Place them in `data/guidelines`, `data/drugs`, etc. (Subdirectories work!).
3.  Run `python process_data.py` to ingest everything at once.
