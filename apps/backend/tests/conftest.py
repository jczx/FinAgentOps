import importlib
import sys
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


def clear_app_modules() -> None:
	for module_name in list(sys.modules):
		if module_name == "app" or module_name.startswith("app."):
			del sys.modules[module_name]


@pytest.fixture()
def client(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Generator[TestClient, None, None]:
	database_path = tmp_path / "finagentops_test.db"
	monkeypatch.setenv("DATABASE_URL", f"sqlite:///{database_path}")
	clear_app_modules()

	main_module = importlib.import_module("app.main")
	with TestClient(main_module.app) as test_client:
		yield test_client

	clear_app_modules()
