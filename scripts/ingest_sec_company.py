import argparse
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = REPOSITORY_ROOT / "apps" / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.database import SessionLocal, engine  # noqa: E402
from app.services.sec_ingestion import run_sec_company_ingestion  # noqa: E402


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(
		description="Ingest public SEC company facts into PostgreSQL.",
	)
	parser.add_argument(
		"--ticker",
		required=True,
		help="Ticker to ingest. The current MVP supports only AAPL.",
	)
	return parser.parse_args()


def main() -> int:
	args = parse_args()

	try:
		with SessionLocal() as db:
			records_processed = run_sec_company_ingestion(
				ticker=args.ticker,
				db=db,
				engine=engine,
			)
	except Exception as error:
		print(f"SEC ingestion failed: {error}", file=sys.stderr)
		return 1

	print(
		f"SEC ingestion completed for {args.ticker.upper()}. "
		f"Financial fact records processed: {records_processed}."
	)
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
