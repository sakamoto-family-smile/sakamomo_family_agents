## Asset Securities Report Agent

TBD

## Prerequisites

- Python 3.9 or higher
- [UV](https://docs.astral.sh/uv/)
- Access to an LLM and API Key


## Running the Sample

1. Navigate to the samples directory:
    ```bash
    cd xxx
    ```
2. Create an environment file with your API key:

   ```bash
   echo "GOOGLE_API_KEY=your_api_key_here" > .env
   ```

4. Run an agent:
    ```bash
    uv run .
    ```

5. In a separate terminal, run the A2A client:
    ```
    cd a2a_sdk

    # Connect to the agent (specify the agent URL with correct port)
    uv run ../../a2a_sdk/hosts/cli --agent http://localhost:10020

    # If you changed the port when starting the agent, use that port instead
    # uv run hosts/cli --agent http://localhost:YOUR_PORT
    ```
