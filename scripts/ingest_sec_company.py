import argparse
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = REPOSITORY_ROOT / "apps" / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.data.company_universe import COMPANY_UNIVERSE, supported_tickers  # noqa: E402
from app.database import SessionLocal, engine  # noqa: E402
from app.services.sec_ingestion import run_sec_company_ingestion  # noqa: E402


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(
		description="Ingest public SEC company facts into PostgreSQL.",
	)
	ingestion_target = parser.add_mutually_exclusive_group(required=True)
	ingestion_target.add_argument(
		"--ticker",
		help=f"Ticker to ingest. Supported tickers: {', '.join(supported_tickers())}.",
	)
	ingestion_target.add_argument(
		"--all",
		action="store_true",
		help="Ingest all companies in the configured company universe.",
	)
	return parser.parse_args()


def main() -> int:
	args = parse_args()
	tickers = [company.ticker for company in COMPANY_UNIVERSE] if args.all else [args.ticker]
	total_records_processed = 0

	for ticker in tickers:
		with SessionLocal() as db:
			try:
				records_processed = run_sec_company_ingestion(
					ticker=ticker,
					db=db,
					engine=engine,
				)
			except Exception as error:
				print(f"SEC ingestion failed for {ticker.upper()}: {error}", file=sys.stderr)
				return 1

			total_records_processed += records_processed
			print(
				f"SEC ingestion completed for {ticker.upper()}. "
				f"Financial fact records processed: {records_processed}."
			)

	print(
		"SEC ingestion run completed. "
		f"Companies processed: {len(tickers)}. "
		f"Total financial fact records processed: {total_records_processed}."
	)
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
