from importlib import resources
import json

from my_plugins.plugins_abc import Plugin
from my_plugins.utils import create_modal
from plugins import register


@register("Test")
class Test(Plugin):
    def __init__(self, arguments: dict[str]):
        super().__init__(arguments)

    @classmethod
    async def modal(self):
        with resources.open_text("my_plugins.testplugin", "modal.json") as f:
            specs = json.load(f)
        return create_modal("Test", specs, ["message", "count"])

    async def get_messages(self) -> list[str]:
        message = self.arguments["message"]
        count = int(self.arguments["count"])
        messages = [message for i in range(count)]
        return messages
