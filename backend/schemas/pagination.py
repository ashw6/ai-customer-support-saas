from pydantic import BaseModel, ConfigDict, Field

from schemas.ticket import TicketResponse


class TicketPageData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    items: list[TicketResponse]
    total: int = Field(..., ge=0)
    page: int = Field(..., ge=1)
    limit: int = Field(..., ge=1)
    pages: int = Field(..., ge=0)


class TicketListSuccessResponse(BaseModel):
    success: bool = True
    data: TicketPageData
