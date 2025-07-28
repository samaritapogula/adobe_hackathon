import json
import re
from pathlib import Path
import fitz  # PyMuPDF
from unidecode import unidecode

def clean_text(text):
    text = unidecode(text)
    text = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def is_potential_heading(text):
    if len(text) < 3:
        return False
    if re.fullmatch(r'\W+', text):  # only symbols
        return False
    if re.match(r"^[*•\-–]\s", text):  # bullet
        return False
    if text.lower() in {"name", "date", "signature"}:
        return False
    return True

def merge_fragments_vertically(blocks):
    merged = []
    current = None
    for block in sorted(blocks, key=lambda b: b['bbox'][1]):
        if current and abs(block['bbox'][1] - current['bbox'][3]) < 5:
            current['text'] += ' ' + block['text']
            current['bbox'] = (
                current['bbox'][0],
                current['bbox'][1],
                max(current['bbox'][2], block['bbox'][2]),
                max(current['bbox'][3], block['bbox'][3])
            )
        else:
            if current:
                merged.append(current)
            current = block.copy()
    if current:
        merged.append(current)
    return merged

def find_headings_and_title(doc):
    all_blocks = []
    text_counts = {}
    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict")['blocks']
        for b in blocks:
            if b['type'] != 0:
                continue
            for l in b['lines']:
                if not l['spans']:
                    continue
                span = l['spans'][0]
                text = " ".join(s['text'] for s in l['spans']).strip()
                text = clean_text(text)
                if not text:
                    continue
                block_data = {
                    "text": text,
                    "size": round(span['size']),
                    "is_bold": (span['flags'] & 16) != 0,
                    "bbox": l['bbox'],
                    "page_num": page_num + 1
                }
                all_blocks.append(block_data)
                text_counts[text] = text_counts.get(text, 0) + 1

    # Title logic (same)
    page1_blocks = [b for b in all_blocks if b['page_num'] == 1]
    merged_blocks = merge_fragments_vertically(page1_blocks)
    if merged_blocks:
        max_size = max(b['size'] for b in merged_blocks)
        title_candidates = [b for b in merged_blocks if b['size'] >= max_size - 1]
        title = max(title_candidates, key=lambda b: len(b['text']))['text']
    else:
        title = max(text_counts.items(), key=lambda x: x[1])[0]

    # Heading levels by font size
    font_sizes = [b['size'] for b in all_blocks]
    body_size = max(set(font_sizes), key=font_sizes.count)
    heading_sizes = sorted([s for s in set(font_sizes) if s > body_size], reverse=True)[:5]
    size_to_level = {s: f"H{i+1}" for i, s in enumerate(heading_sizes)}

    # Extract headings
    headings = []
    seen = set()
    for b in all_blocks:
        txt = b['text']
        if txt in seen or not is_potential_heading(txt):
            continue
        if b['size'] not in size_to_level and not b['is_bold']:
            continue
        level = size_to_level.get(b['size'], "H5")

        # Promote single-word bold uppercase lines (e.g., "Goals:")
        if b['is_bold'] and b['size'] >= body_size and txt.endswith(':') and txt.count(' ') <= 2:
            level = "H2"

        seen.add(txt)
        headings.append({
            "level": level,
            "text": txt,
            "page": b['page_num']
        })

    return {
        "title": title,
        "outline": headings
    }

def process_all_pdfs_sequentially(input_dir, output_dir):
    """
    Processes all PDFs in a directory one by one.
    """
    print(f"--- Running on all PDFs in '{input_dir}' ---")
    pdf_files = list(Path(input_dir).glob("*.pdf"))
    if not pdf_files:
        print(f"No PDF files found in {input_dir}")
        return

    for pdf_file in pdf_files:
        print(f"--- Processing file: {pdf_file.name} ---")
        try:
            headings_data = find_headings_and_title(pdf_file)
            output_file_path = Path(output_dir) / f"{pdf_file.stem}.json"
            with open(output_file_path, 'w') as f:
                json.dump(headings_data, f, indent=4)
            print(f"Successfully processed. Output saved to {output_file_path}")
        except Exception as e:
            print(f"!!! An error occurred while processing {pdf_file.name}: {e} !!!")

if __name__ == "__main__":
    # The Docker container will provide these paths
    input_directory = Path("/app/input")
    output_directory = Path("/app/output")
    output_directory.mkdir(parents=True, exist_ok=True)
    
    process_all_pdfs_sequentially(input_directory, output_directory)
