"""Typed FIPA-inspired synthetic-agent protocol."""
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field

class Performative(str, Enum):
    INFORM = "INFORM"
    CFP = "CFP"
    PROPOSE = "PROPOSE"
    ACCEPT = "ACCEPT-PROPOSAL"
    REJECT = "REJECT-PROPOSAL"
    FAILURE = "FAILURE"

class AgentMessage(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    sender: str = Field(min_length=1, max_length=32)
    receiver: str = Field(min_length=1, max_length=32)
    performative: Performative
    conversation_id: str = Field(min_length=1, max_length=64)
    product: str = Field(min_length=1, max_length=80)
    quantity: int = Field(gt=0, le=100000)
    unit_price: float = Field(ge=0, le=10000000, allow_inf_nan=False)
