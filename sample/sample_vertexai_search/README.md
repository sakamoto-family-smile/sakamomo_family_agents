# Vertex AI Search Sample

This sample demonstrates how to use Vertex AI Search (formerly Enterprise Search) to perform searches in your data.

## Prerequisites

1. Google Cloud Project with Vertex AI Search enabled
2. Python 3.9 or later
3. `uv` package manager

## Setup

1. Clone this repository
2. Create a `.env` file in this directory with the following content:
   ```
   GCP_PROJECT_ID=your-project-id
   LOCATION=your-location  # e.g., us-central1
   SEARCH_DATASTORE_ID=your-datastore-id
   ```
3. Install dependencies:
   ```bash
   uv venv
   uv pip install -r requirements.txt
   ```

## Running the Sample

1. Activate the virtual environment:
   ```bash
   source .venv/bin/activate
   ```

2. Run the sample:
   ```bash
   python main.py
   ```

## Environment Variables

- `GCP_PROJECT_ID`: Your Google Cloud Project ID
- `LOCATION`: The location where your Vertex AI Search datastore is deployed (e.g., us-central1)
- `SEARCH_DATASTORE_ID`: The ID of your Vertex AI Search datastore

## Notes

- Make sure you have the necessary permissions to access Vertex AI Search
- The service account you're using should have the required roles to access Vertex AI Search