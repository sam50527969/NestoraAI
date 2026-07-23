from app.core.workforce import workforce_registry
from app.workers.loader import worker_loader


def main() -> None:
    loaded = worker_loader.load()

    print("Loaded:", loaded)
    print("Registry:", workforce_registry.list_workers())
    print("Worker count:", workforce_registry.count())


if __name__ == "__main__":
    main()