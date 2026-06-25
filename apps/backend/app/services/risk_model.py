from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from app.db_models import FinancialMetricRecord
from app.services.ml_features import MLFeatureRow


FEATURE_COLUMNS = [
	"revenue",
	"net_income",
	"total_assets",
	"total_liabilities",
	"operating_cash_flow",
	"revenue_growth",
	"net_income_growth",
	"profit_margin",
	"debt_to_assets_ratio",
	"return_on_assets",
	"operating_cash_flow_margin",
]


@dataclass(frozen=True)
class RiskModelTrainingResult:
	model_path: Path
	metadata_path: Path
	training_rows: int
	test_rows: int
	accuracy: float | None
	precision: float | None
	recall: float | None
	f1_score: float | None
	target_positive_rate: float


@dataclass(frozen=True)
class RiskModelPrediction:
	probability: float
	label: str
	summary: str
	model_type: str
	feature_columns: list[str]


def feature_matrix(rows: list[MLFeatureRow]) -> list[list[float | None]]:
	return [[getattr(row, column) for column in FEATURE_COLUMNS] for row in rows]


def feature_vector_from_metric(metric: FinancialMetricRecord) -> list[float | None]:
	return [getattr(metric, column) for column in FEATURE_COLUMNS]


def label_for_probability(probability: float) -> str:
	if probability >= 0.65:
		return "High"
	if probability >= 0.35:
		return "Medium"

	return "Low"


def summary_for_prediction(label: str, probability: float) -> str:
	return (
		"Baseline model estimates "
		f"{label.lower()} next-year financial deterioration risk "
		f"with probability {probability:.1%}."
	)


def load_model_metadata(metadata_path: Path) -> dict:
	if not metadata_path.exists():
		return {}

	return json.loads(metadata_path.read_text(encoding="utf-8"))


def predict_risk_from_metric(
	metric: FinancialMetricRecord,
	model_path: Path,
	metadata_path: Path,
) -> RiskModelPrediction:
	if not model_path.exists():
		raise FileNotFoundError(
			f"Risk model artifact was not found at {model_path}. Train the model first.",
		)

	model = joblib.load(model_path)
	probability = float(model.predict_proba([feature_vector_from_metric(metric)])[0][1])
	label = label_for_probability(probability)
	metadata = load_model_metadata(metadata_path)

	return RiskModelPrediction(
		probability=round(probability, 4),
		label=label,
		summary=summary_for_prediction(label, probability),
		model_type=str(metadata.get("model_type", type(model).__name__)),
		feature_columns=list(metadata.get("feature_columns", FEATURE_COLUMNS)),
	)


def target_vector(rows: list[MLFeatureRow]) -> list[int]:
	return [
		row.target_next_year_deterioration
		for row in rows
		if row.target_next_year_deterioration is not None
	]


def train_risk_model(
	rows: list[MLFeatureRow],
	output_dir: Path,
	random_state: int = 42,
) -> RiskModelTrainingResult:
	training_rows = [
		row for row in rows if row.target_next_year_deterioration is not None
	]

	if len(training_rows) < 10:
		raise ValueError("At least 10 labeled feature rows are required to train the model.")

	targets = target_vector(training_rows)
	if len(set(targets)) < 2:
		raise ValueError(
			"Training requires both deterioration and non-deterioration examples.",
		)

	features = feature_matrix(training_rows)
	stratify = targets if min(targets.count(0), targets.count(1)) >= 2 else None
	x_train, x_test, y_train, y_test = train_test_split(
		features,
		targets,
		random_state=random_state,
		stratify=stratify,
		test_size=0.25,
	)

	model = Pipeline(
		steps=[
			("imputer", SimpleImputer(strategy="median")),
			(
				"classifier",
				RandomForestClassifier(
					class_weight="balanced",
					max_depth=5,
					min_samples_leaf=3,
					n_estimators=200,
					random_state=random_state,
				),
			),
		],
	)
	model.fit(x_train, y_train)

	predictions = model.predict(x_test)
	accuracy = accuracy_score(y_test, predictions)
	precision = precision_score(y_test, predictions, zero_division=0)
	recall = recall_score(y_test, predictions, zero_division=0)
	f1 = f1_score(y_test, predictions, zero_division=0)

	output_dir.mkdir(parents=True, exist_ok=True)
	model_path = output_dir / "risk_model.joblib"
	metadata_path = output_dir / "risk_model_metadata.json"
	joblib.dump(model, model_path)

	metadata = {
		"accuracy": round(float(accuracy), 4),
		"feature_columns": FEATURE_COLUMNS,
		"f1_score": round(float(f1), 4),
		"model_type": "RandomForestClassifier",
		"precision": round(float(precision), 4),
		"recall": round(float(recall), 4),
		"target_definition": (
			"1 when at least two next-year signals deteriorate: revenue, net income, "
			"profit margin, debt-to-assets, or operating cash flow."
		),
		"target_positive_rate": round(sum(targets) / len(targets), 4),
		"test_rows": len(y_test),
		"training_rows": len(y_train),
	}
	metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

	return RiskModelTrainingResult(
		model_path=model_path,
		metadata_path=metadata_path,
		training_rows=len(y_train),
		test_rows=len(y_test),
		accuracy=round(float(accuracy), 4),
		precision=round(float(precision), 4),
		recall=round(float(recall), 4),
		f1_score=round(float(f1), 4),
		target_positive_rate=round(sum(targets) / len(targets), 4),
	)
