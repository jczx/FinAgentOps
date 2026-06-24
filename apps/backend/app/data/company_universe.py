from dataclasses import dataclass


@dataclass(frozen=True)
class CompanyMetadata:
	ticker: str
	cik: str
	name: str
	exchange: str
	sector: str


COMPANY_UNIVERSE: tuple[CompanyMetadata, ...] = (
	CompanyMetadata(
		ticker="AAPL",
		cik="0000320193",
		name="Apple Inc.",
		exchange="NASDAQ",
		sector="Technology",
	),
	CompanyMetadata(
		ticker="MSFT",
		cik="0000789019",
		name="Microsoft Corporation",
		exchange="NASDAQ",
		sector="Technology",
	),
	CompanyMetadata(
		ticker="GOOGL",
		cik="0001652044",
		name="Alphabet Inc.",
		exchange="NASDAQ",
		sector="Communication Services",
	),
	CompanyMetadata(
		ticker="AMZN",
		cik="0001018724",
		name="Amazon.com Inc.",
		exchange="NASDAQ",
		sector="Consumer Discretionary",
	),
	CompanyMetadata(
		ticker="NVDA",
		cik="0001045810",
		name="NVIDIA Corporation",
		exchange="NASDAQ",
		sector="Technology",
	),
	CompanyMetadata(
		ticker="META",
		cik="0001326801",
		name="Meta Platforms Inc.",
		exchange="NASDAQ",
		sector="Communication Services",
	),
	CompanyMetadata(
		ticker="AVGO",
		cik="0001730168",
		name="Broadcom Inc.",
		exchange="NASDAQ",
		sector="Technology",
	),
	CompanyMetadata(
		ticker="TSLA",
		cik="0001318605",
		name="Tesla Inc.",
		exchange="NASDAQ",
		sector="Consumer Discretionary",
	),
	CompanyMetadata(
		ticker="BRK.B",
		cik="0001067983",
		name="Berkshire Hathaway Inc.",
		exchange="NYSE",
		sector="Financial Services",
	),
	CompanyMetadata(
		ticker="LLY",
		cik="0000059478",
		name="Eli Lilly and Company",
		exchange="NYSE",
		sector="Healthcare",
	),
	CompanyMetadata(
		ticker="JPM",
		cik="0000019617",
		name="JPMorgan Chase & Co.",
		exchange="NYSE",
		sector="Financial Services",
	),
	CompanyMetadata(
		ticker="WMT",
		cik="0000104169",
		name="Walmart Inc.",
		exchange="NYSE",
		sector="Consumer Staples",
	),
	CompanyMetadata(
		ticker="V",
		cik="0001403161",
		name="Visa Inc.",
		exchange="NYSE",
		sector="Financial Services",
	),
	CompanyMetadata(
		ticker="ORCL",
		cik="0001341439",
		name="Oracle Corporation",
		exchange="NYSE",
		sector="Technology",
	),
	CompanyMetadata(
		ticker="MA",
		cik="0001141391",
		name="Mastercard Incorporated",
		exchange="NYSE",
		sector="Financial Services",
	),
)

COMPANY_UNIVERSE_BY_TICKER = {
	company.ticker: company for company in COMPANY_UNIVERSE
}


def supported_tickers() -> list[str]:
	return [company.ticker for company in COMPANY_UNIVERSE]


def get_company_metadata(ticker: str) -> CompanyMetadata:
	normalized_ticker = ticker.upper()
	try:
		return COMPANY_UNIVERSE_BY_TICKER[normalized_ticker]
	except KeyError as error:
		supported = ", ".join(supported_tickers())
		raise ValueError(
			f"Unsupported ticker '{normalized_ticker}'. Supported tickers: {supported}."
		) from error
