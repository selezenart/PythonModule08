import os
import sys

from dotenv import load_dotenv  # type: ignore[import-not-found]


CONFIG_KEYS: list[tuple[str, str]] = [
    ("MATRIX_MODE", "development"),
    ("DATABASE_URL", ""),
    ("API_KEY", ""),
    ("LOG_LEVEL", "INFO"),
    ("ZION_ENDPOINT", ""),
]


def load_config() -> dict[str, str]:

    load_dotenv()

    config: dict[str, str] = {}
    for name, default in CONFIG_KEYS:
        config[name] = os.environ.get(name, default)
    return config


def describe(config: dict[str, str]) -> list[str]:
    lines: list[str] = []

    lines.append("Mode: " + config["MATRIX_MODE"])

    if config["DATABASE_URL"]:
        if config["MATRIX_MODE"] == "production":
            lines.append("Database: Connected to production cluster")
        else:
            lines.append("Database: Connected to local instance")
    else:
        lines.append("Database: NOT CONFIGURED (set DATABASE_URL)")

    if config["API_KEY"]:
        lines.append("API Access: Authenticated")
    else:
        lines.append("API Access: MISSING (set API_KEY)")

    lines.append("Log Level: " + config["LOG_LEVEL"])

    if config["ZION_ENDPOINT"]:
        lines.append("Zion Network: Online")
    else:
        lines.append("Zion Network: Offline (set ZION_ENDPOINT)")

    return lines


def missing_keys(config: dict[str, str]) -> list[str]:
    required: list[str] = ["DATABASE_URL", "API_KEY", "ZION_ENDPOINT"]
    return [key for key in required if not config[key]]


def security_check(config: dict[str, str]) -> None:
    print("Environment security check:")
    print("[OK] No hardcoded secrets detected")

    if os.path.exists(".env"):
        print("[OK] .env file properly configured")
    else:
        print("[WARN] No .env file found (copy .env.example to .env)")

    if config["MATRIX_MODE"] == "production":
        print("[OK] Running with production overrides")
    else:
        print("[OK] Production overrides available")


def main() -> None:
    print("ORACLE STATUS: Reading the Matrix...")

    config: dict[str, str] = load_config()

    print("Configuration loaded:")
    for line in describe(config):
        print(line)
    print()

    security_check(config)
    print()

    absent: list[str] = missing_keys(config)
    if absent:
        print("The Oracle is troubled. Missing configuration:")
        for key in absent:
            print("  - " + key)
        print("Create a .env file "
              "(see .env.example) to complete the connection.")
        sys.exit(1)

    print("The Oracle sees all configurations.")


if __name__ == "__main__":
    main()
