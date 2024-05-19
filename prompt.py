import json
from ollama import Client as client


def extractConcepts(prompt: str, metadata=None, model='qwen-14b-chat'):
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
        "]\n"
    )
    response, _ = client.generate(model=model, system=SYS_PROMPT, prompt=prompt)
    try:
        result = json.loads(response)
        result = [dict(item, **metadata) for item in result]
    except:
        print("\n\nERROR ### Here is the buggy response: ", response, "\n\n")
        result = None
    return result


def graphPrompt(input: str, metadata={}, model='qwen-14b-chat'):
    if model == None:
        model = "mistral-openorca:latest"

    # model_info = client.show(model_name=model)
    # print( chalk.blue(model_info))

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
        "将您的输出格式化为JSON列表。列表中的每个元素包含一对术语"
        "以及它们之间的关系，如下所示：\n"
        "[\n"
        "   {\n"
        '       "node_1": "从提取的本体中的一个概念",\n'
        '       "node_2": "从提取的本体中的一个相关概念",\n'
        '       "edge": "两个概念之间，node_1和node_2的关系，用一句话或两句话描述"\n'
        "   }, {...}\n"
        "]"
    )

    USER_PROMPT = f"context: ```{input}``` \n\n output: "
    response, _ = client.generate(model=model, system=SYS_PROMPT, prompt=USER_PROMPT)
    try:
        result = json.loads(response)
        result = [dict(item, **metadata) for item in result]
    except:
        print("\n\nERROR ### Here is the buggy response: ", response, "\n\n")
        result = None
    return result
