import os
import json
from openai import OpenAI
from tools import calculate

# 1. 创建客户端
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    base_url=os.environ.get("OPENAI_API_URL")
)

model = os.getenv("OPENAI_MODEL")

# 2. 用户提出问题

question = "125乘以36等于多少"

# 3. 系统提示词
system_prompt = """
你是一个最小ReAct Agent。

你可以使用以下工具：
calculate(a, b, operator)
其中 operator 只支持 +、-、*、/。

如果问题需要计算，请输出 JSON 对象：
{
    "thought": "简短说明为什么需要调用工具",
    "action": "calculate",
    "arguments": {
        "a": 125,
        "b": 36,
        "operator": "*"
    }
}

如果不需要调用工具，可以直接输出：
{
    "thought": "简短说明",
    "action": "final",
    "answer": "最终答案"
}

只输出一个合法的 JSON 对象，不要添加 Markdown 代码块。
"""

#保存context
messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question}
    ]

#首次请求model, 让模型生成Action
response = client.chat.completions.create(
    model=model,
    messages=messages,
    temperature=0
)

#获取模型生成的Action
action_text = response.choices[0].message.content

# 保存model生成的Action
messages.append({"role": "user",
                 "content": action_text})

#将JSON字符串转换成Python字典
action_data = json.loads(action_text)

#读取模型选择的工具
action_name = action_data["action"]

#执行对应的工具
if action_name == "calculate":
    #让模型读取生成的工具参数
    arguments = action_data["arguments"]

    #真正执行工具，得到observation
    observation = calculate(
        arguments["a"],
        arguments["b"],
        arguments["operator"]
    )

    print(f"Action: {action_name}")
    print(f"Observation: {observation}")

    #将工具的执行结果加入上下文
    messages.append({
        "role": "assistant",
        "content": (
            f"工具执行结果（Observation） : {observation}\n"
            "请根据原始用户任务和工具结果，生成最终答案。"
            "不要再次调用工具。"
            "只输出合法 JSON，格式为："
            '{"thought":"简短说明","action":"final","answer":"最终答案"}'
        )
    })

    #第二次请求模型，使用完整的对话上下文
    final_response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0
    )

    # 解析模型返回的最终的结果
    final_text = final_response.choices[0].message.content

    try:
        final_data = json.loads(final_text)

        if final_data.get("action") == "final":
            print(f"最终答案：{final_data['answer']}")
        else:
            print(f"模型未返回 final：{final_text}")

    except json.JSONDecodeError:
        print(f"模型返回的不是合法 JSON：{final_text}")



elif action_name == "final":
    print(f"最终答案：{action_data['answer']}")

else:
    print("错误，模型选择了不支持的工具")
