# CARE-XAI Knowledge Base

Place approved clinical reference material here for Smart Chat. Supported formats are
plain-text Markdown (`.md`), text (`.txt`), JSON (`.json`), CSV/TSV (`.csv`, `.tsv`),
Excel (`.xlsx`), PDF (`.pdf`), and Word (`.docx`). Files are read at request time, so
restarting the API is not required after adding or editing content.

Suggested organization:

```text
knowledge_base/
  guidelines/        # ACR / NCCN / local approved pathways
  protocols/         # Hospital imaging and escalation protocols
  references/        # Validated articles and internal clinical FAQs
```

Keep only de-identified, institution-approved content here. Do not add patient records,
credentials, or protected health information. Smart Chat is decision support and must
not be treated as an autonomous diagnostic system.

PDFs must contain selectable text; scanned PDFs need OCR before they can be searched.
Legacy `.doc` and `.xls` files should be converted to `.docx` and `.xlsx` first.

For JSON, use either `{ "title": "...", "content": "..." }` or a JSON list of
objects with those keys.
