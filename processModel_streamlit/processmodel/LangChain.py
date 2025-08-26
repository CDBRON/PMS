import os

# 【重要】将这一行放在文件的最顶部，以彻底禁用 LangSmith 警告
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGCHAIN_API_KEY"] = " "  # 设置为空字符串也能帮助禁用

from langchain.agents import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

# --- 1. 初始化 LLM ---
llm = ChatGoogleGenerativeAI(model="gemini/gemini-2.0-flash", temperature=0)


# --- 2. 定义自定义工具 ---
@tool
def calculator(expression: str) -> str:
    """
    当需要进行数学计算时，调用此工具。
    输入应该是一个格式清晰的数学表达式字符串。
    例如: `2 + 3`, `10 - 4 / 2`, `(5 * 2) - 1`.
    """
    print(f"\n--- 正在调用自定义工具 'calculator'，输入: {expression} ---\n")
    try:
        # 安全警告: eval() 在生产环境中应谨慎使用。
        result = eval(expression)
        return f"表达式 '{expression}' 的计算结果是: {result}"
    except Exception as e:
        return f"计算表达式 '{expression}' 时发生错误: {e}"


tools = [calculator]

# --- 3. 创建 Agent 和 AgentExecutor (已最终修正) ---
# 【重要修正】拉取一个不包含聊天记录(chat_history)的、用于单次任务的 ReAct prompt。
prompt = hub.pull("hwchase17/react")

# 这个 Agent 不需要聊天记录，可以正常工作
agent = create_react_agent(llm, tools, prompt)

# 创建 AgentExecutor，这是运行智能体的执行器
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)


# --- 4. 运行智能体 ---
def main():
    """主函数，用于接收用户输入并与智能体交互。"""
    print("\n" + "=" * 50)
    print(" 欢迎使用 Gemini 2.0 Flash + LangChain 智能体".center(50))
    print(" (最终修正版)".center(50))
    print("=" * 50)
    print("\n这是一个示例，它集成了一个自定义的计算器工具。")
    print("你可以问它一些需要计算的问题，例如：")
    print("  -> (12 + 8) * 3 等于多少？")
    print("  -> 100 除以 (2 * 5) 的结果是什么？")
    print("\n输入 'exit' 退出程序。\n")

    while True:
        try:
            user_input = input("请输入你的问题 > ")
            if user_input.lower() == 'exit':
                print("程序已退出。")
                break

            # 【重要】这里的调用方式不需要改变，因为 AgentExecutor 会自动处理输入格式
            result = agent_executor.invoke({"input": user_input})

            print("\n" + "-" * 50)
            print("最终答案:".center(50))
            print(result["output"])
            print("-" * 50 + "\n")

        except Exception as e:
            # 打印更详细的错误信息，便于调试
            import traceback
            print("\n程序运行出现错误:")
            traceback.print_exc()
            print()


if __name__ == "__main__":
    if not os.getenv("GOOGLE_API_KEY"):
        print("错误: 请确保你已经创建了 .env 文件，")
        print("并且在其中设置了你的 GOOGLE_API_KEY。")
    else:
        main()