from m2h.config import Config
from m2h.mdNode import MarkDownNode


class MarkDown:
    """
    markdown文本转换
    """

    def __init__(self, config: Config = None):
        r"""
        :param `config` --自定义传入参数，or，使用默认参数

        :example
        >>> from md import MarkDown
        >>> md = MarkDown()
        >>> ...
        >>> # or
        >>> from m2h.config import Config
        >>> from md import MarkDown
        >>> config = Config(...)
        >>> md = MarkDown(config)
        >>> ...
        """
        if config is None:
            config = Config()

        self._md_node = MarkDownNode(
            tag=config.get("markdown_tag"), attr=config.get("markdown_attr")
        )
        self._md_node.set_config(config)
        self._config = config


        self._raw_markdown = None
        self._html = None
        self._tree = None

    def set_config(self, config: Config):
        self._md_node = MarkDownNode(
            tag=config.get("markdown_tag"), attr=config.get("markdown_attr")
        )
        self._md_node.set_config(config)
        self._config = config

    def _clear(self) -> None:
        r"""
        clear all
        """
        self._raw_markdown = None
        self._html = None
        self._tree = None

    def convert(self, markdown_text: str) -> str:
        r"""
        将markdown文本转换为html
        :param `markdown_text` --输入的文本
        """
        self._clear()

        self._raw_markdown = markdown_text
        self._html = self._md_node.convert(markdown_text)
        self._tree = self._md_node.to_dict()

        return self._html

    def get_html(self) -> str:
        r"""
        获取转换后的html文本
        """
        if self._html is None:
            return ""
        else:
            return self._html

    def get_dom_tree(self):
        r"""
        获取转化后的dom树
        """
        if self._tree is None:
            return {}
        else:
            return self._tree

    def __repr__(self) -> str:
        return str(self._md_node)
