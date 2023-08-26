# Markdown 利用正则式实现 md 转 html

## 1.使用

### 1.1.普通使用

```python
    md = MarkDown()
    # 转文本
    html = md.convert(md_text)
    # 转dom树
    dom_tree = md.get_dom_tree()
```

### 1.2.自定义

```python
    config = Config(markdown_tag='my-markdown', code_tag='my-code', code_attr={'class': 'code'})
    md = MarkDown(config)
    # 转文本
    html = md.convert(md_text)
    # 转dom树
    dom_tree = md.get_dom_tree()
```

## 2. 默认基础标识

|   类型   | 对应正则式常量 |    对应 html 标签    |
| :------: | :------------: | :------------------: |
|   缩进   |     INDENT     |
|   标题   |     TITLE      |         h1~6         |
| 无序列表 |       UL       |        ul/li         |
| 有序列表 |       OL       |        ol/li         |
|   评论   |    COMMENT     |      blockquote      |
|  代码区  |      CODE      |    pre.codehilite    |
|  公式区  |    FORMULAR    | script,type=math/tex |
|   线条   |      LINE      |          hr          |
|   表格   |     TABLE      |     table/th/td      |

## 3. 默认内嵌标识

|   类型   | 对应正则式常量 |    对应 html 标签    |
| :------: | :------------: | :------------------: |
|   图片   |      IMG       |         img          |
|   链接   |      LINK      |          a           |
|   粗体   |      BOLD      |          b           |
|   斜体   |     ITALIC     |          i           |
| 内嵌代码 |     I_CODE     |    pre.codehilite    |
| 内嵌公式 |   I_FORMULAR   | script,type=math/tex |
