from sqlalchemy import Column, Integer, String

from app.database.database import Base


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)

    business_name = Column(String, nullable=False)
    category = Column(String)
    location = Column(String)

    phone = Column(String)
    email = Column(String)
    website = Column(String)

    status = Column(String, default="New")