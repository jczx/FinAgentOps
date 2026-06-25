from pathlib import Path
import sys

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = REPOSITORY_ROOT / "apps" / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.database import SessionLocal
from app.services.ml_features import build_ml_feature_rows, write_ml_feature_csv


def main() -> None:
	output_path = REPOSITORY_ROOT / "data" / "processed" / "ml_features.csv"

	with SessionLocal() as db:
		rows = build_ml_feature_rows(db)

	write_ml_feature_csv(rows, output_path)
	print(f"Wrote {len(rows)} ML feature rows to {output_path}")


if __name__ == "__main__":
	main()
