from dataclasses import dataclass
from typing import Any, Callable, Dict, Type


@dataclass(frozen=True, slots=True)
class RegistryEntry:
    key: str
    component: Type[Any]
    name: str
    description: str | None = None


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

    def list_entries(self) -> list[RegistryEntry]:
        """Returns rich registry entries for metadata endpoints and plugin discovery."""
        entries: list[RegistryEntry] = []
        for key, component in self._registry.items():
            description = getattr(component, "description", None)
            if description is None:
                doc = (component.__doc__ or "").strip()
                description = doc or None
            entries.append(
                RegistryEntry(
                    key=key,
                    component=component,
                    name=getattr(component, "display_name", None)
                    or key.replace("_", " ").title(),
                    description=description,
                )
            )
        return entries

    def describe(self, key: str) -> RegistryEntry:
        component = self.get(key)
        description = getattr(component, "description", None)
        if description is None:
            doc = (component.__doc__ or "").strip()
            description = doc or None
        return RegistryEntry(
            key=key.lower(),
            component=component,
            name=getattr(component, "display_name", None)
            or key.replace("_", " ").title(),
            description=description,
        )

    def clear(self) -> None:
        """Clear all registered items (useful for testing)."""
        self._registry.clear()


provider_registry = Registry("Provider")
judge_registry = Registry("Judge")
metric_registry = Registry("Metric")

# Eagerly load providers and judges packages to trigger dynamic registration decorators
import app.evaluation.judges  # noqa: F401, E402
import app.evaluation.providers  # noqa: F401, E402
import app.evaluation.metrics  # noqa: F401, E402
