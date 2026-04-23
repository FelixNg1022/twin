from typing import TypeVar

from pydantic import BaseModel

from app.services.anthropic_client import get_client

T = TypeVar("T", bound=BaseModel)


async def structured_call(
    *,
    model: str,
    system: str,
    messages: list[dict],
    output_model: type[T],
    tool_name: str,
    tool_description: str,
    max_tokens: int = 1024,
) -> T:
    """Call Claude with a forced tool use that returns a Pydantic model.

    Uses Anthropic's tool-use feature with tool_choice to force a specific
    tool call, then parses the tool_use block into the Pydantic model.
    """
    client = get_client()
    response = await client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        tools=[
            {
                "name": tool_name,
                "description": tool_description,
                "input_schema": output_model.model_json_schema(),
            }
        ],
        tool_choice={"type": "tool", "name": tool_name},
        messages=messages,
    )

    for block in response.content:
        if block.type == "tool_use" and block.name == tool_name:
            return output_model.model_validate(block.input)

    raise RuntimeError(
        f"Expected tool_use block for {tool_name}, got: "
        f"{[b.type for b in response.content]}"
    )
