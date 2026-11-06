# CARE-XAI

**Confidence-Aware, Robust, and Explainable Multimodal Framework for Breast Cancer Screening**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-3776AB.svg?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![PyTorch 2.3+](https://img.shields.io/badge/PyTorch-2.3+-EE4C2C.svg?style=flat-square&logo=pytorch&logoColor=white)](https://pytorch.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688.svg?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React 19](https://img.shields.io/badge/React-19-61DAFB.svg?style=flat-square&logo=react&logoColor=black)](https://react.dev/)

CARE-XAI is a clinical decision-support architecture designed for mammographic lesion assessment. The framework couples bilateral dual-view radiological projections—Craniocaudal (CC) and Mediolateral Oblique (MLO)—with structured clinical indicators through patient-specific adaptive modality gating. 

To bridge the gap between experimental deep learning and safe clinical translation, the system integrates test-time Monte Carlo dropout to quantify predictive uncertainty, flags borderline or out-of-distribution cases, and provides localized gradient-weighted visual explanations (Grad-CAM++) alongside counterfactual modality ablations.

---

## Key Highlights

- **Bilateral Dual-View Processing**: Processes paired CC and MLO mammograms using a shared EfficientNetV2-S feature extractor with masked projection pooling and learnable tokens for unobserved views.
- **Adaptive Modality Gating**: Dynamically computes modality attention weights conditioned on combined representations rather than static early or late feature concatenation.
- **Epistemic Uncertainty Estimation**: Employs Monte Carlo dropout ($T=15$ stochastic forward passes) to estimate predictive variance ($\sigma$) and Shannon entropy ($\mathcal{H}$), identifying ambiguous cases that require radiologist intervention.
- **Visual Saliency & Attribution**: Computes high-resolution Grad-CAM++ saliency overlays on mammographic views to localize microcalcification clusters and architectural distortions.
- **Multi-Cohort Compatibility**: Primary benchmarking on the Chinese Mammography Database (CMMD) with standard ingestion and indexing pipelines for CBIS-DDSM, INbreast, VinDr-Mammo, and EMBED.
- **Clinical Workstation**: A responsive diagnostic interface built with React 19 and FastAPI, equipped with DICOM window leveling/width controls, structured clinical intake, and session audit trails.

---

## Architectural Overview

```
                          [ Input Modalities ]
                                   │
      ┌────────────────────────────┴────────────────────────────┐
      ▼                                                         ▼
[ CC Projection ]   [ MLO Projection ]                  [ Patient Covariates ]
      │                   │                                     │
      └─────────┬─────────┘                                     │
                ▼                                               ▼
   EfficientNetV2-S (Shared Weights)                       Clinical MLP
                │                                               │
                ▼                                               ▼
     Dual-View Masked Pooling                              Dense Latent
       $\mathbf{z}_{\text{img}} \in \mathbb{R}^{256}$        $\mathbf{z}_{\text{clin}} \in \mathbb{R}^{256}$
                │                                               │
                └───────────────────────┬───────────────────────┘
                                        ▼
                          [ Adaptive Gating Network ]
                      $\alpha = \sigma(W_g [\mathbf{z}_{\text{img}} \,\|\, \mathbf{z}_{\text{clin}}] + b_g)$
                      $\mathbf{z}_{\text{fused}} = \alpha \mathbf{z}_{\text{img}} + (1 - \alpha)\mathbf{z}_{\text{clin}}$
                                        │
                                        ▼
                          [ Classification Head ]
                                        │
         ┌──────────────────────────────┼──────────────────────────────┐
         ▼                              ▼                              ▼
  Malignancy Probability      MC Dropout Sampling             Grad-CAM++ Engine
 $p = \sigma(W_c \mathbf{z})$    ($T=15$ Stochastic Passes)      Visual Feature Maps
                              $\sigma^2_{\text{pred}}, \mathcal{H}$
```

### 1. Radiological Feature Extraction
Craniocaudal (CC) and Mediolateral Oblique (MLO) views are preprocessed to standardize orientation (left-facing alignment), normalize dynamic pixel ranges, and crop peripheral background air. Both views pass through an EfficientNetV2-S backbone pre-trained on ImageNet-21k. Visual embeddings are combined via masked average pooling:

$$\mathbf{z}_{\text{img}} = \frac{\sum_{v \in \{\text{CC}, \text{MLO}\}} m_v \cdot f_{\text{img}}(x_v)}{\sum_{v} m_v + \epsilon}$$

where $m_v \in \{0, 1\}$ denotes view availability. When views are missing, the network substitutes a trained missing-view token parameter.

### 2. Clinical Covariate Encoding
Structured risk features (patient age and associated clinical covariates) are normalized and mapped through a two-layer multi-layer perceptron (Linear $\rightarrow$ LayerNorm $\rightarrow$ GELU $\rightarrow$ Dropout $\rightarrow$ Linear) into a shared 256-dimensional embedding space $\mathbf{z}_{\text{clin}}$.

### 3. Patient-Adaptive Fusion Gate
Instead of static concatenation, an adaptive gating mechanism models the relative reliability of visual vs. demographic features on a per-case basis:

$$\mathbf{g} = \text{Softmax}\left( W_2 \cdot \text{GELU}(W_1 [\mathbf{z}_{\text{img}} \,\|\, \mathbf{z}_{\text{clin}}]) \right)$$

$$\mathbf{z}_{\text{fused}} = g_0 \mathbf{z}_{\text{img}} + g_1 \mathbf{z}_{\text{clin}}$$

This formulation prevents dense parenchymal artifacts or noisy imaging scans from degrading overall classification performance when clinical risk indicators point strongly in a given direction, and vice versa.

### 4. Confidence Calibration via Monte Carlo Dropout
To prevent overconfident predictions at the decision boundary, test-time dropout is preserved. For $T$ forward passes:

$$\bar{p} = \frac{1}{T} \sum_{t=1}^{T} p^{(t)}, \quad \sigma^2 = \frac{1}{T} \sum_{t=1}^{T} \left( p^{(t)} - \bar{p} \right)^2$$

Cases exhibiting $\sigma \ge 0.08$ or predictive entropy $\mathcal{H}(\bar{p}) \ge 0.50$ are assigned a `HIGH_UNCERTAINTY` flag, prompting human-in-the-loop secondary evaluation.

---

## Supported Datasets

The repository provides standardized dataset indexers under `backend/scripts/`:

| Dataset | Modality | Cohort Size | Annotations | Source |
|---|---|---|---|---|
| **CMMD** | Full-field digital mammography (FFDM) | 1,775+ patients | Biopsy-verified pathology, age | [TCIA](https://www.cancerimagingarchive.net/collection/cmmd/) |
| **CBIS-DDSM** | Digitized film mammography | 1,566 patients | Masses, calcifications, pathology | [TCIA](https://www.cancerimagingarchive.net/collection/cbis-ddsm/) |
| **INbreast** | Full-field digital mammography | 115 patients (410 views) | Expert contouring, BI-RADS | [INESC Porto](https://biad.ulb.ac.be/inbreast.html) |
| **VinDr-Mammo** | Full-field digital mammography | 5,000 examinations | Breast-level BI-RADS, density | [PhysioNet](https://physionet.org/content/vindr-mammo/1.0.0/) |
| **EMBED** | Multi-ethnic screening cohort | Multi-site longitudinal | Demographics, density, pathology | [Emory Healthcare](https://imaging.emory.edu/research/embed/) |

*Note: For testing without downloading multi-gigabyte archives, use `backend/scripts/generate_synthetic_data.py` to synthesize valid DICOM pairs and manifests.*

---

## Directory Structure

```text
care-xai/
├── backend/
│   ├── app/                      # Structured API router modules
│   │   ├── routes/               # Modular endpoints (predict, explain, health, config)
│   │   ├── deps.py               # Dependency injection
│   │   └── main.py               # Application factory
│   ├── src/                      # Core deep learning modules
│   │   ├── model.py              # CAREXAI architecture and adaptive fusion
│   │   ├── data.py               # Dual-view dataset loader and augmentation
│   │   ├── preprocess.py         # DICOM normalization, orientation, cropping
│   │   ├── uncertainty.py        # Monte Carlo dropout inference engine
│   │   ├── xai.py                # Grad-CAM++ hooks and SHAP explanations
│   │   ├── metrics.py            # ROC-AUC, PR-AUC, ECE, Brier, Youden's J
│   │   ├── service.py            # Model service abstraction
│   │   └── config.py             # Configuration specification
│   ├── scripts/                  # Data indexers and dataset utilities
│   ├── checkpoints/              # Model weights storage
│   ├── outputs/                  # Evaluation summaries and reports
│   ├── api.py                    # Standalone FastAPI server for workstation
│   ├── train.py                  # Supervised training loop with early stopping
│   ├── predict.py                # CLI single-case inference
│   ├── config.yaml               # Model configuration & hyperparameters
│   └── requirements.txt          # Python environment dependencies
│
├── frontend_react/               # Clinical diagnostic workstation
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.jsx     # Diagnostic viewer, audit logger, copilot
│   │   │   ├── LandingPage.jsx   # System overview
│   │   │   ├── Navbar.jsx        # Navigation header
│   │   │   └── SignInModal.jsx   # Mock clinician authentication
│   │   ├── App.jsx               # Application root
│   │   └── index.css             # High-contrast clinical theme
│   ├── package.json
│   └── vite.config.js
│
├── docs/                         # Extended technical documentation
│   └── DATASETS.md               # Dataset acquisition and directory setup
├── requirements.txt              # Consolidated dependencies
└── README.md
```

---

## Getting Started

### Prerequisites
- Python 3.10 or later
- Node.js 18+ and npm
- CUDA-compatible GPU recommended for training; CPU supported for inference

### 1. Environment Setup

Clone the repository and initialize the virtual environment:

```bash
git clone https://github.com/achalzz/CARE-XAI.git
cd CARE-XAI

python -m venv .venv

# On Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# On Linux / macOS
source .venv/bin/activate

pip install -r backend/requirements.txt
```

### 2. Synthetic Test Verification (Optional)

Generate synthetic cohorts to verify pipeline execution without downloading external medical datasets:

```bash
python backend/scripts/generate_synthetic_data.py --num-patients 20
python backend/scripts/build_index.py
```

### 3. Launch the Backend API

Start the REST API server:

```bash
uvicorn backend.api:app --host 0.0.0.0 --port 8000 --reload
```

- API Base URL: `http://localhost:8000`
- Interactive OpenAPI Documentation: `http://localhost:8000/docs`
- Health Endpoint: `http://localhost:8000/api/health`

### 4. Launch the Diagnostic Workstation

In a separate terminal:

```bash
cd frontend_react
npm install
npm run dev
```

The clinical interface will be available at `http://localhost:5173`.

---

## Training and Evaluation

To train CARE-XAI on an indexed cohort (e.g., CMMD):

```bash
python backend/train.py \
  --index backend/data/processed/cmmd1_index.csv \
  --epochs 20 \
  --batch-size 4 \
  --image-size 384 \
  --lr 8e-5 \
  --out backend/checkpoints/care_xai_best.pt
```

### Command-Line Inference

Evaluate a single patient record by identifier:

```bash
python backend/predict.py --patient-id D1-0006
```

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Service health status, active compute device, and checkpoint status. |
| `GET` | `/api/samples` | Lists indexed test cases available for immediate evaluation. |
| `POST` | `/api/predict/patient` | Runs full inference with MC-dropout uncertainty on an indexed patient ID. |
| `POST` | `/api/predict/dual-upload` | Accepts paired CC and MLO DICOM uploads with patient clinical parameters. |
| `POST` | `/api/dicom/metadata` | Parses standard DICOM tags (laterality, view angle, patient age). |
| `POST` | `/api/audits` | Records radiologist feedback (concordance, clinical notes, audit timestamp). |
| `POST` | `/api/chat` | Clinical assistant endpoint providing multilingual diagnostic explanations. |

---

## Evaluation Metrics

Model performance is evaluated across discrimination and probabilistic calibration dimensions:

- **Discrimination**: Receiver Operating Characteristic Area Under Curve (ROC-AUC) and Precision-Recall Area Under Curve (PR-AUC).
- **Thresholding**: Optimal operating point determined via Youden's $J$ statistic ($J = \text{Sensitivity} + \text{Specificity} - 1$).
- **Calibration**: Brier Score and Expected Calibration Error (ECE) across 10 uniform reliability bins:

$$\text{ECE} = \sum_{m=1}^{M} \frac{|B_m|}{N} \left| \text{acc}(B_m) - \text{conf}(B_m) \right|$$

---

## Ethical Considerations & Disclaimer

> **Academic Research Prototype**: CARE-XAI has been engineered solely for scientific investigation, technical validation, and educational demonstration. It is not an FDA-, CE-, or CDSCO-cleared medical device, nor has it undergone prospective multi-site randomized clinical trials. Under no circumstances should this software be utilized for autonomous patient triaging, diagnosis, or clinical management. All algorithmic predictions and heatmaps must be independently assessed by certified radiological personnel.

---

## Citation

If you utilize this framework or its components in your research, please cite:

```bibtex
@misc{carexai2026,
  title={CARE-XAI: Confidence-Aware Robust Explainable Multimodal AI for Cancer Diagnosis},
  author={CARE-XAI Contributors},
  year={2026},
  howpublished={\url{https://github.com/achalzz/CARE-XAI}},
  note={Research prototype implementation}
}
```

---

## License

Distributed under the MIT License for academic and non-commercial research use. See `LICENSE` for details.
