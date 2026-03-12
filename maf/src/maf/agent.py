import httpx
from agent_framework import ai_function
from agent_framework.azure import AzureOpenAIResponsesClient
from azure.identity import AzureCliCredential

from maf.settings import get_settings


@ai_function
def read_tickets() -> str:
    """Read all helpdesk tickets from the ticketing system."""
    settings = get_settings()
    with httpx.Client(timeout=10) as client:
        response = client.get(f"{settings.tickets_api_base}/tickets")
        response.raise_for_status()
        tickets = response.json()

    if not tickets:
        return "No tickets found in the system."

    lines = []
    for t in tickets:
        lines.append(
            f"- Ticket #{t['id']}: [{t['priority']}] {t['subject']} "
            f"(status: {t['status']})\n  {t['description']}"
        )
    return "\n".join(lines)


def create_agent():
    settings = get_settings()
    credential = AzureCliCredential()
    client = AzureOpenAIResponsesClient(
        endpoint=settings.azure_openai_endpoint,
        deployment_name=settings.azure_openai_deployment_name,
        credential=credential,
    )
    return client.create_agent(
        name="HelpdeskAgent",
        instructions=(
            "You are a helpful helpdesk assistant. You can read tickets from the "
            "ticketing system using the read_tickets tool. When users ask about "
            "tickets, use this tool to look up current tickets. Be concise and "
            "helpful in your responses."
        ),
        tools=[read_tickets],
    )
