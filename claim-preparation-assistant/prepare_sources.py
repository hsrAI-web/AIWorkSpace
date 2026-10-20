"""Extract original PDFs with page locators and reproducible provenance."""
from pathlib import Path
import hashlib
import json
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent
SOURCES = [
    ('M1', 'optima-secure-claim-manual.pdf', 'https://customer-portal-assets.hdfcergo.com/assets/v2/docs/default-source/downloads/claim-forms/my-optima-secure---cm-783226902747.pdf'),
    ('F1', 'optima-secure-claim-form.pdf', 'https://customer-portal-assets.hdfcergo.com/assets/v2/docs/default-source/downloads/claim-forms/myoptima-secure---cf-58675432702.pdf'),
]

def main():
    pages, manifest = [], []
    for source_id, name, url in SOURCES:
        path = ROOT / 'sources' / name
        raw = path.read_bytes()
        if not raw.startswith(b'%PDF-'):
            raise ValueError(f'{name} is not a PDF')
        reader = PdfReader(path)
        for number, page in enumerate(reader.pages, 1):
            text = page.extract_text() or ''
            if not text.strip():
                raise ValueError(f'OCR required: {name}, page {number}')
            pages.append(dict(source_id=source_id, file=name, page=number, text=text))
        manifest.append(dict(source_id=source_id, file=name, url=url,
                             accessed='2026-10-19', pages=len(reader.pages),
                             sha256=hashlib.sha256(raw).hexdigest(),
                             product='my: Optima Secure', uin='HDFHLIP25041V062425',
                             applicability='Verify against the issued policy version'))
    destination = ROOT / 'data'
    destination.mkdir(exist_ok=True)
    (destination / 'pages.json').write_text(json.dumps(pages, ensure_ascii=False, indent=2), encoding='utf-8')
    (destination / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(f'Extracted {len(pages)} nonempty pages from {len(manifest)} verified PDF files.')

if __name__ == '__main__':
    main()
