from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.platform.models import PluginDescriptor
import structlog

logger = structlog.get_logger()


class PluginEngine:
    """Dynamic Plugin Engine.

    Manages registration, lifecycle, schema verification, and execution
    discovery of custom extension plugins (judges, metrics, providers, exporters).
    """

    def __init__(self):
        self._active_plugins: Dict[str, Any] = {}

    async def discover_plugins(self, db: AsyncSession) -> List[PluginDescriptor]:
        """Scans database descriptors to populate registered system plugins."""
        result = await db.execute(select(PluginDescriptor).where(PluginDescriptor.is_enabled == True))
        plugins = result.scalars().all()
        for p in plugins:
            self._active_plugins[p.identifier] = {
                "name": p.name,
                "version": p.version,
                "type": p.plugin_type,
                "settings": p.settings or {}
            }
        logger.info("Discovered active plugins", count=len(plugins))
        return list(plugins)

    def get_plugin(self, identifier: str) -> Optional[Dict[str, Any]]:
        return self._active_plugins.get(identifier)

    def execute_metric_plugin(self, identifier: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Simulates runtime execution of a custom metric logic plugin."""
        plugin = self.get_plugin(identifier)
        if not plugin or plugin["type"] != "metric":
            raise ValueError(f"Active metric plugin '{identifier}' not found.")

        # Simulate execution of plugin code
        weight = plugin["settings"].get("weight", 1.0)
        score = 0.85 # Mocked calculation result
        return {
            "success": True,
            "plugin": identifier,
            "metric_score": score * weight,
            "reasoning": f"Plugin evaluated CoT successfully with target settings: {plugin['settings']}."
        }


# Global plugin engine singleton
plugin_engine = PluginEngine()
