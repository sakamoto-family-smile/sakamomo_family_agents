"""This file serves as the main entry point for the application.

It initializes the A2A server, defines the agent's capabilities,
and starts the server to handle incoming requests.
"""

from agent import AssetSecuritiesReportAgent, AssetSecuritiesReportAgentConfig
import click
from common.server import A2AServer
from common.types import (
    AgentCapabilities, AgentCard, AgentSkill, MissingAPIKeyError
)
import logging
import os
from task_manager import AgentTaskManager
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@click.command()
@click.option("--host", "host", default="localhost")
@click.option("--port", "port", default=10020)
def main(host, port):
    """Entry point for the A2A + analyze the financial report using agent."""
    try:
        if not os.getenv("GOOGLE_API_KEY"):
            raise MissingAPIKeyError("GOOGLE_API_KEY environment variable not set.")
        if not os.getenv("EDINET_API_KEY"):
            raise MissingAPIKeyError("EDINET_API_KEY environment variable not set.")
        if not os.getenv("GCP_PROJECT"):
            raise MissingAPIKeyError("GCP_PROJECT environment variable not set.")
        if not os.getenv("GCS_LOG_BUCKET_NAME"):
            raise MissingAPIKeyError("GCS_LOG_BUCKET_NAME environment variable not set.")
        if not os.getenv("LLM_MODEL_NAME"):
            # llm model nameは設定されていないケースも許容しても良さそう
            raise MissingAPIKeyError("LLM_MODEL_NAME environment variable not set.")

        capabilities = AgentCapabilities(streaming=False)
        skill = AgentSkill(
            id="asset_securities_report_agent",
            name="Asset Securities Report",
            description=(
                "Based on the company name, I will search for the relevant annual securities report (Yukashoken Hokokusho), "
                "analyze the report from multiple perspectives (such as management strategy, financial condition, and governance), "
                "and then forecast the company's recent stock price based on the analysis of each perspective."
            ),
            tags=["analyze financial report", "analyze asset securities report"],
            examples=["Please translate the following into English and analyze ACCESS Co., Ltd.'s annual securities report."],
        )

        agent_card = AgentCard(
            name="Asset Securities Report",
            description=(
                "Based on the company name, I will search for the relevant annual securities report (Yukashoken Hokokusho), "
                "analyze the report from multiple perspectives (such as management strategy, financial condition, and governance), "
                "and then forecast the company's recent stock price based on the analysis of each perspective."
            ),
            url=f"http://{host}:{port}/",
            version="0.0.1",
            defaultInputModes=AssetSecuritiesReportAgent.get_supported_content_types(),
            defaultOutputModes=AssetSecuritiesReportAgent.get_supported_content_types(),
            capabilities=capabilities,
            skills=[skill],
        )

        config = AssetSecuritiesReportAgentConfig(
            log_bucket_name=str(os.getenv("GCS_LOG_BUCKET_NAME")),
            llm_model_name=str(os.getenv("LLM_MODEL_NAME")),
        )
        server = A2AServer(
            agent_card=agent_card,
            task_manager=AgentTaskManager(
                agent=AssetSecuritiesReportAgent(config=config)
            ),
            host=host,
            port=port,
        )
        logger.info(f"Starting server on {host}:{port}")
        server.start()
    except MissingAPIKeyError as e:
        logger.error(f"Error: {e}")
        exit(1)
    except Exception as e:
        logger.error(f"An error occurred during server startup: {e}")
        exit(1)


if __name__ == "__main__":
    main()
