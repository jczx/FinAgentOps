from pathlib import Path
import sys

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = REPOSITORY_ROOT / "apps" / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.database import SessionLocal
from app.services.ml_features import build_ml_feature_rows, write_ml_feature_csv
from app.services.risk_model import train_risk_model


def main() -> None:
	feature_path = REPOSITORY_ROOT / "data" / "processed" / "ml_features.csv"
	model_dir = REPOSITORY_ROOT / "models"

	with SessionLocal() as db:
		rows = build_ml_feature_rows(db)

	write_ml_feature_csv(rows, feature_path)
	result = train_risk_model(rows, model_dir)

	print(f"Wrote feature dataset to {feature_path}")
	print(f"Saved model to {result.model_path}")
	print(f"Saved metadata to {result.metadata_path}")
	print(
		"Metrics: "
		f"accuracy={result.accuracy}, "
		f"precision={result.precision}, "
		f"recall={result.recall}, "
		f"f1={result.f1_score}, "
		f"positive_rate={result.target_positive_rate}"
	)


if __name__ == "__main__":
	main()
