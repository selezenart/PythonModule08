import os
import sys
import site


def in_virtual_environment():
    if os.environ.get("VIRTUAL_ENV"):
        return True
    return sys.prefix != getattr(sys, "base_prefix", sys.prefix)


def package_path():
    try:
        paths = site.getsitepackages()
        if paths:
            return paths[0]
    except AttributeError:
        pass
    return site.getusersitepackages()


def show_plugged_in():
    print("MATRIX STATUS: You're still plugged in")
    print("Current Python: " + sys.executable)
    print("Virtual Environment: None detected")
    print()
    print("WARNING: You're in the global environment!")
    print("The machines can see everything you install.")
    print()
    print("To enter the construct, run:")
    print("    python -m venv matrix_env")
    print("    source matrix_env/bin/activate    # On Unix")
    print("    matrix_env\\Scripts\\activate       # On Windows")
    print()
    print("Then run this program again.")


def show_in_construct():
    env_path = os.environ.get("VIRTUAL_ENV", sys.prefix)
    env_name = os.path.basename(env_path)
    print("MATRIX STATUS: Welcome to the construct")
    print("Current Python: " + sys.executable)
    print("Virtual Environment: " + env_name)
    print("Environment Path: " + env_path)
    print()
    print("SUCCESS: You're in an isolated environment!")
    print("Safe to install packages without affecting")
    print("the global system.")
    print()
    print("Package installation path:")
    print(package_path())


def main():
    if in_virtual_environment():
        show_in_construct()
    else:
        show_plugged_in()


if __name__ == "__main__":
    main()
