from sqlalchemy import Column, Integer, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy import Enum as SAEnum

from .base import Base
from .enums import (
    AnnualTurnoverEnumGBP, IndustryCategoryEnum, ProductServiceEnum,
    BusinessStructureEnum, LegalEntityTypeEnum
)

class Merchant(Base):
    __tablename__ = "merchant"

    id                     = Column(Integer, primary_key=True, index=True)
    company_name           = Column(Text, nullable=False)
    address                = Column(Text, nullable=True)
    country                = Column(Text, nullable=True)
    phone                  = Column(Text, nullable=True)
    email                  = Column(Text, unique=True, nullable=False)
    annual_turnover        = Column(SAEnum(AnnualTurnoverEnumGBP), nullable=True)
    website                = Column(Text, nullable=True)
    company_num            = Column(Text, nullable=True)
    tax_number             = Column(Text, nullable=True)
    created_at             = Column(DateTime, nullable=False)
    onboarding_person_id   = Column(Integer, nullable=True)
    industry_category      = Column(SAEnum(IndustryCategoryEnum), nullable=True)
    product_description    = Column(SAEnum(ProductServiceEnum), nullable=True)
    business_structure     = Column(SAEnum(BusinessStructureEnum), nullable=True)
    legal_entity_type      = Column(SAEnum(LegalEntityTypeEnum), nullable=True)

    transactions = relationship("LiveTransaction", back_populates="merchant") 