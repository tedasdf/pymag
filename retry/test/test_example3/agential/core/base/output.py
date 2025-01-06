"""Base class for agents and prompting method outputs."""

from typing import Any

from pydantic import BaseModel, Field


class BaseOutput(BaseModel):
    """Base class for structured method outputs.

    Attributes:
        answer (str): The answer generated by the method.
        total_prompt_tokens (int): The total number of input tokens used.
        total_completion_tokens (int): The total number of output tokens used.
        total_tokens (int): The total number of tokens used.
        total_cost (float): The total cost of the output.
        total_prompt_cost (float): The total cost of the prompt tokens.
        total_completion_cost (float): The total cost of the completion tokens.
        total_prompt_time (float): The total time taken for the LLM API to generate the outputs in seconds.
        total_time (float): The total time for the method to finish generating in seconds.
        additional_info (Any): A general attribute for additional information.
    """

    answer: str = Field(..., description="The answer generated by the method.")
    total_prompt_tokens: int = Field(..., description="Total input tokens used.")
    total_completion_tokens: int = Field(..., description="Total output tokens used.")
    total_tokens: int = Field(..., description="Total tokens used.")
    total_prompt_cost: float = Field(
        ..., description="Total cost of the prompt tokens."
    )
    total_completion_cost: float = Field(
        ..., description="Total cost of the completion tokens."
    )
    total_cost: float = Field(..., description="Total cost of the output.")
    total_prompt_time: float = Field(
        ...,
        description="Total time taken for the LLM API to generate the outputs in seconds.",
    )
    total_time: float = Field(
        ...,
        description="Total time for the method to finish generating in seconds.",
    )
    additional_info: Any = Field(
        ..., description="Additional information related to the output."
    )