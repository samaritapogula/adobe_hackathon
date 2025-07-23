import json
from pathlib import Path
import time

def process_all_pdfs():
    """
    Scans the input directory, processes each PDF, and writes a JSON output.
    """
    input_dir = Path("/app/input")
    output_dir = Path("/app/output")

    # Ensure the output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Starting PDF processing...")
    
    pdf_files = list(input_dir.glob("*.pdf"))
    if not pdf_files:
        print("No PDF files found in /app/input.")
        return

    for pdf_file in pdf_files:
        start_time = time.time()
        print(f"Processing file: {pdf_file.name}")

        # --- THIS IS WHERE YOUR PDF PARSING LOGIC WILL GO ---
        # For now, we'll just create dummy data.
        output_data = {
            "title": f"Title for {pdf_file.stem}",
            "outline": [
                {"level": "H1", "text": "Dummy Introduction", "page": 1},
                {"level": "H2", "text": "Dummy Section 1.1", "page": 2},
            ]
        }
        # --- END OF PDF PARSING LOGIC ---

        # Define the output file path
        output_file_path = output_dir / f"{pdf_file.stem}.json"

        # Write the JSON output
        with open(output_file_path, 'w') as f:
            json.dump(output_data, f, indent=4)
        
        end_time = time.time()
        print(f"Finished processing {pdf_file.name}. Output saved to {output_file_path}")
        print(f"Time taken: {end_time - start_time:.4f} seconds.\n")

    print("All files processed.")


if __name__ == "__main__":
    process_all_pdfs()
