from abc import ABC, abstractmethod
import aiohttp
import aiofiles
import json
import discord as dc
from discord.ui import Modal, InputText
from dataclasses import dataclass

# import wot_crawler as wot
# TODO: stworzyć foldery dla pluginów (załatwię problem wielu importów)  


@dataclass
class PluginArguments(ABC):
    pass


class Plugin(ABC):

    """
    Every task has its own Plugin instance. When asked, it produces messages
    which will be sent by the task.
    """

    def __init__(self, arguments=None):
        self.arguments = arguments

    @classmethod
    def get_children(cls):
        """
        Get all direct subclasses of this class.
        """
        chlidren_dict = {}
        for child in cls.__subclasses__():
            chlidren_dict[child.__name__] = child
        return chlidren_dict

    @abstractmethod
    async def get_messages(self) -> list[str]:
        """
        Return a list of messages prepared to send on discord.
        """
        raise NotImplementedError

    @abstractmethod
    async def modal(self) -> Modal:
        raise NotImplementedError


@dataclass
class TestArguments(PluginArguments):
    message: str = "Default message"
    count: int = 1


class TestModal(Modal):
        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)
            self.arguments = TestArguments()
            self.add_item(InputText(label="Message",
                                    style=dc.InputTextStyle.long))
            self.add_item(InputText(label="Number"))

        async def callback(self, interaction: dc.Interaction):
            self.arguments.message = self.children[0].value
            self.arguments.count = int(self.children[1].value)
            await interaction.response.send_message("Arguments passed")




class Test(Plugin):
    """
    A simple Plugin for testing.
    """

    def __init__(self, arguments: TestArguments) -> None:
        super().__init__(arguments)

    @classmethod
    def modal(self) -> TestModal:
        return TestModal(title="Plugin 'Test' is asking for arguments")

    async def get_messages(self) -> list[str]:
        message = self.arguments.message
        count = self.arguments.count
        messages = [message for i in range(count)]
        return messages


# TODO: naprawić tem szmelc
# class WotPosts(Plugin):
#     """ Crawls a topic on World Of Tanks official forum """
#     async def soup_generator(self, link):
#         async with aiohttp.ClientSession as session:
#             while link is not None:
#                 async with session.get(link) as resp:
#                     page_html = await resp.text()
#                     soup = wot.create_soup(page_html)
#                 link = wot.get_prev_page(soup)
#                 yield soup

#     async def get_messages(self, request: Request):
#         messages = []
#         async for page_soup in self.soup_generator(request.link):
#             new_messages = wot.get_posts_list(page_soup)
#             to_add = []
#             for message in reversed(new_messages):
#                 if message.id_ in request.ids:
#                     break
#                 to_add.append(message)
#                 request.ids.add(message.id_)
#             if not to_add:
#                 break
#             messages.extend(reversed(to_add))
#         request.messages = messages

#     async def get_headers(self) -> Dict[str, str]:
#         async with aiofiles.open("wot_headers.json") as f:
#             json_str = await f.read()
#         return json.loads(json_str)
