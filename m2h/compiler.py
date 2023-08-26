import re

TITLE = re.compile(r"^(\#{1,6} )(.*)")
UL = re.compile(r"^([+-]) (.*)")
OL = re.compile(r"^(\d+\.) (.*)")
COMMENT = re.compile(r"^(\>+)(.*)")
CODE = re.compile(r"^(\`\`\`)(.*)")
FORMULAR = re.compile(r"^(\$\$)(.*)")
LINE = re.compile(r"^[ -]*-{3,}[ -]*$")
TABLE = re.compile(r"^ *\|?(?:[\-\: ]+\|)+[\-\: ]+\|? *$")
# order
IMG = re.compile(r"!\[([^\[]*)\]\(([^\(]*)\)")
LINK = re.compile(r"\[([^\[]*)\]\(([^\(]*)\)")
BOLD = re.compile(r"(?:\*\*[^\*]*\*\*|\_\_[^\_]*\_\_)")
ITALIC = re.compile(r"(?:\*[^\*]*\*|\_[^\_]*\_)")
I_CODE = re.compile(r"\`([^\`]*)\`")
I_FORMULAR = re.compile(r"\$([^\$]*)\$")


class Compiler:
    @staticmethod
    def extract_title(parent, text):
        m_title = TITLE.search(text)
        if m_title is not None:
            # 提取title
            m_title, new_text = m_title.groups()

            # 得到node
            level = m_title.count("#")
            t_node = parent.create_node(tag="h" + str(level))
            parent._append_child(t_node)

            # 提取剩余部分
            parent._append_line(text=new_text, parent=t_node, line_start=False)
            return True
        return False

    @staticmethod
    def extract_ul_ol(parent, text):
        m_ul = UL.search(text)
        if m_ul is not None:
            _, new_text = m_ul.groups()
            if parent._last_child._tag == "ul":
                li = parent.create_node(tag="li")
                parent._last_child._append_child(li)
            else:
                ul = parent.create_node(tag="ul")
                li = parent.create_node(tag="li")
                ul._append_child(li)
                parent._append_child(ul)
            # 提取剩余部分
            parent._append_line(text=new_text, parent=li, line_start=False)
            return True

        m_ol = OL.search(text)
        if m_ol is not None:
            _, new_text = m_ol.groups()
            if parent._last_child._tag == "ol":
                li = parent.create_node(tag="li")
                parent._last_child._append_child(li)
            else:
                ol = parent.create_node(tag="ol")
                li = parent.create_node(tag="li")
                ol._append_child(li)
                parent._append_child(ol)
            # 提取剩余部分
            parent._append_line(text=new_text, parent=li, line_start=False)
            return True
        return False

    @staticmethod
    def extract_comment(parent, text):
        m_comment = COMMENT.search(text)
        if m_comment is not None:
            m_comment, content = m_comment.groups()
            level = m_comment.count(">")
            if (
                parent._last_child._tag == parent._config.get("comment_tag")
                and parent._last_child._level >= level
            ):
                node = parent._last_child
            else:
                node = parent.create_node(tag=parent._config.get("comment_tag"))
                node._level = level
                parent._append_child(node)
            parent._append_line(text=content.lstrip(" "), parent=node)
            return True
        return False

    @staticmethod
    def extract_code(parent, text):
        m_code = CODE.search(text)
        if m_code is not None:
            if parent.block_open:
                parent.block_open = False
                return True
            parent.block_open = True
            m_code, language = m_code.groups()
            node = parent.create_node(
                tag=parent._config.get("code_tag"), attr=parent._config.get("code_attr")
            )

            if language != "":
                node._set_attribute("language", language)
            parent._append_child(node)
            return True
        return False

    @staticmethod
    def extract_formula(
        parent,
        text,
    ):
        m_formula = FORMULAR.search(text)
        if m_formula is not None:
            if parent.block_open:
                parent.block_open = False
                return True
            parent.block_open = True
            m_formula, _ = m_formula.groups()
            node = parent.create_node(
                tag=parent._config.get("formula_tag"),
                attr=parent._config.get("formula_attr"),
            )
            parent._append_child(node)
            return True
        return False

    @staticmethod
    def extract_block(parent, text):
        if parent.block_open:
            node = parent._last_child
            # 代码块
            # 数学公式
            node._append_child(text)
            return True
        return False

    @staticmethod
    def extract_line(parent, text):
        m_line = LINE.search(text)
        if m_line is not None:
            line = parent.create_node(tag="hr")
            parent._append_child(line)
            return True
        return False

    @staticmethod
    def extract_table(parent, text: str, pre_text: str):
        # extract table-data
        if parent.table_open:
            tbody = text.strip(" ").strip("|").split("|")
            for idx, item in enumerate(tbody):
                if item.find("\\") != -1:
                    tbody[idx] = item + "|"
                    tbody.pop(idx + 1)

            tr = parent.create_node(tag="tr")
            # 转为th
            for i in range(parent.col_num):
                if i < len(tbody):
                    th = parent.create_node(tag="td")
                    parent._append_line(text=tbody[i], parent=th, line_start=False)
                    tr._append_child(th)
                else:
                    tr._append_child(parent.create_node(tag="td"))
            parent._last_child._append_child(tr)
            return True

        m_table = TABLE.search(text)
        # extract table
        if m_table is not None and not parent.table_open:
            table_form = m_table.group().strip(" ").strip("|")
            parent.col_num = len(table_form.split("|"))

            table = parent.create_node(tag="table")

            # 获取headers
            headers = pre_text.strip(" ").strip("|").split("|")
            for idx, item in enumerate(headers):
                if item.find("\\") != -1:
                    headers[idx] = item + "|"
                    headers.pop(idx + 1)
            if len(headers) == parent.col_num:
                # 满足条件则提取table
                parent.table_open = True
                parent._remove_last()

                tr = parent.create_node(tag="tr")
                # 转为th
                for i in range(parent.col_num):
                    if i < len(headers):
                        th = parent.create_node(tag="th")
                        parent._append_line(
                            text=headers[i], parent=th, line_start=False
                        )
                        tr._append_child(th)
                    else:
                        tr._append_child(parent.create_node(tag="th"))
                table._append_child(tr)
                parent._append_child(table)
                return True
        return False

    @staticmethod
    def extract_enter(parent, text):
        if text == "":
            parent.table_open = False
            parent._append_child(parent.create_node(tag="br", self_close=True))
            return True
        return False

    @staticmethod
    def extract_image(text):
        m_img_list = IMG.findall(text)
        for m_img in m_img_list:
            content, src = m_img
            text = text.replace(
                "![%s](%s)" % m_img, '<img src="%s" alt="%s"/>' % (src, content)
            )
        return text

    @staticmethod
    def extract_link(text):
        m_link_list = LINK.findall(text)
        for m_link in m_link_list:
            content, href = m_link
            text = text.replace(
                "[%s](%s)" % m_link, '<a href="%s">%s</a>' % (href, content)
            )
        return text

    @staticmethod
    def extract_bold(text):
        m_bold_list = BOLD.findall(text)
        for m_bold in m_bold_list:
            symbol = m_bold[0]
            if symbol == "*":
                content = m_bold.strip("*")
                text = text.replace(m_bold, "<b>%s</b>" % content)
            else:
                content = m_bold.strip("_")
                text = text.replace(m_bold, "<b>%s</b>" % content)
        return text

    @staticmethod
    def extract_italic(text):
        m_italic_list = ITALIC.findall(text)
        for m_italic in m_italic_list:
            symbol = m_italic[0]
            if symbol == "*":
                content = m_italic.strip("*")
                text = text.replace(m_italic, "<i>%s</i>" % content)
            else:
                content = m_italic.strip("_")
                text = text.replace(m_italic, "<i>%s</i>" % content)
        return text

    @staticmethod
    def extract_inner_code(parent, text):
        m_code_list = I_CODE.findall(text)
        for m_code in m_code_list:
            code = parent.create_node(
                # tag=parent._config.get("code_tag"),
                tag="code",
                attr=parent._config.get("code_attr"),
                children=[m_code],
            )
            text = text.replace("`%s`" % m_code, "%s" % code.to_html())

        return text

    @staticmethod
    def extract_inner_formula(parent, text):
        m_math_list = I_FORMULAR.findall(text)
        for m_math in m_math_list:
            formula = parent.create_node(
                tag=parent._config.get("formula_tag"),
                attr=parent._config.get("formula_attr"),
                children=[m_math],
            )
            text = text.replace("$%s$" % m_math, "%s" % formula.to_html())
        return text
