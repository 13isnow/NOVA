kimi_prompt = """请分析txt文件写有若干文档的关键词与摘要，形式为：
                    文件名.md
                    {
                    ‘关键词’：[关键词若干]
                    ‘文章摘要‘：[摘要]
                    }

                    我需要基于文档关键词绘制知识图谱，请你总结出它们的层级关系，返回形式如下：
                    {
                    [根节点文件名]->[子节点文件名]->[子节点文件名]->……
                    [另一个根节点的文件名]->[子节点文件名]->……
                    ……
                    }
                """


class Node:

    def __init__(self, name, parent=None):
        self.parent = parent
        self.name = name


networks = """"2023秋季学期索引文档.md" -> "实践组.md" -> "任务汇报文档.md",
  "3.2 图片摘要.md" -> "识别.md" -> "思维导图.md",
  "AI_KG_doc.py.md" -> "倒排索引.md" -> "关键词.md",
  "AI_KG_doc.py.md" -> "推荐 list.md" -> "词袋模型.md",
  "AI_KG_doc.py.md" -> "KMP算法.md" -> "索引匹配.md",
  "AI_KG_doc.py.md" -> "NLP-自然语言处理.md" -> "正则表达式.md",
  "AI_KG_doc.py.md" -> "TF-IDF（1）.md" -> "搜索.md",
  "AI_KG_doc.py.md" -> "TF-IDF（2）.md" -> "相似度.md",
  "一些内容.md" -> "语雀.md" -> "知识管理.md",
  "与AI的对话.md" -> "学习.md" -> "廖雪峰.md" -> "菜鸟教程.md",
  "分支任务2汇报文档.md" -> "在线学习网站.md" -> "学习网.md",
  "回答问题.md" -> "作者.md" -> "阮一海.md",
  "大作业体会.md" -> "可视化项目.md" -> "自我评价.md",
  "如何导入文档.md" -> "作者.md" -> "阮一海.md",
  "支线：环境配置.md" -> "环境组织框架.md" -> "配置策略.md",
  "目录（先看我）.md" -> "索引算法.md" -> "分词.md",
  "目录（先看我）.md" -> "词向量.md" -> "索引匹配.md",
  "社团大作业分组2.md" -> "思政课.md" -> "Linux.md",
  "索引匹配（1）.md" -> "南京大学学生手册.md" -> "文档相似度.md",
  "索引匹配（2）.md" -> "文章推荐算法.md" -> "学生手册.md",
  "续--导出文档.md" -> "语雀.md" -> "文档导出.md",
  "认识索引算法.md" -> "索引算法.md" -> "搜索引擎.md",
  "词向量的搭建（1）.md" -> "搜索.md" -> "匹配索引.md",
  "词向量的搭建（2）.md" -> "新文章.md" -> "训练.md",
  "针对老师问题的实验性文档，勿点.md" -> "文档.md" -> "索引.md" """
networks = networks.split(',\n')
res = {}
print(networks)
for network in networks:
    net = network.split(' -> ')

"""
import AI_summarize
import os

folder_path = "D:\code\Test\Yuque\阮一海"
for filename in os.listdir(folder_path):
    # 检查文件扩展名是否为.md
    if filename.endswith('.md'):
        # 构建完整的文件路径
        file_path = os.path.join(folder_path, filename)
        file = open('test.txt', 'a', encoding='utf-8')
        # 读取Markdown文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # 如果需要，可以将Markdown转换为HTML
            keywords = AI_summarize.summarize_keywords(content)
            file.write(filename + '\n' + keywords + '\n')

        file.close()
        
        

import wikipedia

# a = wikipedia.search("python", results=2)
wikipedia.set_lang("zh")
text = wikipedia.summary("服务器")



    def logic():
        prompt = "请分析txt文件写有若干文档的关键词与摘要，形式为：
                    文件名.md
                    {
                    ‘关键词’：[关键词若干]
                    ‘文章摘要‘：[摘要]
                    }
                    
                    我需要基于文档关键词绘制知识图谱，请你总结出它们的层级关系，返回形式如下：
                    {
                    [根节点文件名]->[子节点文件名]->[子节点文件名]->……
                    [另一个根节点的文件名]->[子节点文件名]->……
                    ……
                    }
                "

    pass


"""
