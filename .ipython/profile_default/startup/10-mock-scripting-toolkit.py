from pathlib import Path
import sys

tests_path = Path(__file__).parents[3] / "tests"

sys.path.insert(1, str(tests_path))
from mocks import scripting_toolkit  # noqa: E402 F401  # isort: skip
