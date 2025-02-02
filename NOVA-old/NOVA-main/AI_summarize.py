from http import HTTPStatus
import dashscope
import json
import words_operation

import re

dashscope.api_key = "sk-b1bb53cc65204da6991fa7097705480e"


def filter_words(text):
    chinese_pattern = r'[\u4e00-\u9fff]'
    newline_pattern = r'\n+'
    punctuation_pattern = r'[ ，。；：！？《》【】「」『』（）\n ]'

    combined_pattern = f'({chinese_pattern}|{punctuation_pattern})'
    matches = re.findall(combined_pattern, text)
    result = ''.join(matches)
    result = re.sub(newline_pattern, ' ', result)
    result = re.sub(' ', '', result)
    return result


def longText_input(messages, text, over_prompt, step=6000, default='.', ):
    """

    :param messages: 消息数据，将要传给AI的数据，类型为list
    :param text: 将要input的文本
    :param over_prompt: 结束输入的指令
    :param step: 步长，如千问input限制6000token，那么step==6000
    :param default: 默认回应，如命令AI再没有输入完毕前均回应'.'，从而限制AI的发散问答
    :return: 返回处理后的messages
    """

    def body_fill(role, content):
        body = {'role': role, 'content': content}
        return body

    for i in range(0, len(text), step):
        messages.append(body_fill("user", text[i:i + step]))
        messages.append(body_fill("assistant", default))

    messages.append(body_fill("user", over_prompt))
    return messages


def summarize_keywords(text) -> str:
    text = filter_words(text)
    messages = [
        {
            'role': 'system',
            'content': """我将分块给你一篇文章让你总结，请你在我下达指令“你可以开始总结了”后输出以下格式的内容\n
                               {\n
                                    关键词:[这里你需要总结文章的关键词，注意只总结技术相关的词汇，关键词限制在3个以内]\n
                                    文章摘要:[尽可能简明地摘要文档主要内容]\n
                                }\n
                                如果我没有下达指令，请回复句号而不做其他处理。
                            """
        },
    ]
    over_prompt = """你可以开始总结了。请按照以下格式输出内容\n
                       {\n
                            '关键词':[这里你需要总结文章的关键词，注意只总结技术相关的词汇，不需要其他类型的词汇，关键词限制在3个以内]\n
                            '文章摘要':[尽可能简明地摘要文档主要内容]\n
                        }\n
                        """
    longText_input(messages, text, over_prompt, step=6000, default='.')

    response = dashscope.Generation.call(
        model='qwen-14b-chat',
        messages=messages
    )
    if response.status_code == HTTPStatus.OK:
        return response['output']['text']
    else:
        print('Failed request_id: %s, status_code: %s, code: %s, message:%s' %
              (response.request_id, response.status_code, response.code,
               response.message))


def summarize_new_topic(orig_text, new_text) -> str:
    orig_text = filter_words(orig_text)
    new_text = filter_words(new_text)
    messages = [
        {
            "role": "system",
            "content": "你将得到两份文本，前者为文档的初始版本，后者为它的更新内容，你需要比较二者的联系，总结文档更新了哪些新内容，并列出主要的变更点。"
        },
        {
            "role": "user",
            "content": f"以下是一份文档的初始版本，请仔细阅读并记住内容:{orig_text}。这是它更新的文档文本内容：{new_text}"
        }
    ]
    response = dashscope.Generation.call(
        model='qwen-14b-chat',
        messages=messages
    )
    if response.status_code == HTTPStatus.OK:
        return response['output']['text']
    else:
        print('Failed request_id: %s, status_code: %s, code: %s, message:%s' %
              (response.request_id, response.status_code, response.code,
               response.message))


def summarize_chunk(text, metadata=None, model='qwen-14b-chat'):
    print('summarize_chunk')
    if metadata is None:
        metadata = {}
    SYS_PROMPT = (
        "您的任务是从给定的上下文中提取关键的专业概念，包括但不限于科学术语、技术路径。 "
        "仅提取最重要和最基本（原子性）的概念，如果需要，将概念分解为更简单的概念。"
        "将概念归类到以下类别之一："
        "[technical term, technological path, technological concept, technical standard]\n"
        "将输出格式化为以下格式的JSON列表：\n"
        "[\n"
        "   {\n"
        '       "entity": 概念,\n'
        '       "importance": 概念在上下文中的重要性，按1到5的等级评分（5表示最高）,\n'
        '       "category": 概念类型,\n'
        "   }, \n"
        "   {\n"
        '       "entity": 另一个概念,\n'
        '       "importance": 概念在上下文中的重要性，按1到5的等级评分（5表示最高）,\n'
        '       "category": 概念类型,\n'
        "   }, \n"
        "{ …… }\n"
        "]\n"
    )
    messages = [
        {
            "role": "system",
            "content": SYS_PROMPT
        },
        {
            "role": "user",
            "content": text
        }
    ]
    response = dashscope.Generation.call(
        model=model,
        messages=messages
    )
    try:
        result = json.loads(response['output']['text'][7:-3])
        result = [dict(item, **metadata) for item in result]
    except Exception as e:
        print(e, "\n\nERROR ### Here is the buggy response: ", response, "\n\n")
        result = None
    return result


def cnt_decorate(fn):
    cnt = 0

    def wrapped(*args, **kwargs):
        nonlocal cnt
        cnt += 1
        print(f'{cnt} operate', end=' ')
        return fn(*args, **kwargs)

    return wrapped


@cnt_decorate
def summarize_network(text: str, metadata=None, model='qwen-14b-chat'):
    print('summarize_network')
    if metadata is None:
        metadata = {}

    SYS_PROMPT = (
        "您是一位网络图制作者，负责从给定的上下文中提取术语及其关系。"
        "您将获得一段上下文（由```符号界定）。您的任务是从给定的上下文中提取术语的本体。"
        "这些术语应代表上下文中的关键概念。\n"
        "思考1：在遍历每个句子时，思考其中提到的关键词。\n"
        "\t术语可能包括物体、实体、地点、组织、个人、\n"
        "\t条件、缩写、文档、服务、概念等\n"
        "\t术语应尽可能基本（原子性）。\n\n"
        "思考2：思考这些术语如何与其它术语形成一对一的关系。\n"
        "\t在同一个句子或同一段落中提到的术语通常与彼此相关。\n"
        "\t术语可以与许多其他术语相关。\n\n"
        "思考3：找出每一对相关术语之间的关系。 \n\n"
        "经过上面的思考后，你需要总结你的思考结果"
        "请将您的输出格式化为JSON列表。列表中的每个元素包含一对术语以及它们之间的关系"
        "格式如下所示：\n"
        "[\n"
        "   {\n"
        '       "node_1": "从提取的本体中的一个概念",\n'
        '       "node_2": "从提取的本体中的一个相关概念",\n'
        '       "edge": "两个概念之间，node_1和node_2的关系，用一句话或两句话描述"\n'
        "   }, {...}\n"
        "]"
    )
    USER_PROMPT = f"context: ```{text}``` \n\n output: "

    messages = [
        {
            "role": "system",
            "content": SYS_PROMPT
        },
        {
            "role": "user",
            "content": USER_PROMPT
        }
    ]
    response = dashscope.Generation.call(
        model=model,
        messages=messages
    )
    try:
        result = json.loads(response['output']['text'][7:-3])
        result = [dict(item, **metadata) for item in result]
    except Exception as e:
        print(e, "\n\nERROR ### Here is the buggy response: ", response, "\n\n")
        result = None
    return result
