import sys
from main import load_or_create_system, interactive_loop

if __name__ == "__main__":
    container_name = sys.argv[1] if len(sys.argv) > 1 else "default"
    system = load_or_create_system(container_name)
    interactive_loop(system, container_name)