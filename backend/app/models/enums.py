import enum

# Example values—replace with your actual DB enum definitions
class GenderEnum(enum.Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"

class CountryCodeEnum(enum.Enum):
    US = "US"
    GB = "GB"
    IN = "IN"
    BG = "BG"
    RO = "RO"
    HU = "HU"
    CZ = "CZ"
    PL = "PL"
    RU = "RU"
    UA = "UA"
    MX = "MX"
    BR = "BR"
    CL = "CL"
    CO = "CO"
    PE = "PE"
    AR = "AR"

    # ...add all ISO codes you support

class CreditCardTypeEnum(enum.Enum):
    VISA = "VISA"
    MASTERCARD = "MASTERCARD"
    AMEX = "AMEX"
    DINERS = "DINERS"
    JCB = "JCB"
    DISCOVER = "DISCOVER"
    UNIONPAY = "UNIONPAY"
    MAESTRO = "MAESTRO"
    MIR = "MIR"
    # ...etc

class FundingSourceEnum(enum.Enum):
    CREDIT = "CREDIT"
    DEBIT = "DEBIT"
    PREPAID = "PREPAID"

class CreationTypeEnum(enum.Enum):
    ECOM = "ECOM"
    RECURRING = "RECURRING"
    STORED_ACCOUNT = "STORED_ACCOUNT"
   

class ScaTypeEnum(enum.Enum):
    NO_SCA = "NO_SCA"
    TRA = "TRA"
    EXEMPTION_LOW_VALUE = "EXEMPTION_LOW_VALUE"
    THREEDS_2_0 = "THREEDS_2_0"

class CurrencyEnum(enum.Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    BGN = "BGN"
    RON = "RON"
    HUF = "HUF"
    CZK = "CZK"
    PLN = "PLN"
    RUB = "RUB"
    UAH = "UAH"
    INR = "INR"
    MXN = "MXN"
    BRL = "BRL"
    CLP = "CLP"
    COP = "COP"
    PEN = "PEN"
    ARS = "ARS"
    # ...other currencies

class StatusEnum(enum.Enum):
    PAY_SETTLED = "PAY_SETTLED"


class TransactionTypeEnum(enum.Enum):
    PAYMENT = "PAYMENT"

class RegionEnum(enum.Enum):
    INTER = "INTER"
    INTRA = "INTRA"
    DOMESTIC = "DOMESTIC"

class PaymentSuccessfulEnum(enum.Enum):
    TRUE = "true"
    FALSE = "false"

# Business-specific enums for merchants
class AnnualTurnoverEnumGBP(enum.Enum):
    BELOW_100K = "LESS THAN £100K"
    _100K_TO_500K = "£100K-£500K"
    _500K_TO_1M = "£500K-£1M"
    ABOVE_1M = "ABOVE £1M"
    NOT_APPLICABLE = "NOT APPLICABLE"

class IndustryCategoryEnum(enum.Enum):
    FINANCE = "finance"
    RETAIL = "retail"
    TECHNOLOGY = "technology"
    # ...etc

class ProductServiceEnum(enum.Enum):
    HARDWARE = "hardware"
    SOFTWARE = "software"
    SERVICE = "service"

class BusinessStructureEnum(enum.Enum):
    LLC = "LLC"
    CORPORATION = "corporation"
    SOLE_PROPRIETORSHIP = "sole_proprietorship"

class LegalEntityTypeEnum(enum.Enum):
    PRIVATE = "private"
    PUBLIC = "public"
    NON_PROFIT = "non_profit" 