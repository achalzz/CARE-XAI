# Multi-Center Mammography Dataset Acquisition & Setup Guide

This guide details how to acquire, place, preprocess, and index the 5 supported datasets in **CARE-XAI**:
1. **CMMD** (Chinese Mammography Database)
2. **CBIS-DDSM** (Curated Breast Imaging Subset of DDSM)
3. **INbreast**
4. **VinDr-Mammo** (PhysioNet)
5. **EMBED** (Emory Breast Imaging Dataset)

---

## ⚡ Instant Dry-Run: Multi-Center Synthetic Generator

If you want to test the entire multi-center pipeline immediately without downloading ~200+ GB of hospital DICOMs:

```bash
# Generates synthetic DICOM images + metadata for all 5 datasets in backend/data/raw/
python backend/scripts/generate_multicenter_synthetic_data.py --num-patients-per-dataset 10

# Build individual index files
python backend/scripts/build_index.py
python backend/scripts/build_cbis_ddsm_index.py
python backend/scripts/build_inbreast_index.py
python backend/scripts/build_vindr_index.py
python backend/scripts/build_embed_index.py

# Merge all into unified multicenter index
python backend/scripts/build_multicenter_index.py
```

---

## 1. CMMD (Chinese Mammography Database)

* **Host**: [The Cancer Imaging Archive (TCIA)](https://www.cancerimagingarchive.net/collection/cmmd/)
* **Format**: Dual-view FFDM DICOMs (CC, MLO) + Excel metadata (`CMMD_clinicaldata_revision.xlsx`).
* **Download Instructions**:
  1. Install the [NBIA Data Retriever](https://wiki.cancerimagingarchive.net/display/NBIA/NBIA+Data+Retriever+FAQ).
  2. Download the CMMD manifest file (`.tcia`) from TCIA.
  3. Download the clinical metadata spreadsheet `CMMD_clinicaldata_revision.xlsx`.
  4. Place the files as follows:
     ```text
     backend/data/raw/
       ├── CMMD/
       │   ├── D1-0001/
       │   │   ├── CC.dcm
       │   │   └── MLO.dcm
       │   └── ...
       └── CMMD_clinicaldata_revision.xlsx
     ```
* **Build Index**:
  ```bash
  python backend/scripts/build_index.py
  ```

---

## 2. CBIS-DDSM (Curated Breast Imaging Subset of DDSM)

* **Host**: [TCIA CBIS-DDSM Collection](https://www.cancerimagingarchive.net/collection/cbis-ddsm/)
* **Format**: Digital mammograms (CC and MLO views) + pathology labels (`mass_case_description_train_set.csv`, `calc_case_description_train_set.csv`, etc.).
* **Download Instructions**:
  1. Open the TCIA CBIS-DDSM portal and download the NBIA Data Retriever manifest.
  2. Download the description CSV files:
     - `mass_case_description_train_set.csv`
     - `mass_case_description_test_set.csv`
     - `calc_case_description_train_set.csv`
     - `calc_case_description_test_set.csv`
  3. Organize under `backend/data/raw/CBIS-DDSM/`:
     ```text
     backend/data/raw/CBIS-DDSM/
       ├── mass_case_description_train_set.csv
       ├── mass_case_description_test_set.csv
       ├── P_00001/
       │   ├── P_00001_LEFT_CC.dcm
       │   └── P_00001_LEFT_MLO.dcm
       └── ...
     ```
* **Build Index**:
  ```bash
  python backend/scripts/build_cbis_ddsm_index.py
  ```

---

## 3. INbreast

* **Host**: Breast Research Group, INESC Porto, Portugal ([INbreast Database](https://biad.ulb.ac.be/inbreast.html))
* **Format**: High-precision full-field digital mammograms (FFDM) + `INbreast.csv`.
* **Download Instructions**:
  1. Request academic access following the institutional data sharing agreement.
  2. Download the `AllDICOMs` folder and the master table `INbreast.csv`.
  3. Organize under `backend/data/raw/INbreast/`:
     ```text
     backend/data/raw/INbreast/
       ├── INbreast.csv
       └── AllDICOMs/
           ├── 20586908_6c613a14b80a8591_MG_R_CC_ANON.dcm
           └── ...
     ```
* **Build Index**:
  ```bash
  python backend/scripts/build_inbreast_index.py
  ```

---

## 4. VinDr-Mammo

* **Host**: [PhysioNet VinDr-Mammo](https://physionet.org/content/vindr-mammo/1.0.0/)
* **Format**: 5,000 screening exams (20,000 images) with breast-level BI-RADS and density.
* **Download Instructions**:
  1. Create an account on PhysioNet and sign the data use agreement.
  2. Download `breast-level_annotations.csv` and the DICOM images using `wget` or AWS CLI.
  3. Organize under `backend/data/raw/VinDr-Mammo/`:
     ```text
     backend/data/raw/VinDr-Mammo/
       ├── breast-level_annotations.csv
       └── images/
           ├── <study_id>/
           │   ├── <image_id_1>.dcm
           │   └── <image_id_2>.dcm
           └── ...
     ```
* **Build Index**:
  ```bash
  python backend/scripts/build_vindr_index.py
  ```

---

## 5. EMBED (Emory Breast Imaging Dataset)

* **Host**: [Emory Healthcare / EMBED](https://imaging.emory.edu/research/embed/)
* **Format**: Multi-ethnic screening cohort with longitudinal clinical variables.
* **Download Instructions**:
  1. Apply for access via Emory's data repository portal.
  2. Extract the cohort cohort table (`embed_metadata.csv`) and DICOM studies.
  3. Organize under `backend/data/raw/EMBED/`:
     ```text
     backend/data/raw/EMBED/
       ├── embed_metadata.csv
       └── images/
           ├── <patient_id>/
           │   ├── CC.dcm
           │   └── MLO.dcm
           └── ...
     ```
* **Build Index**:
  ```bash
  python backend/scripts/build_embed_index.py
  ```

---

## 🔄 Multi-Center Training & Cross-Dataset Validation

### 1. Joint Multi-Center Training
Train CARE-XAI on all available cohorts simultaneously:
```bash
python backend/train.py \
  --index backend/data/processed/multicenter_index.csv \
  --epochs 20 \
  --batch-size 4
```

### 2. Zero-Shot External Validation
Train solely on **CMMD** and test generalization zero-shot on **INbreast** or **CBIS-DDSM**:
```bash
# 1. Train on CMMD
python backend/train.py --index backend/data/processed/cmmd1_index.csv --out backend/checkpoints/cmmd_only.pt

# 2. Evaluate checkpoint on INbreast test set
python backend/predict.py --checkpoint backend/checkpoints/cmmd_only.pt --patient-id 1001
```
