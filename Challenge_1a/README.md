# Adobe India Hackathon 2025 - Round 1A 
This project is a solution for Challenge 1A of the Adobe India Hackathon. It is a robust, rule-based system written in Python for extracting a structured outline (Title and H1, H2, H3 headings) from various types of PDF documents.

## Approach
This solution uses a robust, rule-based system to analyze a PDF's structure and extract its hierarchical outline. The logic is designed to be adaptive and handle various document layouts, including single-page reports and complex, multi-page books with multi-column layouts.

The core process is as follows:

## Text Extraction & Sorting 
The script first extracts all text blocks with their rich metadata (font size, style, and position). For multi-column documents, it sorts these blocks by their page number and coordinates to ensure a correct, column-by-column reading order.

## Hybrid Title Detection
A hybrid strategy is used to find the document's title. For multi-page documents, it identifies the most common repeating header text. For single-page documents (or those without a clear header), it falls back to a layout-based analysis, selecting the most prominent text on the first page based on a score of its font size and vertical position.

## Heading Classification
The script filters out irrelevant content like repeating headers, page numbers, and Table of Contents entries. It then analyzes the remaining text, identifying potential headings based on a combination of features:

* Font size relative to the document's main body text.

* Font style (e.g., bold).

* Common textual patterns (e.g., "Chapter 1", "1.1.1").

## Hierarchy Assignment
The identified headings are mapped to H1, H2, and H3 levels based on a dynamic analysis of the top three most prominent heading font styles found in the document.

## How to Build and Run

### Prerequisites

* Docker must be installed and running on your system.

### Instructions

1.  **Clone the Repository**:
    ```bash
    git clone [https://github.com/samaritapogula/adobe_hackathon.git](https://github.com/samaritapogula/adobe_hackathon.git)
    cd adobe_hackathon
    ```

2.  **Prepare Input**:
    * Create an `input` directory in the project root.
    * Place all the PDF files you want to process inside this `input` directory.

3.  **Build the Docker Image**:
    ```bash
    docker build --platform linux/amd64 -t adobe_hackathon .
    ```

4.  **Run the Container**:
    This command will process all PDFs in the `input` folder and place the resulting `.json` files in a new `output` folder.
    ```bash
    docker run --rm -v $(pwd)/input:/app/input:ro -v $(pwd)/output:/app/output adobe_hackathon
    ```
