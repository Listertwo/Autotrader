"""Logger: log files live in the project's logs folder no matter where the program is started from."""
import json
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # project root, so "tests.x" and "backtest.x" imports work
from tests._helpers import *
from config import LOG_DIR

# Runs in a brand-new Python process so we see the logger exactly as it is when first imported.
PROBE = """
import importlib, json, logging
import utils.logger as lg
first = len(lg.logger.handlers)
importlib.reload(lg)                      # importing/reloading twice must not add duplicate handlers
print(json.dumps({
    "files": [h.baseFilename for h in lg.logger.handlers if isinstance(h, logging.FileHandler)],
    "propagate": lg.logger.propagate,
    "handlers_first": first,
    "handlers_after_reload": len(lg.logger.handlers),
    "level": lg.logger.level,
}))
"""


def probe_from(cwd):
    env = dict(os.environ, PYTHONPATH=ROOT)
    out = subprocess.run([sys.executable, "-c", PROBE], cwd=cwd, env=env, capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout.strip().splitlines()[-1])


def test_log_files_go_to_project_logs_folder_not_the_working_directory():
    with tempfile.TemporaryDirectory() as elsewhere:
        info = probe_from(elsewhere)
        expected = sorted(str((LOG_DIR / name).resolve()) for name in ("application.log", "error.log"))
        assert sorted(os.path.realpath(p) for p in info["files"]) == sorted(os.path.realpath(p) for p in expected)
        assert os.listdir(elsewhere) == [], "logger created files/folders in the working directory"


def test_handlers_are_not_duplicated_and_records_do_not_double_print():
    with tempfile.TemporaryDirectory() as elsewhere:
        info = probe_from(elsewhere)
        assert info["handlers_first"] == 3                       # application, error, console
        assert info["handlers_after_reload"] == 3
        assert info["propagate"] is False                        # otherwise every console line prints twice
        assert info["level"] == logging.DEBUG


def test_log_folder_is_inside_the_project():
    assert os.path.realpath(str(LOG_DIR)).startswith(os.path.realpath(ROOT))


if __name__ == "__main__":
    sys.exit(1 if run_tests(globals(), "Logger") else 0)
