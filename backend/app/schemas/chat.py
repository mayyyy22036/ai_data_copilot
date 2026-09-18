from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    answer: str


class RAGResponse(BaseModel):
    answer: str
    sources: list[str]


class SQLResponse(BaseModel):
    answer: str
    sql: str
    row_count: int


class PandasResponse(BaseModel):
    answer: str
    raw_result: dict


class AgentResponse(BaseModel):
    answer: str
    tool_used: str
    reasoning: str
    details: dict


class GraphResponse(BaseModel):
    answer: str
    evidence: list[dict]
    iterations: int
