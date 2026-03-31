from sqlalchemy import Column, Integer, String, Float, Date
from .database import Base


class Expense(Base):
    __tablename__ = "expenses"

    id          = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False)
    amount      = Column(Float,  nullable=False)
    date        = Column(Date,   nullable=False)

    def __repr__(self):
        return f"<Expense id={self.id} description={self.description!r} amount={self.amount}>"