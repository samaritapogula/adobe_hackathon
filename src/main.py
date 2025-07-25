import json
import re
from pathlib import Path
import fitz  # PyMuPDF
from collections import Counter

def find_headings_and_title(doc):
    """
    Analyzes a report-style PDF to extract a hierarchical outline.
    """
    all_text_blocks = []
    text_counts = {}
    
    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if b['type'] == 0:
                for l in b["lines"]:
                    if not l["spans"]: continue
                    line_text = " ".join([s['text'] for s in l['spans']]).strip()
                    if not line_text or (line_text.isdigit() and len(line_text) < 4):
                        continue
                    text_counts[line_text] = text_counts.get(line_text, 0) + 1
                    span = l["spans"][0]
                    all_text_blocks.append({
                        "text": line_text, 
                        "size": round(span["size"]), 
                        "is_bold": (span["flags"] & 16) != 0,
                        "bbox": l["bbox"], 
                        "page_num": page_num + 1
                    })

    if not all_text_blocks: return {"title": "Error: No text found", "outline": []}

    all_text_blocks.sort(key=lambda b: (b['page_num'], b['bbox'][0], b['bbox'][1]))
    
    title, title_bbox, header_footer_texts = "", None, set()
    if doc.page_count > 1:
        repeating_texts = {text: count for text, count in text_counts.items() if count >= 2}
        if repeating_texts:
            title = max(repeating_texts, key=repeating_texts.get)
            header_footer_texts = {title}
    
    if not title:
        max_title_score = 0
        page1_blocks = [b for b in all_text_blocks if b['page_num'] == 1]
        if page1_blocks:
            for block in page1_blocks:
                score = (1 / (block['bbox'][1] + 1)) * 1000 + block['size']
                if score > max_title_score:
                    max_title_score = score
                    title = block['text']
                    title_bbox = block['bbox']
    
    headings = []
    blocks_to_process = all_text_blocks[:]
    
    toc_page_num = 0
    for block in blocks_to_process:
        if "table of contents" in block['text'].lower():
            toc_page_num = block['page_num']
            headings.append({"level": "H1", "text": block['text'], "page": block['page_num']})
            break
    if toc_page_num > 0:
        blocks_to_process = [b for b in blocks_to_process if b['page_num'] != toc_page_num]

    non_header_blocks = [b for b in blocks_to_process if b['text'] not in header_footer_texts and b['bbox'] != title_bbox]
    font_sizes = [b['size'] for b in non_header_blocks]
    if not font_sizes:
        headings.sort(key=lambda x: (x['page'], x.get('level', 'H9')))
        return {"title": title, "outline": headings}
        
    body_size = max(set(font_sizes), key=font_sizes.count)
    
    heading_pattern = re.compile(r"^(?:#\s*\d+|Chapter \d+|[IVXLCDM]+\.|[A-Z]\)|\d+(?:\.\d+)*)", re.IGNORECASE)
    potential_headings = []
    for b in non_header_blocks:
        is_large_font = b['size'] > body_size
        is_body_font_but_bold = (b['size'] == body_size and b['is_bold'])
        is_heading_pattern = heading_pattern.match(b['text'])
        if is_heading_pattern or ((is_large_font or is_body_font_but_bold) and b['text'] and b['text'][0].isupper()):
            potential_headings.append(b)

    heading_font_sizes = sorted([size for size in set([b['size'] for b in potential_headings])], reverse=True)[:5]
    size_to_level_map = {size: f"H{i+1}" for i, size in enumerate(heading_font_sizes)}

    last_heading_indent = -1
    last_heading_level = 0
    
    for block in potential_headings:
        text = block['text']
        indent = block['bbox'][0]
        level_str = size_to_level_map.get(block['size'])
        level = int(level_str[-1]) if level_str else 9
        
        if last_heading_indent != -1 and indent > last_heading_indent + 5 and level >= last_heading_level:
            continue
            
        if re.match(r"^\s*[\•\*\-]\s+", text): continue
        date_pattern = re.compile(r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s*\d{4}\b', re.IGNORECASE)
        year_pattern = re.compile(r'^\s*(19|20)\d{2}\s*$')
        if date_pattern.search(text) or year_pattern.match(text): continue
        if re.match(r"^\d+\.$", text.strip()): continue
        punctuation_count = sum(1 for char in text if char in ",.():")
        if punctuation_count > 3: continue
            
        heading_level = size_to_level_map.get(block['size'])
        if heading_level:
            headings.append({"level": heading_level, "text": text, "page": block['page_num']})
            last_heading_indent = indent
            last_heading_level = level

    headings.sort(key=lambda x: (x['page'], [b['bbox'][1] for b in all_text_blocks if b['text'] == x['text'] and b['page_num'] == x['page']][0]))
    return {"title": title, "outline": headings}

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
