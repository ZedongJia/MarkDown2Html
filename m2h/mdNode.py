import re
from m2h.config import Config
from typing import TypeAlias
from m2h.compiler import Compiler

# define type
Node: TypeAlias = "MarkDownNode"

INDENT = re.compile(r"^ +")


class MarkDownNode:
    r"""
    解析每一个类型的文本为对应节点
    """

    # 特殊节点标注
    UNKNOWN = "__known__"
    STRING = "__string__"
    IGNORE_SET = set([UNKNOWN, STRING])

    _config = None

    @classmethod
    def create_node(cls, **kwargs):
        r"""
        > 初始化html的dom节点
        :param tag --默认为STRING(__string__)
        :param attr --属性
        :param children --子节点, 默认为list()
        :param parent --父节点默认为None
        >>> node = MarkDownNode.create_node(tag='div', children=['hello world'], parent=None)
        >>> print(node)
        """
        return cls(**kwargs)

    def __init__(
        self,
        tag: str = None,
        attr: dict = None,
        children: list = None,
        parent=None,
        self_close=False,
    ):
        r"""
        > 初始化html的dom节点
        :param tag --默认为STRING(__string__)
        :param attr --属性
        :param children --子节点, 默认为list()
        :param parent --父节点默认为None
        >>> node = MarkDownNode(tag='div', children=['hello world'], parent=None)
        >>> print(node)
        """
        # 节点基本属性，标签、属性、父级、孩子
        self._tag = self.STRING if tag is None else tag
        self._attr = {} if attr is None else attr
        self._parent = parent
        self._children: list[MarkDownNode] = [] if children is None else children

        # 代码区或公式区的标识符
        self.block_open = False

        # 表格标识符
        self.table_open = False
        self.col_num = 0

        # 嵌套层级
        self._level = 1

        # 自闭合
        self.self_close = self_close

    @staticmethod
    def set_config(config: Config):
        r"""
        设置配置选项
        """
        # 配置
        MarkDownNode._config = config

    @property
    def _open_tag(self):
        r"""
        标签开始：<tag ?=?>
        """
        return (
            "<"
            + self._tag
            + "".join(
                [" " + str(k) + "=" + '"' + str(v) + '"' for k, v in self._attr.items()]
            )
            + ">"
        ) * self._level

    @property
    def _self_close_tag(self):
        r"""
        自闭合标签：<tag ?=? />
        """
        return (
            "<"
            + self._tag
            + "".join(
                [" " + str(k) + "=" + '"' + str(v) + '"' for k, v in self._attr.items()]
            )
            + "/>"
        )

    @property
    def _close_tag(self):
        r"""
        标签结束：</tag>
        """
        return ("</" + self._tag + ">") * self._level

    @property
    def _last_child(self):
        r"""
        获取最后一个孩子，不存在返回一个标签为`__unknown__`的节点（乐
        """
        return (
            self._children[-1]
            if len(self._children) != 0
            else MarkDownNode(tag="__unknown__")
        )

    def _remove_last(self):
        self._children.pop()

    def _append_child(self, child: Node):
        r"""
        添加孩子，并设置孩子的父亲为该节点
        :param child --MarkDownNode
        """
        if type(child) == str:
            if self._attr.get("class", None) == self._config.get("code_attr").get(
                "class", "undefined"
            ):
                child = MarkDownNode(tag="code", children=[child])
            else:
                child = MarkDownNode(tag="__string__", children=[child])

        child._parent = self
        self._children.append(child)

    def _set_attribute(self, key: str, value: str):
        r"""
        设置节点属性

        :param key --可选择['class', 'style', ...]

        :param value --可选择['test1 test2...', ...]
        """
        self._attr[key] = value

    def _get_attribute(self, key):
        r"""
        获取属性，不存在返回None
        """
        return self._attr.get(key, None)

    def convert(self, md_text: str):
        r"""
        :param md_text --输入一段markdown文本
        :return html:str --输出html文本
        """

        # 初始化
        self._children = []
        curr_level = 0
        curr_node = self

        # 文本切割
        text_list = md_text.split("\n")
        pre_text = ""

        for text in text_list:
            indent = INDENT.search(text)
            if self.block_open:
                curr_node._append_line(text=text + "\n", pre_text=pre_text)
            elif self.table_open:
                curr_node._append_line(text=text, pre_text=pre_text)
            elif indent is None:
                while curr_level > 0:
                    # 递归回归至0
                    curr_node = curr_node._parent
                    curr_level -= 1
                # 直接加入
                curr_node._append_line(text=text, pre_text=pre_text)
                # 计算level
                curr_level = 0
            else:
                # 计算缩进
                indent = indent.group()
                level = int(indent.count(" ") / 4)
                if level == curr_level:
                    curr_node._append_line(text=text.lstrip(" "), pre_text=pre_text)
                elif level - curr_level == 1:
                    # 满足条件。新建子md
                    # 新建子md
                    new_node = MarkDownNode(tag="div", parent=curr_node)
                    curr_node._append_child(new_node)
                    curr_node = new_node
                    curr_node._append_line(text=text.lstrip(" "), pre_text=pre_text)
                    # 计算level
                    curr_level = level
                elif level > curr_level:
                    # 超出太多，转为p标签
                    curr_node._append_line(
                        text=text.lstrip(" "), pre_text=pre_text, line_start=False
                    )
                else:
                    # 递归回归，至level级别
                    while level < curr_level:
                        curr_node = curr_node._parent
                        curr_level -= 1
                    curr_node._append_line(text=text.lstrip(" "), pre_text=pre_text)
            pre_text = text

        return self.to_html()

    def _append_line(
        self,
        text: str,
        pre_text: str = "",
        parent: Node = None,
        line_start: bool = True,
    ):
        r"""
        :param text --当前行的文本
        :param pre_text --上一行文本
        :param parent --当前文本所属父节点
        :param line_start --是否为行起始文本
        """
        # 当前节点指向
        node_ptr = self if parent is None else parent

        if line_start is True:
            # 预处理块级
            if Compiler.extract_enter(node_ptr, text):
                return

            # 解析代码块
            if Compiler.extract_code(node_ptr, text):
                return

            # 解析数学公式
            if Compiler.extract_formula(node_ptr, text):
                return

            # 解析table
            if Compiler.extract_table(node_ptr, text, pre_text):
                return

            # 预检查block
            if Compiler.extract_block(node_ptr, text):
                return

            # 解析标题
            if Compiler.extract_title(node_ptr, text):
                return

            # 解析列表
            if Compiler.extract_ul_ol(node_ptr, text):
                return

            # 解析内嵌注释
            if Compiler.extract_comment(node_ptr, text):
                return

            # 解析横线
            if Compiler.extract_line(node_ptr, text):
                return

        # 解析图片
        text = Compiler.extract_image(text)

        # 解析链接
        text = Compiler.extract_link(text)

        # 解析粗体
        text = Compiler.extract_bold(text)

        # 解析斜体
        text = Compiler.extract_italic(text)

        # 解析内嵌代码
        text = Compiler.extract_inner_code(
            node_ptr,
            text,
        )
        # 解析内嵌数学公式
        text = Compiler.extract_inner_formula(node_ptr, text)
        node_ptr._append_child(text)

    def to_html(self):
        r"""
        获得当前转换的html文本格式
        """
        if self.self_close:
            return self._self_close_tag

        if self._tag in self.IGNORE_SET:
            return "".join(
                [_c if type(_c) == str else _c.to_html() for _c in self._children]
            )
        else:
            return (
                self._open_tag
                + "".join(
                    [_c if type(_c) == str else _c.to_html() for _c in self._children]
                )
                + self._close_tag
            )

    def to_dict(self):
        r"""
        获得以当前节点为祖节点的dom树
        """
        if self.self_close:
            return {"tag": self._tag, "attr": self._attr}
        else:
            return {
                "tag": self._tag,
                "attr": self._attr,
                "children": [
                    _c if type(_c) == str else _c.to_dict() for _c in self._children
                ],
            }

    def __str__(self) -> str:
        return self._open_tag
