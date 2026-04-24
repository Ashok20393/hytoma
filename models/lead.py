from pydantic import BaseModel

class Lead(BaseModel):
    name: str
    phone: str
    status: str
    salesPerson: str
    totalAmount: float = 0
    advancePaid: float = 0
    quotationSent: bool = False