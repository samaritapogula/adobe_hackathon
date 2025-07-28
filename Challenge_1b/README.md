# Adobe India Hackathon 2025 - Round 1B 
This project is a solution for Challenge 1B of the Adobe India Hackathon. It is an advanced, multi-stage pipeline designed to act as an intelligent document analyst, extracting and prioritizing relevant content from a collection of PDFs based on a specific user persona and task.

## Approach Explanation 
This solution mimics the workflow of a human research assistant by first understanding the structure of the documents, then understanding the user's query in depth, and finally scoring and curating the most relevant content. The process is broken down into four main stages:

### Stage 1: Structural Analysis & Content Chunking
The foundation of this system is its ability to understand the structure of each PDF. It leverages the logic developed in Round 1A to perform a full structural analysis, identifying all the headings within each document. This structure is then used to intelligently "chunk" the content. Instead of using arbitrary chunks like fixed-size paragraphs, the system defines a chunk as all the text that falls between one heading and the next. This creates semantically coherent, section-based chunks that are ideal for relevance analysis and ensures that the final output can be linked back to a meaningful section title.

### Stage 2: Dynamic Query Generation
To accurately capture a user's intent, a simple query is often insufficient. This system employs a dynamic query expansion technique. Instead of using the user's raw task description as a single query, it generates a diverse set of ten different questions and prompts based on the user's persona and job. These varied queries are then encoded into high-dimensional vectors using a sentence-transformer model, and the resulting vectors are averaged. This creates a single, robust "intent vector" that captures the nuances of the user's request from multiple angles, leading to more accurate semantic matching.

### Stage 3: Hybrid Relevance Scoring
The core of the system is its hybrid scoring model, which combines the strengths of both semantic and keyword-based search. Each text chunk is assigned a score based on a weighted average:

* 70% Semantic Score: The cosine similarity between the chunk's vector and the user's averaged intent vector. This captures contextual and semantic relevance.

* 30% Keyword Score: A simple, direct score based on the presence of keywords from the original persona and task. This ensures that chunks containing key terms are given a slight boost.
This hybrid approach provides a balanced score that reflects both deep understanding and specific keyword relevance.

### Stage 4: Intelligent Curation
Finally, after all chunks are scored and ranked, a curation layer ensures the final output is diverse and useful. It applies de-duplication logic to avoid returning multiple sections with very similar titles and enforces a limit on the number of results from any single document. This guarantees the user receives a varied and concise summary from across the entire document collection, providing the most valuable insights for their task.

## Libraries and Models
### Core Libraries:
* PyMuPDF (fitz): Used for robust PDF parsing and text extraction.

* sentence-transformers: The core framework for generating text embeddings.

* torch: The backend deep learning framework for sentence-transformers.

### ML Model:

* all-MiniLM-L6-v2: A small, fast, and powerful sentence-transformer model used for semantic search. It is included in the Docker image and runs entirely offline.

## How to Build and Run
### Prerequisites

* Docker must be installed and running.

### Instructions

#### 1. Clone the Repository:
```Bash
git clone https://github.com/samaritapogula/adobe_hackathon.git
cd adobe_hackathon
```
#### 2. Organize Files:

* Place your sample collections (e.g., Collection 1/, Collection 2/) in the root of the project.

* Each collection folder must contain a PDFs/ subfolder and a challenge1b_input.json file.

#### 3. Build the Docker Image:

```Bash
docker build --platform linux/amd64 -t adobe-hackathon-1b .
```

#### 4. Run the Solution:
The script is designed to automatically find and process all collection folders. The output for each collection will be saved as challenge1b_output.json inside its respective folder.

```Bash

docker run --rm -v $(pwd):/app adobe-hackathon-1b
```
