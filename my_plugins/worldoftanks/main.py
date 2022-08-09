from discord.ui import Modal

from my_plugins.plugins_abc import Plugin
from plugins import register


@register(name="WorldOfTanks")
class Wot(Plugin):
    async def get_messages() -> list[str]:
        return []

    async def modal() -> Modal:
        return Modal()


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
