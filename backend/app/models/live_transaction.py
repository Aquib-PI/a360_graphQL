from sqlalchemy import (
    Column, Integer, Text, Numeric, Boolean, DateTime, ForeignKey
)
from sqlalchemy.orm import relationship
from sqlalchemy.types import Float
from sqlalchemy import Enum as SAEnum

from .base import Base
from .enums import (
    GenderEnum, CountryCodeEnum, CreditCardTypeEnum, FundingSourceEnum,
    CreationTypeEnum, ScaTypeEnum, CurrencyEnum, StatusEnum,
    TransactionTypeEnum, RegionEnum, PaymentSuccessfulEnum
)

class LiveTransaction(Base):
    __tablename__ = "live_transactions"

    id                  = Column(Integer, primary_key=True, index=True)
    merchant_id         = Column(Integer, ForeignKey("merchant.id"), nullable=False)
    i_transaction_id    = Column(Text, nullable=True)
    e_transaction_id    = Column(Text, nullable=True)
    date_time           = Column(DateTime, nullable=False)
    credit_card_num     = Column(Text, nullable=True)
    amount              = Column(Numeric(15, 2), nullable=False)
    full_name           = Column(Text, nullable=True)
    gender              = Column(SAEnum(GenderEnum), nullable=True)
    address_line_1      = Column(Text, nullable=True)
    address_line_2      = Column(Text, nullable=True)
    city                = Column(Text, nullable=True)
    state_or_province   = Column(Text, nullable=True)
    postal_code         = Column(Text, nullable=True)
    issuer_country_code = Column(SAEnum(CountryCodeEnum), nullable=True)
    credit_card_type    = Column(SAEnum(CreditCardTypeEnum), nullable=True)
    funding_source      = Column(SAEnum(FundingSourceEnum), nullable=True)
    creation_type       = Column(SAEnum(CreationTypeEnum), nullable=True)
    sca_type            = Column(SAEnum(ScaTypeEnum), nullable=True)
    latitude            = Column(Numeric(9, 4), nullable=True)
    longitude           = Column(Numeric(9, 4), nullable=True)
    transaction_currency= Column(SAEnum(CurrencyEnum), nullable=False)
    usd_value           = Column(Numeric(15, 2), nullable=False)
    created_at          = Column(DateTime, nullable=False)
    acquirer_id         = Column(Integer, ForeignKey("acquirer.id"), nullable=False)
    ip_address          = Column(Text, nullable=True)
    status              = Column(SAEnum(StatusEnum), nullable=False)
    transaction_type    = Column(SAEnum(TransactionTypeEnum), nullable=False)
    fraud               = Column(Boolean, nullable=False)
    pred_fraud          = Column(Boolean, nullable=False)
    fraud_score         = Column(Numeric, nullable=True)
    email               = Column(Text, nullable=True)
    payment_successful  = Column(SAEnum(PaymentSuccessfulEnum), nullable=False)
    gateway_fee         = Column(Numeric, nullable=True)
    pricing_ic          = Column(Numeric, nullable=True)
    country_code        = Column(SAEnum(CountryCodeEnum), nullable=True)
    region              = Column(SAEnum(RegionEnum), nullable=True)

    merchant = relationship("Merchant", back_populates="transactions")
    acquirer = relationship("Acquirer", back_populates="transactions") 