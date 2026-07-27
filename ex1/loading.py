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


def compare_dependency_managers() -> None:
    print()
    print("PIP vs POETRY:")
    print("  installed versions right now:")
    for name in DEPENDENCIES:
        version = package_version(name)
        label = version if version is not None else "missing"
        print("    " + name.ljust(12) + label)
    print()
    rows: list[tuple[str, str, str]] = [
        ("manifest", "requirements.txt", "pyproject.toml"),
        ("lock file", "none by default", "poetry.lock"),
        ("versions", "flat pinned list", "solved constraints"),
        ("resolver", "first fit, no backtrack", "full SAT solver"),
        ("environment", "you create the venv", "Poetry creates it"),
        ("dev extras", "second requirements file", "dependency groups"),
        ("run command", "python3 loading.py", "poetry run python ..."),
    ]
    print("  " + "topic".ljust(12) + "pip".ljust(26) + "poetry")
    for topic, pip_side, poetry_side in rows:
        print("  " + topic.ljust(12) + pip_side.ljust(26) + poetry_side)


def generate_matrix_data() -> "pd.DataFrame":
    import numpy as np
    import pandas as pd

    rng = np.random.default_rng()
    sectors = np.array(["Zion", "Nebuchadnezzar", "Construct", "Loop"])
    activity_bias = np.array([-6.0, 2.0, 9.0, 18.0])
    anomaly_rate = np.array([1.5, 2.5, 3.5, 6.0])
    index = rng.integers(0, sectors.size, size=DATA_POINTS)
    frame = pd.DataFrame(
        {
            "cycle": np.arange(DATA_POINTS),
            "sector": sectors[index],
            "agent_activity": (
                rng.normal(50.0, 10.0, DATA_POINTS) + activity_bias[index]
            ),
            "code_density": rng.gamma(2.0, 8.0, DATA_POINTS),
            "anomalies": rng.poisson(anomaly_rate[index]),
        }
    )
    frame["glitch"] = frame["anomalies"] > 5
    return frame


def analyze(frame: "pd.DataFrame") -> "pd.DataFrame":
    summary = frame.groupby("sector").agg(
        mean_activity=("agent_activity", "mean"),
        mean_density=("code_density", "mean"),
        glitch_rate=("glitch", "mean"),
    )
    return summary.sort_values("mean_activity", ascending=False)


def visualize(frame: "pd.DataFrame", summary: "pd.DataFrame") -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    fig.suptitle("Matrix Data Analysis", fontsize=16)

    top_left = axes[0][0]
    top_left.hist(frame["agent_activity"], bins=40, color="#00ff41")
    top_left.set_title("Agent activity distribution")
    top_left.set_xlabel("activity")
    top_left.set_ylabel("count")

    top_right = axes[0][1]
    rolling = frame["code_density"].rolling(window=25).mean()
    top_right.plot(frame["cycle"], rolling, color="#00ff41")
    top_right.set_title("Code density (25-cycle rolling mean)")
    top_right.set_xlabel("cycle")
    top_right.set_ylabel("density")

    bottom_left = axes[1][0]
    bottom_left.bar(
        summary.index, summary["mean_activity"], color="#008f11"
    )
    bottom_left.set_title("Mean agent activity per sector")
    bottom_left.set_ylabel("activity")
    bottom_left.tick_params(axis="x", rotation=20)

    bottom_right = axes[1][1]
    bottom_right.scatter(
        frame["code_density"],
        frame["agent_activity"],
        c=frame["glitch"].map({True: "#ff0033", False: "#008f11"}),
        s=10,
        alpha=0.6,
    )
    bottom_right.set_title("Density vs activity (red = glitch)")
    bottom_right.set_xlabel("code density")
    bottom_right.set_ylabel("agent activity")

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
    visualize(frame, summary)
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
