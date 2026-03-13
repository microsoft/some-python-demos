import httpx
from agent_framework import tool
from agent_framework.azure import AzureOpenAIResponsesClient
from azure.identity import AzureCliCredential

from maf.settings import get_settings

settings = get_settings()


@tool
def read_tickets() -> str:
    """Read all helpdesk tickets from the ticketing system."""
    with httpx.Client(timeout=10) as client:
        response = client.get(f"{settings.tickets_api_base}/tickets")
        response.raise_for_status()
        tickets = response.json()

    if not tickets:
        return "No tickets found in the system."

    lines = []
    for t in tickets:
        lines.append(
            f"- Ticket #{t['id']}: [{t['priority']}] {t['subject']} (status: {t['status']})\n  {t['description']}"
        )
    return "\n".join(lines)


def create_agent():
    credential = AzureCliCredential()
    return AzureOpenAIResponsesClient(
        endpoint=settings.azure_openai_endpoint,
        deployment_name=settings.azure_openai_deployment_name,
        credential=credential,
    ).as_agent(
        name="HelpdeskAgent",
        instructions=(
            "You are a helpful helpdesk assistant. You can read tickets from the "
            "ticketing system using the read_tickets tool. When users ask about "
            "tickets, use this tool to look up current tickets. Be concise and "
            "helpful in your responses."
        ),
        tools=[read_tickets],
    )
