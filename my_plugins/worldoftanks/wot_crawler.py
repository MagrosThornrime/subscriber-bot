from bs4 import BeautifulSoup
from typing import List, Tuple, Union
import re

from data_class import Message


def get_prev_page(post_page: BeautifulSoup) -> Union[str, None]:
    """
    :return: link to previous page
    :raises AttributeError: when post_page is None
    :raises TypeError: when there is more than one
    link in 'previous page' block
    """
    link_block = post_page.find("a", title="Previous Page")
    return link_block["href"] if link_block is not None else None


def get_author(block: BeautifulSoup) -> str:
    """
    :return: post's author's name
    :raises AttributeError: when block is None
    """
    author_block = block.find(class_="author", recursive=True)
    return author_block.text.strip()


def get_date_and_time(block: BeautifulSoup) -> Tuple[str, str]:
    """
    :return: date and time of post's creation
    :raises AttributeError: when there is no member of class
    'posted_info' in block or when there are more titles
    in block with such class
    :raises TypeError: when there is no block with 'published' class
    """
    date_span_1 = block.find(class_="posted_info", recursive=True)
    date_span_2 = date_span_1.find(class_="published", recursive=True)
    date_str = date_span_2["title"]
    date, _, time = date_str.partition("T")
    return date, time


def get_title(block: BeautifulSoup) -> str:
    """
    :return: the post's author's title (e.g 'Player' or 'WG Staff')
    :raises AttributeError: when there is no block with 'basic_info' or
    'group_title' class
    """
    info_block = block.find(class_="basic_info", recursive=True)
    title_block = info_block.find(class_="group_title", recursive=True)
    return title_block.text


def get_content(block: BeautifulSoup) -> str:
    """
    :return: the message's content converted to markdown format
    :raises AttributeError: when there is no block with 'post_body' class
    """
    post_body = block.find(class_="post_body", recursive=True)
    for script in post_body.select("script"):
        script.extract()
    return post_body


def get_posts_list(posts_page: BeautifulSoup) -> List[Message]:
    """
    :return: a list of the page's messages
    :raises AttributeError: when one of helper functions raises one
    :raises TypeError: as above, but also when there is no 'id'
    in a block with 'post_block' class
    """
    posts = []
    post_blocks = posts_page("div", class_="post_block")
    for block in post_blocks:
        id_ = re.search(r"[0-9]+", block["id"])[0]
        author = get_author(block)
        date, time = get_date_and_time(block)
        title = get_title(block)
        content = get_content(block)
        post = Message(id_, author, title, date, time, content)
        post.markdownify_message(strip=["div", "input", "span"])
        posts.append(post)
    return posts


def create_soup(html_page: str) -> BeautifulSoup:
    """
    :return: a BeautifulSoup object for parsing html string
    """
    return BeautifulSoup(html_page, "html.parser")


# ------------------------------


def get_topics_list(topics_page: BeautifulSoup) -> List[Tuple[str, str]]:
    try:
        topics = []
        for link in topics_page.find_all(class_="topic_title", recursive=True):
            topics.append((link["href"], link.text.strip()))
    except (AttributeError, TypeError):
        return []
    return topics


def parse_topics_page(html_file: str) -> List[Tuple[str, str]]:
    with open(html_file, "r") as f:
        soup = BeautifulSoup(f, "html.parser")
    return get_topics_list(soup)


if __name__ == "__main__":
    html_file = "topic.html"
    # html_file = "test.html"
    posts = parse_posts_page(html_file)
    print(posts[0].content)

# spostrzeżenia: mogę zamiast zapisywać do pliku,
# przekazywać całe strony jako tekst do funkcji