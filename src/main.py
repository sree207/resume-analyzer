from utils.version import get_python_version

def main():
    """Main entry point of the application."""
    version = get_python_version()
    print(f"Hello Python v{version}!")