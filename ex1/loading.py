import importlib.metadata
import importlib.util
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


DEPENDENCIES: dict[str, str] = {
    "pandas": "Data manipulation",
    "numpy": "Numerical computation",
    "matplotlib": "Visualization",
}

DATA_POINTS: int = 1000
OUTPUT_FILE: str = "matrix_analysis.png"


def package_version(name: str) -> str | None:
    if importlib.util.find_spec(name) is None:
        return None
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def check_dependencies() -> list[str]:
    missing: list[str] = []
    print("Checking dependencies:")
    for name, role in DEPENDENCIES.items():
        version = package_version(name)
        if version is None:
            missing.append(name)
            print("[KO] " + name + " (not installed) - " + role + " not ready")
        else:
            print("[OK] " + name + " (" + version + ") - " + role + " ready")
    return missing


def print_install_instructions(missing: list[str]) -> None:
    print()
    print("LOADING FAILED: missing programs -> " + ", ".join(missing))
    print()
    print("Load them with pip:")
    print("    python3 -m venv matrix_env")
    print("    source matrix_env/bin/activate")
    print("    pip install -r requirements.txt")
    print()
    print("Or load them with Poetry:")
    print("    poetry install")
    print("    poetry run python loading.py")


def detect_manager() -> str:
    if "pypoetry" in sys.prefix:
        return "Poetry virtual env (" + sys.prefix + ")"
    if sys.prefix != sys.base_prefix:
        return "pip virtual env (" + sys.prefix + ")"
    return "global Python, no virtual env (" + sys.prefix + ")"


def read_file_lines(path: str) -> list[str]:
    try:
        with open(path) as file:
            return file.read().splitlines()
    except OSError:
        return []


def read_requirements() -> dict[str, str]:
    rules: dict[str, str] = {}
    for line in read_file_lines("requirements.txt"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        cut = len(line)
        for sign in "<>=!~":
            position = line.find(sign)
            if position != -1 and position < cut:
                cut = position
        rules[line[:cut].strip()] = line[cut:].strip()
    return rules


def marker_matches(marker: str) -> bool:
    parts = marker.replace('\\"', "").split()
    if len(parts) != 3 or parts[0] != "python_version":
        return True
    wanted = int(parts[2].split(".")[1])
    current = sys.version_info.minor
    if parts[1] == "==":
        return current == wanted
    if parts[1] == ">=":
        return current >= wanted
    if parts[1] == "<":
        return current < wanted
    return True


def read_poetry_lock() -> dict[str, str]:
    locked: dict[str, str] = {}
    name = ""
    version = ""
    marker = ""
    for line in read_file_lines("poetry.lock") + ["[[package]]"]:
        if line == "[[package]]":
            if name and marker_matches(marker):
                locked[name] = version
            name = version = marker = ""
        elif line.startswith("name = "):
            name = line.split('"')[1]
        elif line.startswith("version = "):
            version = line.split('"')[1]
        elif line.startswith("markers = "):
            marker = line[len('markers = "'):-1]
    return locked


def compare_dependency_managers() -> None:
    print()
    print("PIP vs POETRY:")
    print("  running in: " + detect_manager())
    print()
    rules = read_requirements()
    locked = read_poetry_lock()
    print(
        "  " + "package".ljust(12) + "rule".ljust(10)
        + "poetry.lock".ljust(14) + "installed here"
    )
    for name in DEPENDENCIES:
        rule = rules.get(name, "?")
        version = package_version(name)
        installed = version if version is not None else "missing"
        lock = locked.get(name, "no lock")
        print(
            "  " + name.ljust(12) + rule.ljust(10)
            + lock.ljust(14) + installed
        )
    if not locked:
        print("  (no poetry.lock yet: run 'poetry install' to create it)")
    print()
    print("  pip installs the newest version that matches the rule,")
    print("  so the result depends on the day you install.")
    print("  Poetry installs exactly what poetry.lock says,")
    print("  so every machine gets the same versions.")
    print()
    rows: list[tuple[str, str, str]] = [
        ("dependency file", "requirements.txt", "pyproject.toml"),
        ("lock file", "none", "poetry.lock (exact versions)"),
        ("virtual env", "you create and activate", "Poetry creates it"),
        ("install", "pip install -r requirements.txt", "poetry install"),
        ("run", "python3 loading.py", "poetry run python loading.py"),
    ]
    print("  " + "topic".ljust(17) + "pip".ljust(33) + "poetry")
    for topic, pip_side, poetry_side in rows:
        print("  " + topic.ljust(17) + pip_side.ljust(33) + poetry_side)


def generate_matrix_data() -> "pd.DataFrame":
    import numpy as np
    import pandas as pd

    rng = np.random.default_rng()
    frame = pd.DataFrame(
        {"signal": rng.uniform(0.0, 100.0, DATA_POINTS)}
    )
    return frame


def analyze(frame: "pd.DataFrame") -> "pd.DataFrame":
    return frame.describe()


def visualize(frame: "pd.DataFrame") -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(frame["signal"], bins=20, color="#00ff41")
    ax.set_title("Matrix signal distribution")
    ax.set_xlabel("signal")
    ax.set_ylabel("count")

    fig.tight_layout()
    fig.savefig(OUTPUT_FILE, dpi=120)
    plt.close(fig)


def run_analysis() -> None:
    print()
    print("Analyzing Matrix data...")
    frame = generate_matrix_data()
    print("Processing " + str(len(frame)) + " data points...")
    summary = analyze(frame)
    print()
    print(summary.round(2).to_string())
    print()
    print("Generating visualization...")
    visualize(frame)
    print("Analysis complete!")
    print("Results saved to: " + OUTPUT_FILE)


def main() -> int:
    print("LOADING STATUS: Loading programs...")
    print()
    missing = check_dependencies()
    if missing:
        print_install_instructions(missing)
        compare_dependency_managers()
        return 1
    run_analysis()
    compare_dependency_managers()
    return 0


if __name__ == "__main__":
    sys.exit(main())
