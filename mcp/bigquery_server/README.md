# BigQuery MCP Server

This is a Model Context Protocol (MCP) server that provides access to Google BigQuery. It allows AI models to interact with BigQuery through a standardized interface.

## Features

- List all datasets in a project
- List tables and their schemas in a dataset
- Execute SQL queries and get results

## Prerequisites

- Python 3.9 or later
- Google Cloud project with BigQuery enabled
- Docker (for containerization)
- gcloud CLI (for deployment)

## Setup

1. Set up Google Cloud project and authentication:
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

2. Create service account and grant permissions:
   ```bash
   make setup-sa
   ```

## Local Development

1. Install dependencies:
   ```bash
   pip install -e .
   ```

2. Run the server locally:
   ```bash
   make run-local
   ```

## Deployment to Cloud Run

1. Build and deploy to Cloud Run:
   ```bash
   make deploy
   ```

## Available Tools

### 1. List Datasets
Lists all available datasets in the project.

Example:
```json
{
  "datasets": [
    {
      "dataset_id": "example_dataset",
      "friendly_name": "Example Dataset",
      "full_dataset_id": "project-id.example_dataset"
    }
  ]
}
```

### 2. List Tables
Lists all tables and their schemas in a specified dataset.

Example:
```json
{
  "tables": [
    {
      "table_id": "example_table",
      "full_table_id": "project-id.example_dataset.example_table",
      "schema": [
        {
          "name": "column1",
          "type": "STRING",
          "mode": "REQUIRED",
          "description": "Example column"
        }
      ],
      "num_rows": 1000,
      "created": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### 3. Execute Query
Executes a SQL query and returns the results.

Example:
```json
{
  "rows": [
    {
      "column1": "value1",
      "column2": 123
    }
  ],
  "total_rows": 1,
  "schema": [
    {
      "name": "column1",
      "type": "STRING",
      "mode": "REQUIRED"
    },
    {
      "name": "column2",
      "type": "INTEGER",
      "mode": "REQUIRED"
    }
  ]
}
```

## Environment Variables

- `GOOGLE_CLOUD_PROJECT`: Google Cloud project ID (required)

## Security

The server uses a dedicated service account with minimal permissions:
- `roles/bigquery.dataViewer`: Read access to BigQuery data
- `roles/bigquery.jobUser`: Ability to run BigQuery jobs