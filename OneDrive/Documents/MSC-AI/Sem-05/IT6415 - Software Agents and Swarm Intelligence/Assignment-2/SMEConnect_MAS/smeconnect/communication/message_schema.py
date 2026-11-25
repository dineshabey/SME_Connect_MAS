from enum import Enum
from pydantic import BaseModel, Field

class Performative(str, Enum):
    INFORM = "INFORM"
    CFP = "CFP"
    PROPOSE = "PROPOSE"
    ACCEPT = "ACCEPT-PROPOSAL"
    REJECT = "REJECT-PROPOSAL"
    FAILURE = "FAILURE"

class AgentMessage(BaseModel):
    sender: str
    receiver: str
    performative: Performative
    conversation_id: str
    product: str
    quantity: int = Field(gt=0)
    unit_price: float = Field(ge=0)
