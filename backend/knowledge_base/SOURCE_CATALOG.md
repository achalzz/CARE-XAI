# CARE-XAI source catalog

This catalog separates **model-development data**, **knowledge-base references**, and
**integration services**. Review every source's current terms, institutional approval,
and de-identification requirements before use. Never upload patient-identifiable data.

## 1. Mammography data for model development

| Source | Best use | Notes |
|---|---|---|
| [TCIA CMMD](https://www.cancerimagingarchive.net/collection/cmmd/) | Primary paired CC/MLO benchmark and biopsy-confirmed classification research | This is the project’s existing data source. Preserve the collection citation and comply with its data-use terms. |
| [CBIS-DDSM on Kaggle](https://www.kaggle.com/datasets/awsaf49/cbis-ddsm-breast-cancer-image-dataset) | Lesion/calcification experimentation and external testing | Kaggle-hosted derivative; inspect the data card and original DDSM attribution before download. |
| [DMID on Kaggle](https://www.kaggle.com/datasets/orvile/dmid-breast-cancer-mammography-dataset) | Additional mammography classification experiments | Research/education-oriented dataset. Validate labels, view completeness, and license. |
| [MIAS on Kaggle](https://www.kaggle.com/datasets/orvile/mias-dataset/data) | Small benchmark and preprocessing smoke tests | Older digitized-film data; do not treat it as representative of modern FFDM deployment. |
| [Augmented INbreast on Kaggle](https://www.kaggle.com/datasets/eoussama/breast-cancer-mammograms/data) | Prototype classification only | CC BY-NC-SA 4.0 and augmented images: do not use to claim independent validation or production performance. |

## 2. Approved knowledge-base references

| Source | Add to knowledge base? | Appropriate role |
|---|---|---|
| [ACR BI-RADS overview](https://www.acr.org/Clinical-Resources/Clinical-Tools-and-Reference/Reporting-and-Data-Systems/BI-RADS) | Add links and institution-licensed extracts only | Standardized breast-imaging terminology and reporting framework. The full manual is licensed/copyrighted. |
| [ACR mammography reporting requirements](https://accreditationsupport.acr.org/support/solutions/articles/11000046162-reporting-mammography-revised-12-12-19-) | Yes, as a linked/reference summary | BI-RADS final-assessment categories and reporting workflow. |
| [NCI mammograms overview](https://www.cancer.gov/types/breast/screening/mammograms) | Yes | Public patient-safe background for screening, breast density, and BI-RADS context. |
| [ACR density statement](https://www.acr.org/Advocacy/Position-Statements/Reporting-Breast-Density) | Yes | Density reporting and its effect on mammographic sensitivity. |
| [NCCN patient guidelines](https://www.nccn.org/patients/guidelines/content/PDF/genetics-patient.pdf) | Link only unless your licence permits local copies | Genetics/familial risk context; verify the current guideline/version and use conditions. |

## 3. Technical services and standards

| Source | CARE-XAI use |
|---|---|
| [HL7 FHIR DiagnosticReport](https://hl7.org/fhir/diagnosticreport.html) | Standard shape for interoperable diagnostic-report export; can reference images, observations, narrative conclusions, and a formatted PDF. |
| [DICOMweb QIDO-RS / WADO-RS](https://dicom.nema.org/Dicom/News/November2025/docs/sups/sup248.pdf) | PACS search and retrieval design. Use QIDO-RS for finding studies/series and WADO-RS for retrieving image data/metadata. |
| [OHIF Viewer](https://github.com/ohif/Viewers) | Enterprise-grade web DICOM viewer option with DICOMweb support, measurements, and extension architecture. |
| [MONAI Label](https://docs.monai.io/projects/label/en/latest/index.html) | Human-in-the-loop labeling and active-learning service; can integrate with OHIF and DICOMweb. |

## Recommended ingestion order

1. Add local hospital-approved protocols and de-identified FAQs under `protocols/`.
2. Add public or licensed guideline summaries under `guidelines/`, with source URL, publication date, version, and reviewer.
3. Add benchmark documentation/data dictionaries—not raw patient scans—under `references/`.
4. Record a source owner, review date, licence, and expiry date for each imported document.

The Smart Chat retriever supports `.md`, `.txt`, `.json`, `.csv`, `.tsv`, `.xlsx`,
`.pdf`, and `.docx` files placed anywhere in this directory.
