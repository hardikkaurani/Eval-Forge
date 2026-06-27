from typing import Any, Callable, Dict, Type


class Registry:
    """A generic class to handle dynamic registration and lookup of components."""

    def __init__(self, name: str):
        self.name = name
        self._registry: Dict[str, Type[Any]] = {}

    def register(self, key: str) -> Callable[[Type[Any]], Type[Any]]:
        """Decorator to register a class under a given key."""
        def decorator(cls: Type[Any]) -> Type[Any]:
            self._registry[key.lower()] = cls
            return cls
        return decorator

    def get(self, key: str) -> Type[Any]:
        """Lookup a registered class by key, raising KeyError if not found."""
        lowered_key = key.lower()
        if lowered_key not in self._registry:
            raise KeyError(f"'{key}' is not registered in the {self.name} registry.")
        return self._registry[lowered_key]

    def list_keys(self) -> list[str]:
        """Returns list of registered keys."""
        return list(self._registry.keys())

    def clear(self) -> None:
        """Clear all registered items (useful for testing)."""
        self._registry.clear()

provider_registry = Registry("Provider")
judge_registry = Registry("Judge")
metric_registry = Registry("Metric")

# Eagerly load providers and judges packages to trigger dynamic registration decorators
