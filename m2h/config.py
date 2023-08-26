from typing import TypeAlias

# define type
ReturnValue: TypeAlias = str | dict | None


class Config:
    def __init__(self, **config):
        r"""
        `[OPTIONAL]`
        ```
        markdown_tag   : str  = ?,

        markdown_attr  : str  = ?,

        code_tag       : str  = ?,

        code_attr      : dict = ?,

        formula_tag    : str  = ?,

        formula_attr   : dict = ?,

        comment_tag    : str  = ?,
        ```
        """
        self._config = {
            "markdown_tag": "div"
            if config.get("markdown_tag", None) is None
            else config.get("markdown_tag", None),
            "markdown_attr": {"class": "markdown-body"}
            if config.get("markdown_attr", None) is None
            else config.get("markdown_attr", None),
            "code_tag": "pre"
            if config.get("code_tag", None) is None
            else config.get("code_tag", None),
            "code_attr": {"class": "codehilite"}
            if config.get("code_attr", None) is None
            else config.get("code_attr", None),
            "formula_tag": "script"
            if config.get("formula_tag", None) is None
            else config.get("formula_tag", None),
            "formula_attr": {"type": "math/tex"}
            if config.get("formula_attr", None) is None
            else config.get("formula_attr", None),
            "comment_tag": "blockquote"
            if config.get("comment_tag", None) is None
            else config.get("comment_tag", None),
        }

    def get(self, _key, _default=None) -> ReturnValue:
        return self._config.get(_key, _default)
