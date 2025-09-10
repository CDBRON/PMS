import ast
import json
import re
import uuid
from collections import deque
import traceback
import streamlit as st
import time
import os
import asyncio
from xml.dom import minidom
from GPTClient import GPTClient
import xml.etree.ElementTree as ET



# --- 这部分代码保持不变，放在您的 Python 脚本顶部 ---
from langchain_community.utilities import SerpAPIWrapper
from langchain.tools import Tool

# 假设您已经在 .env 文件中设置了 SERPAPI_API_KEY
# load_dotenv() 应该已经执行过了

# 1. 创建一个搜索工具实例
search_api = SerpAPIWrapper(serpapi_api_key="9117d9d03f08785a96d06fecd65e9234b384b5df3e9e07a3ad6b13e1636d4ae8")

# 2. 将其包装成一个专用的工具
industry_search_tool = Tool(
    name="IndustryBestPracticeSearch",
    func=search_api.run,
    description="It is used when you need to understand the standards, best practices or common steps of a specific industry or business process. This tool can access the Internet to obtain the latest and real-world information."
)


# --- 1. 页面基础配置 ---
st.set_page_config(
    page_title="CoRePro构造器",
    page_icon="🤖",
    layout="centered"
)
asyncio.set_event_loop(asyncio.new_event_loop())


class Config:
    """Centralized configuration parameters."""
    # MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY")
    # Gemini_API_KEY: str = os.getenv("Gemini_API_KEY")
    MISTRAL_MODEL: str = "mistral-large-latest"
    Gemini_MODEL: str = "gemini-2.5-flash-lite"
    TEMPERATURE: float = 0


st.title("CoRePro🤖")
st.markdown("---")

# --- 新增：获取用户的Google Gemini API Key ---
api_key = st.text_input("请输入您的 Google Gemini API Key:", type="password",
                        help="您的API Key将仅在当前会话中使用，不会被存储。")

# --- 只有在用户输入API Key后才继续执行应用的核心逻辑 ---
if api_key:
    try:
        # 使用用户输入的API Key初始化GPTClient
        gpt_client = GPTClient(
            # api_key=Config.Gemini_API_KEY,
            api_key=api_key,
            model=Config.Gemini_MODEL,
            temperature=Config.TEMPERATURE
        )
    except Exception as e:
        st.error(f"API Key无效或客户端初始化失败: {e}")
        st.stop()  # 如果Key无效或初始化失败，则停止执行

    # --- 2. 初始化会话状态 ---
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant",
             "content": "你好！我是CoRePro。请用自然语言描述您想创建的企业级工作流，例如：“设计一个员工差旅报销流程”"}
        ]

    # 初始化用于存储当前工作流的会话状态
    if "current_workflow_ir" not in st.session_state:
        st.session_state.current_workflow_ir = None

    # --- 3. 界面标题 ---
    # st.title("AURA v2.6  🤖")
    # st.markdown("---")

    # --- 4. 显示历史对话消息 ---
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # --- 5. 处理用户输入 (核心交互逻辑) ---
    if prompt := st.chat_input("请描述您想创建的工作流..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("正在分析您的需求并激活CoRePro核心构造器..."):
                time.sleep(2)
            system_content = '''
            You are a decision-maker. Based on the user's input, you determine which category it belongs to.
            # Core Task
            Your sole responsibility is to analyze the user's input (user_content) and accurately classify its intent into one of the predefined categories.
            You must return your result with string format.
            # Guiding Principles
            1.  **Focus on Classification**: Your role is to classify, not to execute or converse. Do not engage in dialogue with the user. Do not attempt to answer questions or fulfill the request yourself.
            2.  **Strict Adherence to Format**: Your output must be a string and nothing else. Do not include any explanations, comments, markdown code blocks, or greetings.
            # Intent Categories
            1.  **`CREATE_WORKFLOW`**: The user wants to create a new workflow from scratch.
            2.  **`MODIFY_WORKFLOW`**: The user wants to modify an existing workflow (add, delete, or adjust steps).
            3.  **`UNCLEAR_INTENT`**: Use this when the user's intent is ambiguous and cannot be clearly classified into any of the above categories.
            # Output Format Definition
            Your output must a string,include `CREATE_WORKFLOW`、`MODIFY_WORKFLOW`、`UNCLEAR_INTENT`.
            Let's think step by step!
            '''
            user_content = f'''Now this input is {prompt},please tackle this input.'''
            messages = [{'role': 'system', 'content': system_content}, {'role': 'user', 'content': user_content}]
            result = gpt_client.chat_completion(str(messages), temperature=0)
            cleaned_result = result.strip().replace("'", "").replace('"', "")

            if cleaned_result == 'CREATE_WORKFLOW':
                response = f'''好的,现在为你创建一个"{prompt}"的工作流。即将开始多阶段进化式构造...'''
                st.write(response)
                st.session_state.messages.append({"role": "assistant", "content": response})


                # STAGE 1: Meta-Structure Debate
                # STAGE 1: Meta-Structure Debate (Final Version)
                def run_debate_phase(user_prompt):
                    st.markdown("---")
                    st.subheader("阶段一：引导式头脑风暴 (生成BPMN组件清单)")
                    opinion_A = ""
                    opinion_B = ""
                    final_ir = ""

                    # --- 步骤 1.1: BPMN专家架构师A进行有纪律的生成 ---
                    # 这是最终的、为BPMN场景优化的、带有强约束的Prompt
                    debater_A_system_prompt = '''
                    You are Architect Debater A, a specialist in designing structured business processes (BPMN).Your key skill is to take a user's core idea and flesh it out into a realistic, comprehensive business process.
                    Your goal is to generate a single, comprehensive, and practical component inventory for the user's request.You don't just translate; you analyze, enrich, and then design, proactively identifying opportunities for parallel , inclusive and exclusive logic.


                    **[YOUR THINKING PROCESS]**
                    1.  **Analyze the User's Request:** Understand the core process the user wants.、
                    2.  **Enrich the Scenario (Your Key Value!):** Ask yourself: "In a real-world, efficient business, what parts of this process could happen at the same time? What optional steps or choices might exist?" You MUST actively look for these opportunities.
                    3.  **Formulate a Plan:** Based on your analysis, briefly state the enriched scenario you will model. This makes your reasoning transparent.
                    4.  **Generate Components:** Generate the `roles`, `activities`, and `gateways` for the *enriched scenario* you just planned.

                    **[EXAMPLE OF YOUR THINKING PROCESS]**
                    *   **If User Says:** "Design a loan application process."
                    *   **Your Internal Thought & Plan:** "A simple loan process is too linear. A real-world process is more complex. After an initial check, the bank could perform the risk assessment and the collateral valuation *in parallel* to save time. Also, the applicant might be offered *optional* loan insurance. My plan is to model a process with a parallel gateway for assessments and an inclusive gateway for optional products."
                    *   **Your Generation:** You would then generate components including a `parallelGateway` and an `inclusiveGateway`.

                    **[CONTEXT & ASSUMPTION]**
                    *   You MUST assume that every user request is for a standard, real-world business process that needs to be modeled.
                    *   Your output should always be rich enough to capture the core logic, key participants, and critical decision points.


                    **[CORE COMPONENTS TO GENERATE (Your Toolbox)]**
                    You must generate a Python dictionary containing the following three keys: `roles`, `activities`, and `gateways`.

                    1.  **`roles` (list[str]):** The participants (people, departments, or systems) who perform actions.
                        *   *Example:* `["Employee", "Manager"]`

                    2.  **`activities` (list[dict]):** The specific, tangible business actions performed by a single role.
                        *   *Example:* `{"id": "act_1", "description": "Employee submits expense report"}`

                    3.  **`gateways` (list[dict]):** Decision points where the process flow splits or merges. You MUST use the correct `type` based on the logic.
                        *   **`exclusiveGateway`**: Use for **"EITHER/OR"** decisions. Only one path can be taken (e.g., Yes/No, Approved/Rejected).
                        *   **`parallelGateway`**: Use when multiple activities **MUST ALL happen concurrently**. All outgoing paths are activated simultaneously.
                        *   **`inclusiveGateway`**: Use for **"ONE OR MORE"** decisions. One or more paths can be taken based on conditions.

                    **[GENERATION RULES & CONSTRAINTS (VERY IMPORTANT)]**
                    1.  **STAY FOCUSED:** Generate components that are **directly and strictly relevant** to the user's stated process. Do not invent unrelated sub-processes or tangential activities. For "Employee Onboarding," you can include "IT Account Setup," but you must NOT include "Company Annual Party Planning."
                    2.  **BUSINESS VALUE ONLY:** Every component, especially activities, MUST represent a tangible business action or decision. **Aggressively filter out** trivial, non-business steps like "Save to database," "Log event," "Send notification," or "Check network status." These are implementation details, not process steps.
                    3.  **INCLUDE KEY EXCEPTIONS:** A robust process handles failures. Ensure you include the "unhappy paths," such as what happens if a request is rejected, needs more information, or times out.
                    4.  **MAINTAIN CORRECT GRANULARITY:**
                         **Roles:** Each role must represent a distinct business function, department, or system. Avoid overly generic roles like "User" (prefer "Customer" or "Employee") and avoid specific individual names like "John Doe" (prefer "Hiring Manager").
                         **Activities:** The scope of each activity must be just right. It should represent a clear, actionable task with business value. Avoid overly broad descriptions like "Process order" and overly microscopic ones like "Click submit button." A good example is "Verify customer credit score."
                         **Gateways:** The same principle applies. A gateway must represent a meaningful business decision that dictates the flow's path. Avoid trivial checks. A good example is "Is credit score above 700?", not "Check if form is open."**
                    5.  **USE THE EXAMPLE AS A SCOPE BENCHMARK:** The example below is your reference for the appropriate level of detail and scope. It demonstrates all gateway types.

                    **[QUALITY REFERENCE EXAMPLE for "New Employee Onboarding"]**
                    ```python
                    {{
                        "roles": ["Candidate", "HR Department", "IT Department", "Hiring Manager"],
                        "activities": [
                            {{"id": "act_1", "description": "HR Department sends offer letter"}},
                            {{"id": "act_2", "description": "Candidate accepts offer"}},
                            {{"id": "act_3", "description": "IT Department provisions laptop and accounts"}},
                            {{"id": "act_4", "description": "HR Department prepares payroll and tax forms"}},
                            {{"id": "act_5", "description": "Hiring Manager prepares onboarding plan"}},
                            {{"id": "act_6", "description": "HR Department enrolls employee in health plan"}},
                            {{"id": "act_7", "description": "HR Department enrolls employee in retirement plan"}},
                            {{"id": "act_8", "description": "HR Department processes rejection notification"}}
                        ],
                        "gateways": [
                            {{
                                "id": "gate_1",
                                "type": "exclusiveGateway",
                                "description": "Is offer accepted?"
                            }},
                            {{
                                "id": "gate_2",
                                "type": "parallelGateway",
                                "description": "Initiate parallel setup tasks"
                            }},
                            {{
                                "id": "gate_3",
                                "type": "inclusiveGateway",
                                "description": "Select optional benefits"
                            }}
                        ]
                    }}
                    ```

                    **[YOUR TASK DIRECTIVE]**
                    Following all definitions and rules strictly, generate a component inventory for the user's request.
                    Let's think step by step!
                    **[OUTPUT FORMAT]**
                    Your output MUST be only a single Python dictionary, enclosed in ```python ... ```.
                    '''

                    with st.expander("步骤 1.1: BPMN专家架构师 A 生成组件清单", expanded=True):
                        # --- 阶段 1: 直接调用外部工具获取背景知识 ---
                        st.markdown("#### 步骤 1.1: 直接调用外部工具获取背景知识")
                        tool_output = ""  # 初始化工具输出
                        with st.spinner("正在为您的需求搜索外部资料..."):
                            # 1. 直接根据用户输入构建一个更有效的搜索查询
                            search_query = f"Standard business process steps and best practices for '{user_prompt}'"
                            st.info(f"自动生成的搜索查询: `{search_query}`")

                            try:
                                # 2. 直接执行工具（调用您定义的Python函数）
                                tool_output = industry_search_tool.run(search_query)
                                st.success("外部信息获取成功！")

                                st.markdown("##### 查看获取到的研究资料:")
                                st.text_area(
                                    label="研究资料",
                                    value=tool_output,
                                    height=150,
                                    label_visibility="collapsed"
                                )
                            except Exception as e:
                                st.error(f"工具调用失败，将仅基于内置知识进行设计。错误: {e}")
                                tool_output = "外部资料获取失败。"  # 即使失败也要提供信息

                            # --- 阶段 2: 专家架构师进行最终设计 ---
                        st.markdown("#### 步骤 1.2: BPMN专家架构师 A 生成组件清单")
                        with st.spinner("BPMN专家架构师A正在整合外部信息并设计流程组件..."):
                            # 3. 构造一个增强的用户提示，将研究结果包含进去
                            final_user_prompt = f"""
                                    User Request: '{user_prompt}'

                                    [Context from External Research]
                                    Here is some background information obtained from an internet search. You MUST use this information to ensure your design is comprehensive and based on real-world practices.
                                    ---
                                    {tool_output}
                                    ---
                                    Please use the original request and the research context above to inform your final design.
                                    """
                            # 4. 准备LLM调用，使用您原来的强大提示词
                            messages_A = [
                                {'role': 'system', 'content': debater_A_system_prompt},
                                {'role': 'user', 'content': final_user_prompt}
                            ]
                            # 5. LLM调用，生成最终的组件清单
                            opinion_A = gpt_client.chat_completion(str(messages_A), temperature=0)
                            opinion_A = opinion_A.strip().replace("```python", "").replace("```", "")
                        st.info("架构师 A 的最终设计方案 (BPMN专家版):")
                        st.code(opinion_A, language="python")
                        # with st.spinner("BPMN专家架构师A正在设计流程组件..."):
                        #     messages_A = [{'role': 'system', 'content': debater_A_system_prompt},
                        #                   {'role': 'user', 'content': f"User Request: '{user_prompt}'"}]
                        #     opinion_A = gpt_client.chat_completion(str(messages_A), temperature=0)
                        #     opinion_A = opinion_A.strip().replace("```python", "").replace("```", "")
                        # st.info("架构师 A 的观点 (BPMN专家版):")
                        # st.code(opinion_A, language="python")

                    # --- 后续的辩手B和法官逻辑保持不变，它们将在这个高质量的清单基础上工作 ---
                    # ... (辩手B和法官的代码与您原始版本一致，此处省略以保持简洁) ...
                    # ... The rest of the function for Debater B and the Judge remains the same ...
                    debater_B_system_prompt = f'''
                    You are Architect Debater B, a meticulous and detail-oriented process analyst. 
                    Your motto is "The strength of a process is in how it handles exceptions." 
                    You specialize in identifying overlooked components, alternative paths, and potential failure points that are often missed in the initial design phase.
                    You will receive a user request and Debater A's initial component inventory. Your task is to critically evaluate this inventory and then propose a new, more complete version.
                    **[KNOWLEDGE INJECTION: The Process Component Inventory IR]**
                    This is the required Intermediate Representation (IR) for the component inventory. It is a Python dictionary containing exactly these three keys: `'roles'`, `'activities'`, and `'gateways'`.
                    1.  `'roles'` (list[str]): A flat list of unique entities (e.g., 'Customer', 'Sales Team').
                    2.  **`'activities'` (list[dict]):** A flat list of dictionaries representing atomic actions.
                    3.  **`'gateways'` (list[dict]):** A flat list of dictionaries representing potential points of logic. The `'type'` can be `'exclusiveGateway'`, `'parallelGateway'`, or `'inclusiveGateway'`.
                    **[YOUR TASK DIRECTIVES]**
                    Your task is to perform a two-step analysis: Critique, then Expand.
                    1.  **CRITIQUE THE INVENTORY:** Scrutinize Debater A's inventory by asking these critical questions:
                        *   **Roles:** Is there any other department, system, external service, or regulatory body involved that was missed? (e.g., 'Audit Team', 'Legal Department').
                        *   **Activities:** What about the "unhappy paths"? What happens if something is rejected, needs clarification, or times out? Are there activities for notifications, logging, or archiving?
                        *   **Gateways:** Did Debater A overlook any simple decision points (`exclusiveGateway`) or clear concurrent tasks (`parallelGateway`)? Crucially, what about optional, conditional paths?
                    2.  **EXPAND THE INVENTORY:** Based on your critique, create a new, more robust inventory.
                    **[OUTPUT FORMAT]**
                    You MUST strictly follow this Markdown structure.
                    <critique>
                    [Provide a concise, bullet-point critique identifying the key missing roles, activities, and gateways from Debater A's inventory. Focus on what was overlooked.]
                    </critique>
                    <proposal>
                    ```python
                    # Your new, more complete Component Inventory, incorporating both Debater A's original components and your additions.
                    ```
                    </proposal>
                    [YOUR TASK]
                    User Request: "{user_prompt}"
                    Let's think step by step!
                    Debater A's Proposal:
                    {opinion_A}
                    '''
                    with st.expander("步骤 1.2: 架构师辩手 B 提出批判与替代方案", expanded=True):
                        with st.spinner("正在等待辩手 B 发言..."):
                            user_content_B = f"user request: '{user_prompt}'\n\n---\n\nThe proposal of debater A is as follows:\n```python\n{opinion_A}\n```\n\nPlease start your critical analysis and propose a better alternative."
                            messages_B = [{'role': 'system', 'content': debater_B_system_prompt},
                                          {'role': 'user', 'content': user_content_B}]
                            opinion_B = gpt_client.chat_completion(str(messages_B), temperature=0)
                            opinion_B_match = re.search(r'<proposal>\s*```python(.*?)```\s*</proposal>', opinion_B,
                                                        re.DOTALL)
                            if opinion_B_match:
                                opinion_B_code = opinion_B_match.group(1).strip()
                            else:
                                opinion_B_code = opinion_A

                        st.warning("辩手 B 的观点:")
                        st.markdown(opinion_B)

                    judge_system_prompt = '''
                    You are the Chief Engineer Judge, a seasoned systems architect with a holistic perspective. 
                    Your motto is "The best plan is born from constructive conflict." 
                    Your duty is to analyze the debate between two architects, synthesize their best ideas, correct their oversights, and ultimately produce the single, most comprehensive, and definitive component inventory for the process.
                    You will receive the user request and the complete debate between Architect A and Architect B.
                    **[KNOWLEDGE INJECTION: The Process Component Inventory IR]**
                    The final Component Inventory is a Python dictionary containing exactly these three keys: `'roles'`, `'activities'`, and `'gateways'`. 
                    **[YOUR DECISION-MAKING PRINCIPLES]**
                    1.  **SYNTHESIZE, DO NOT CHOOSE:** Your primary function is synthesis. **NEVER** simply pick one proposal over the other. You must merge the strengths of both.
                    2.  **ACKNOWLEDGE AND INTEGRATE:** Start with Debater A's foundational inventory. Integrate the valid additions and insightful critiques from Debater B.
                    3.  **CRITICALLY EVALUATE ALL INPUTS:** Scrutinize the entire debate. You have the final authority to **merge, rephrase, or discard** any component from either proposal to improve clarity and consistency.
                    4.  **TRANSCENDENTAL THINKING (YOUR KEY VALUE):** Your most critical task is to identify what **both** debaters missed. Elevate the inventory by considering a higher level of abstraction.
                    5.  **JUSTIFY YOUR JUDGMENT:** Your reasoning is as important as the final inventory.
                    **[OUTPUT FORMAT]**
                    You **MUST** strictly follow this Markdown structure.
                    ```judgment
                    # Provide a concise and insightful summary of the debate.
                    ```              
                    ```python
                    # Place your final, definitive, and most comprehensive Component Inventory here.
                    ```
                    '''
                    with st.expander("步骤 1.3: 总工程师法官进行综合与升华", expanded=True):
                        with st.spinner("总工程师法官正在深度思考并作出最终裁决..."):
                            user_content_judge = f"""user request: '{user_prompt}'
                                                       ---
                                                       The proposal of debater A:
                                                       ```python
                                                       {opinion_A}
                                                       ```
                                                       ---
                                                       Debater B's analysis and plan:
                                                       {opinion_B}
                                                       ---
                                                       Please conduct a comprehensive assessment and give your final ruling.
                                                       Let's think step by step!
                                                       """
                            messages_judge = [{'role': 'system', 'content': judge_system_prompt},
                                              {'role': 'user', 'content': user_content_judge}]
                            final_judgment = gpt_client.chat_completion(str(messages_judge), temperature=0)
                            final_ir_match = re.search(r'```python(.*?)```', final_judgment, re.DOTALL)
                            if final_ir_match:
                                final_ir = final_ir_match.group(1).strip()
                            else:
                                final_ir = "{}"

                        st.success("总工程师法官的裁决:")
                        st.markdown(final_judgment)
                    st.balloons()
                    return final_ir


                # NEW STAGE 2: Inventory Simplification
                def run_inventory_simplification(inventory_ir, user_prompt):
                    st.markdown("---")
                    st.subheader("阶段二：组件清单瘦身 (第一轮精简)")
                    st.info("目标：通过完整的案例学习，智能筛选所有必要的组件。")

                    if not inventory_ir or not isinstance(inventory_ir, dict):
                        st.warning("无有效组件清单传入，跳过此阶段。")
                        return None

                    inventory_ir_str = json.dumps(inventory_ir, indent=2)

                    ### MODIFICATION START: Escaped all curly braces in the JSON example ###
                    simplifier_prompt = f'''
                    You are a Pragmatic Process Analyst. Your mission is to refine a comprehensive component inventory into a lean, practical, and effective workflow by distinguishing between essential business logic and non-essential "nice-to-haves".
                    
                    
                     **[Simplification Principles]**
                    Your goal is to remove non-essential "nice-to-haves". You should focus on:
                    1.  **Merging Redundant Roles:** Combine roles that perform very similar functions.
                    2.  **Removing Trivial Activities:** Eliminate activities that represent system-level implementation details (e.g., "Log event," "Send notification").
                
                
                    **[ABSOLUTE RULE: GATEWAY PRESERVATION HIERARCHY]**
                    This is your most important and non-negotiable directive. You must treat different gateway types differently:
                
                    1.  **`parallelGateway` & `inclusiveGateway` (DO NOT REMOVE):**
                        *   These two types of gateways represent **sacrosanct business logic** (concurrency and optionality).
                        *   You are **STRICTLY FORBIDDEN** from removing or simplifying them for any reason.
                        *   It does not matter if you think their description is "vague" or "implicitly handled" elsewhere. Your task is to **PRESERVE THEM UNCONDITIONALLY**. They are considered non-trivial by definition and must be passed to the next stage.
                
                    2.  **`exclusiveGateway` (MAY BE REMOVED):**
                        *   You are permitted to evaluate `exclusiveGateway`s.
                        *   You may remove one **ONLY IF** it represents a truly trivial, non-business decision (e.g., "Is form open?").
                        *   If it represents a valid business choice (e.g., "Is request approved?"), you must keep it.       
                        
                        
                                                     
                    **[GOLD-STANDARD EXAMPLE]**
                    Here is a complete example of your task. You will receive a bloated inventory and must produce a rationale and a lean version.

                    **INPUT - Bloated Inventory:**
                    ```json
                    {{
                        "roles": ["Employee", "Manager", "System"],
                        "activities": [
                            {{"id": "act_1", "description": "Employee submits request"}},
                            {{"id": "act_2", "description": "System logs the submission"}},
                            {{"id": "act_3", "description": "Manager approves request"}}
                        ],
                        "gateways": [
                            {{"id": "gate_1", "type": "exclusiveGateway", "description": "Is request approved?"}},
                            {{"id": "gate_2", "type": "parallelGateway", "description": "Initiate parallel post-approval actions"}},
                            {{"id": "gate_3", "type": "exclusiveGateway", "description": "Check if database is connected?"}}
                        ]
                    }}
                    ```

                    **YOUR CORRECT OUTPUT:**
                    <simplification_rationale>
                    *   **Removed Trivial Activity:** Removed 'System logs the submission' as it's an implementation detail.
                    *   **Preserved Essential Gateway:** Kept 'gate_1' (`exclusiveGateway`) because "Is request approved?" is a core business decision.
                    *   **PRESERVED PER ABSOLUTE RULE:** Kept 'gate_2' (`parallelGateway`) unconditionally. Even though its description "Initiate parallel post-approval actions" is general, its TYPE makes it non-removable by definition.
                    *   **Removed Trivial Gateway:** Removed 'gate_3' (`exclusiveGateway`) because checking a database connection is a system-level check, not a business process decision.
                    </simplification_rationale>
                    <lean_inventory>
                    ```python
                    {{
                        "roles": ["Employee", "Manager", "System"],
                        "activities": [
                            {{"id": "act_1", "description": "Employee submits request"}},
                            {{"id": "act_3", "description": "Manager approves request"}}
                        ],
                        "gateways": [
                            {{"id": "gate_1", "type": "exclusiveGateway", "description": "Is request approved?"}},
                            {{"id": "gate_2", "type": "parallelGateway", "description": "Initiate parallel post-approval actions"}}
                        ]
                    }}
                    ```
                    </lean_inventory>

                    [CRITICAL OUTPUT INSTRUCTION]
                    Your entire response MUST strictly follow the XML-like tag structure shown in the example above.
                    1.You MUST include a <simplification_rationale> section. If you find no items to simplify, you MUST write "No simplifications were necessary as the initial inventory is already lean and practical." inside the tags.
                    2.You MUST include a <lean_inventory> section containing the final Python code block. If no changes are made, this section will contain the original inventory.
                    3.DO NOT add any other text, greetings, or explanations outside of these two required tag structures.
                    


                    **[YOUR CURRENT TASK]**
                    Now, apply this exact same logic to the following inventory, strictly adhering to the **ABSOLUTE RULE** about gateways. You MUST NOT remove any `parallelGateway` or `inclusiveGateway`.
                    Let's think step by step!
                    **User Request:** "{user_prompt}"
                    **Component Inventory to Simplify:**
                    ```json
                    {inventory_ir_str}
                    ```
                    '''
                    ### MODIFICATION END ###

                    with st.expander("执行组件清单瘦身", expanded=True):
                        with st.spinner("流程分析师正在进行智能筛选..."):
                            messages = [{'role': 'system', 'content': simplifier_prompt}]
                            response = gpt_client.chat_completion(str(messages), temperature=0)

                            rationale_match = re.search(r'<simplification_rationale>(.*?)</simplification_rationale>',
                                                        response, re.DOTALL)
                            ir_match = re.search(r'<lean_inventory>\s*```python(.*?)```\s*</lean_inventory>', response,
                                                 re.DOTALL)

                            rationale = rationale_match.group(1).strip() if rationale_match else "未能解析简化报告。"
                            lean_ir = None
                            if ir_match:
                                try:
                                    lean_ir_string = ir_match.group(1).strip()
                                    lean_ir = ast.literal_eval(lean_ir_string)
                                except (ValueError, SyntaxError) as e:
                                    st.error(f"解析瘦身版IR时出错: {e}")
                                    lean_ir = inventory_ir

                    st.info("#### 组件瘦身报告:")
                    st.markdown(rationale)
                    if lean_ir:
                        st.success("#### 精简后的组件清单:")
                        st.code(json.dumps(lean_ir, indent=2), language="json")
                        return lean_ir
                    return inventory_ir


                # STAGE 3: Detail Filling Debate
                # STAGE 3: Detail Filling Debate (MODIFIED for Single-Lane Output)
                def run_detail_filling_debate(meta_structure_ir, user_prompt):
                    st.markdown("---")
                    # 更新阶段标题
                    st.subheader("阶段三：流程搭建 (精确类型保留)")
                    draft_ir = None
                    final_ir = None
                    if isinstance(meta_structure_ir, str):
                        try:
                            meta_structure_ir = ast.literal_eval(meta_structure_ir)
                        except (ValueError, SyntaxError):
                            st.error("错误：元结构IR不是有效的Python字典格式，无法继续进行细节填充。")
                            return None
                    inventory_str = json.dumps(meta_structure_ir, indent=2)

                    # --- 这是为“精确类型保留”重写的、带有强约束的Prompt ---
                    architect_prompt = f'''
                    You are a meticulous Process Architect. Your task is to assemble a flat inventory of components into a structured process flow. Your most critical responsibility is to ensure the **exact, specific BPMN type** of each gateway is preserved.

                    **[KNOWLEDGE INJECTION: The Target Process Flow IR]**
                    The final output MUST be a Python dictionary. The key rule is: The 'role' of an activity or gateway MUST be prepended to its 'description' string.

                    **[CRITICAL INSTRUCTION: GATEWAY TYPES]**
                    When you create a gateway element in your output, its `type` field **MUST** be one of the following exact strings, copied directly from the source Component Inventory:
                    - `exclusiveGateway`
                    - `parallelGateway`
                    - `inclusiveGateway`
                    **DO NOT** use a generic type like `"gateway"`. This is a critical error. You must look at the `type` in the input inventory and use that exact string.

                    **[CRITICAL INSTRUCTION: NO CLOSING GATEWAYS]**
                    You MUST ONLY generate splitting gateways (gateways with branches). 
                    The system that processes this IR will automatically create the corresponding merging (closing) gateways. 
                    **DO NOT** add a gateway element that has no branches for the purpose of merging a previous split. 
                    For example, after a `parallelGateway` with branches, you should not add another `parallelGateway` with no branches to close it.
                    
                    
                    **[CRITICAL INSTRUCTION : COMPONENT UNIQUENESS AND LOGICAL PROGRESSION (ABSOLUTE RULE)]**
                    This is your most important rule to prevent generating invalid workflows.
                    1.  **USE EACH COMPONENT ONCE:** Each activity and gateway from the input inventory has a unique ID. You **MUST NOT** use the same activity or gateway ID in multiple places within your generated process flow. Each component represents a single, unique step in the process.
                    2.  **ENSURE FORWARD PROGRESSION:** The workflow must always move forward. **DO NOT** create a structure where a task is performed, and then a subsequent gateway leads back to the exact same task. This is a logical loop and is forbidden. If a task needs to be repeated, it should be modeled as a new, distinct activity with a new ID (e.g., "Rework Application").

                    **[GOLD-STANDARD EXAMPLE: "New Employee Onboarding"]**
                    This example demonstrates all rules correctly: precise types, paired gateways, and (most importantly) each activity and gateway is used only once, ensuring a clean, forward-progressing flow.
                    
                    
                    ```json
                    {{
                    "process": [
                        {{
                            "type": "activity",
                            "id": "act_1",
                            "description": "HR Department: Send offer letter"
                        }},
                        {{
                            "type": "exclusiveGateway",
                            "id": "gate_1",
                            "description": "Candidate: Is offer accepted?",
                            "branches": [
                                {{
                                    "condition": "Yes",
                                    "flow": [
                                        {{
                                            "type": "parallelGateway",
                                            "id": "gate_2_split",
                                            "description": "Onboarding Kick-off: Initiate parallel setup tasks",
                                            "branches": [
                                                {{
                                                    "condition": "",
                                                    "flow": [ {{ "type": "activity", "id": "act_3", "description": "IT Department: Provision laptop" }} ]
                                                }},
                                                {{
                                                    "condition": "",
                                                    "flow": [ {{ "type": "activity", "id": "act_4", "description": "HR Department: Prepare payroll" }} ]
                                                }}
                                            ]
                                        }},
                                        {{
                                            "type": "parallelGateway",
                                            "id": "gate_2_merge",
                                            "description": "",
                                            "branches": []
                                        }},
                                        {{
                                            "type": "activity",
                                            "id": "act_5",
                                            "description": "Hiring Manager: Prepare onboarding plan"
                                        }}
                                    ]
                                }},
                                {{
                                    "condition": "No",
                                    "flow": [
                                        {{
                                            "type": "activity",
                                            "id": "act_8",
                                            "description": "HR Department: Process rejection notification"
                                        }}
                                    ]
                                }}
                            ]
                        }}
                    ]
                }}
                    ```

                    **[YOUR TASK]**
                    1.  Analyze the provided Component Inventory.
                    2.  Construct the process flow by nesting activities and gateways logically, following the comprehensive example above.
                    3.  For every gateway you create, ensure its `type` field is an exact match (`exclusiveGateway`, `parallelGateway`, or `inclusiveGateway`) from the inventory.
                    4.  Merge the role into the description for all elements.
                    5.  **Crucially, do not add any closing gateways.**

                    **[YOUR CURRENT TASK]**
                    **User Request:** {user_prompt}
                    Let's think step by step!
                    **Component Inventory:**
                    ```json
                    {inventory_str}
                    ```
                    **Output Format:** Your output MUST be only a single Python dictionary in the specified format, enclosed in ```python ... ```. DO NOT add any explanation.
                    '''

                    with st.expander("执行流程搭建", expanded=True):
                        with st.spinner("流程架构师正在搭建并验证节点类型..."):
                            architect_response = gpt_client.chat_completion(architect_prompt)
                            match = re.search(r"```python\s*(\{.*?\})\s*```", architect_response, re.DOTALL)
                            if match:
                                try:
                                    draft_ir = ast.literal_eval(match.group(1))
                                except (ValueError, SyntaxError) as e:
                                    st.error(f"解析架构师草案时出错: {e}")
                                    draft_ir = None
                            if draft_ir:
                                st.info("流程架构师的草案 (单泳道格式):")
                                st.code(json.dumps(draft_ir, indent=2), language="json")
                            else:
                                st.error("流程架构师未能生成有效草案。")
                        if not draft_ir:
                            st.warning("由于未能生成初始草案，细节填充阶段已中止。")
                            return None

                        # For simplicity, we are skipping a separate review stage.
                        final_ir = draft_ir
                        st.success("最终流程草案 (单泳道格式):")
                        st.code(json.dumps(final_ir, indent=2), language="json")
                        return final_ir


                # STAGE 4: Critical Validation
                def run_critical_validation(candidate_ir, user_prompt):
                    st.markdown("---")
                    st.subheader("阶段四：顺序逻辑验证 (业务流程推理)")
                    st.info("目标：模拟业务专家，审查每一步之间的逻辑关系，确保流程符合常识和因果顺序。")

                    if not candidate_ir:
                        st.warning("无有效候选IR，跳过此阶段。")
                        return None

                    candidate_ir_str = json.dumps(candidate_ir, indent=2)

                    ### MODIFICATION START: Escaped all curly braces in the JSON example ###
                    critic_system_prompt = f'''
                    You are a meticulous "Logical Flow Critic" AI. 
                    Your sole purpose is to analyze the SEQUENCE of a proposed workflow and identify logical impossibilities or reversed steps based on business common sense.
                    **[GOLD-STANDARD EXAMPLE]**
                    Here is a complete example of your task. You will receive a flawed IR and must produce a validation report and a hardened (corrected) version.

                    **INPUT - Flawed IR:**
                    ```json
                    {{
                        "process": [
                            {{
                                "type": "activity",
                                "id": "activity_1",
                                "description": "Baker: Bake the cake"
                            }},
                            {{
                                "type": "activity",
                                "id": "activity_2",
                                "description": "Baker: Mix ingredients"
                            }},
                            {{
                                "type": "exclusiveGateway",
                                "id": "gateway_1",
                                "description": "Baker: Is the cake ready?",
                                "branches": [
                                    {{
                                        "condition": "No",
                                        "flow": [
                                            {{
                                                "type": "activity",
                                                "id": "activity_3",
                                                "description": "Waiter: Serve the cake to customer"
                                            }}
                                        ]
                                    }}
                                ]
                            }}
                        ]
                    }}
                    ```

                    **YOUR CORRECT OUTPUT:**
                    <validation_report>
                    *   **Causality Error:** Activity 'activity_1' (Bake the cake) cannot occur before 'activity_2' (Mix ingredients). The order must be reversed.
                    *   **Logical Contradiction:** In gateway 'gateway_1', the 'No' branch incorrectly leads to 'activity_3' (Serve the cake). A cake that is not ready cannot be served. This branch should likely lead to a waiting or re-baking step.
                    </validation_report>
                    <hardened_final_ir>
                    ```python
                    {{
                        "process": [
                            {{
                                "type": "activity",
                                "id": "activity_2",
                                "description": "Baker: Mix ingredients"
                            }},
                            {{
                                "type": "activity",
                                "id": "activity_1",
                                "description": "Baker: Bake the cake"
                            }},
                            {{
                                "type": "exclusiveGateway",
                                "id": "gateway_1",
                                "description": "Baker: Is the cake ready?",
                                "branches": [
                                    {{
                                        "condition": "Yes",
                                        "flow": [
                                            {{
                                                "type": "activity",
                                                "id": "activity_3",
                                                "description": "Waiter: Serve the cake to customer"
                                            }}
                                        ]
                                    }},
                                    {{
                                        "condition": "No",
                                        "flow": [
                                            {{
                                                "type": "activity",
                                                "id": "activity_4_fix",
                                                "description": "Baker: Continue baking for 10 more minutes"
                                            }}
                                        ]
                                    }}
                                ]
                            }}
                        ]
                    }}
                    ```
                    </hardened_final_ir>

                    [CRITICAL OUTPUT INSTRUCTION]
                    Your entire response MUST strictly follow the XML-like tag structure shown in the example above.
                    1.You MUST include a <validation_report> section. If you find no logical errors, you MUST write "No logical errors were found. The process sequence is valid." inside the tags.
                    2.You MUST include a <hardened_final_ir> section containing the final Python code block. If you found no errors, you MUST provide the original, unchanged IR in this section.
                    3.DO NOT add any other text, greetings, or explanations outside of these two required tag structures.

                    **[YOUR CURRENT TASK]**
                    Now, apply this exact same logical analysis to the following IR.

                    **User Request:** "{user_prompt}"
                    **Candidate Final IR to be validated:**
                    ```json
                    {candidate_ir_str}
                    ```
                    '''
                    ### MODIFICATION END ###

                    with st.expander("执行顺序逻辑验证", expanded=True):
                        with st.spinner("逻辑流程评论家正在逐一审查步骤间的因果关系..."):
                            messages_critic = [{'role': 'system', 'content': critic_system_prompt}]
                            validation_response = gpt_client.chat_completion(str(messages_critic), temperature=0)

                            # --- 优化的解析逻辑 ---
                            report_match = re.search(r'<validation_report>(.*?)</validation_report>',
                                                     validation_response,
                                                     re.DOTALL)
                            ir_match = re.search(r'<hardened_final_ir>\s*```python(.*?)```\s*</hardened_final_ir>',
                                                 validation_response, re.DOTALL)

                            validation_report = "未能从AI响应中解析出验证报告。"
                            if report_match:
                                validation_report = report_match.group(1).strip()
                                if not validation_report:
                                    validation_report = "AI提供了空的验证报告。"

                            hardened_ir = None
                            if ir_match:
                                try:
                                    hardened_ir_string = ir_match.group(1).strip()
                                    if hardened_ir_string:
                                        hardened_ir = ast.literal_eval(hardened_ir_string)
                                    else:
                                        st.warning("AI返回了空的强化版流程，将使用验证前的版本。")
                                        hardened_ir = candidate_ir
                                except (ValueError, SyntaxError) as e:
                                    st.error(f"解析强化版IR时出错: {e}")
                                    hardened_ir = candidate_ir  # 出错时回退

                        # 如果在上面的所有步骤后 hardened_ir 仍然是 None (例如，ir_match 失败)
                        if not hardened_ir:
                            st.warning("AI未提供有效的强化版流程，或认为当前流程已足够健壮。将使用验证前的版本继续。")
                            hardened_ir = candidate_ir

                        st.warning("#### 逻辑验证报告:")
                        st.markdown(validation_report)
                        st.success("#### 最终IR (已通过逻辑验证):")
                        st.code(json.dumps(hardened_ir, indent=2), language="json")
                        return hardened_ir


                # STAGE 5: Refinement & Simplification
                def run_refinement_and_simplification(hardened_ir, user_prompt):
                    st.markdown("---")
                    st.subheader("阶段五：业务流程优化 (第二轮精简)")
                    st.info("目标：通过合并连续活动或精炼描述来优化流程，消除浪费。")

                    if not hardened_ir:
                        st.warning("由于上一步未能生成有效的IR，优化阶段已跳过。")
                        return None
                    hardened_ir_str = json.dumps(hardened_ir, indent=2)

                    # --- 强化后的Prompt ---
                    optimizer_system_prompt = f'''
                    You are a Process Refinement Specialist. 
                    Your task is to refine a finalized workflow by optimizing its **activities** for clarity and efficiency, while **strictly preserving the established logical flow defined by the gateways.**
                    Please remember that if there are parallel gateways and inclusive gateways, do not remove them.

                    **[Optimization Principles (Your Mandate)]**
                    Your ONLY permitted actions are:
                    1.  **Merge Sequential Activities:** If you find two or more activities in a row that are performed by the *exact same role*, you should merge them into a single, more comprehensive activity.
                    2.  **Clarify Vague Descriptions:** If an activity description is generic (e.g., "System: Do stuff"), you should refine it to be more specific and value-driven (e.g., "System: Archive validated invoice").
                    3.  **Remove unnecessary roles**.

                    **[CRITICAL CONSTRAINT 1: DO NOT MODIFY GATEWAYS]**
                    Gateways represent the immutable business logic that has already been validated. 
                    You **MUST NOT** add, remove, or change any gateways or their branching structure. 
                    Your focus is solely on the activities within the existing flow.
                    
                    
                    **[CRITICAL CONSTRAINT 2: RESPECT BRANCH INTEGRITY (ABSOLUTE RULE)]**
                    This is your most important structural rule. Activities located in different branches of a `parallelGateway` or `inclusiveGateway` are, by definition, **NOT SEQUENTIAL**. They run in parallel or are optional paths.
                    *   You are **STRICTLY FORBIDDEN** from merging activities that exist in separate branches.
                    *   Merging is **ONLY** permissible for activities that are adjacent to each other *within the exact same `flow` array*.
                    *   You must not create empty branches as a result of merging.

                   **[GOLD-STANDARD EXAMPLE - DEMONSTRATING CORRECT VS. INCORRECT MERGING]**
                    This example demonstrates the critical rule of branch integrity.
                    
                    
                    **INPUT - Inefficient IR:**
                    ```json
                    {{
                    "process": [
                        {{"type": "activity", "id": "act_1", "description": "Finance: Receive invoice"}},
                        {{"type": "activity", "id": "act_2", "description": "Finance: Check invoice against PO"}},
                        {{
                            "type": "parallelGateway",
                            "id": "gate_1",
                            "description": "Parallel System Actions",
                            "branches": [
                                {{
                                    "condition": "",
                                    "flow": [ {{"type": "activity", "id": "act_3", "description": "System: Log invoice data"}} ]
                                }},
                                {{
                                    "condition": "",
                                    "flow": [ {{"type": "activity", "id": "act_4", "description": "System: Notify purchasing department"}} ]
                                }}
                            ]
                        }}
                        ]
                    }}
                    ```

                    **YOUR CORRECT OUTPUT:**
                    <optimization_rationale>
                    *   **Merged Sequential Activities:** Correctly combined 'act_1' and 'act_2' because they are performed by the same 'Finance' role and appear sequentially in the top-level `process` array.
                    *   **Preserved Parallel Activities (Per Absolute Rule):** Did **NOT** merge 'act_3' and 'act_4'. Even though they are both performed by the 'System' role, they are located in different branches of the `parallelGateway` ('gate_1'). Therefore, they are not sequential and merging them would violate the process logic. This is the correct and required behavior.
                    *   **Refined Description:** Clarified the vague description for activity 'act_3' from "Update records" to "System: Archive validated invoice and notify accounting".
                    *   **No Gateway Changes:** The gateway 'gate_1' was correctly left untouched as its logic is final.
                    </optimization_rationale>
                    <optimized_ir>
                    ```python
                    {{
                    "process": [
                        {{"type": "activity", "id": "act_1_merged", "description": "Finance: Receive and validate invoice against PO"}},
                        {{
                            "type": "parallelGateway",
                            "id": "gate_1",
                            "description": "Parallel System Actions",
                            "branches": [
                                {{
                                    "condition": "",
                                    "flow": [ {{"type": "activity", "id": "act_3", "description": "System: Log invoice data"}} ]
                                }},
                                {{
                                    "condition": "",
                                    "flow": [ {{"type": "activity", "id": "act_4", "description": "System: Notify purchasing department"}} ]
                                }}
                                ]
                        }}
                        ]
                    }}
                    ```
                    </optimized_ir>

                    **[CRITICAL OUTPUT INSTRUCTION]**
                    Your entire response **MUST** strictly follow the XML-like tag structure.
                    1.  You **MUST** include an `<optimization_rationale>` section. If no optimizations are possible, you MUST write "No activity optimizations were necessary. The process is already efficient." inside the tags.
                    2.  You **MUST** include an `<optimized_ir>` section. If no changes are made, you **MUST** provide the original, unchanged IR in this section.
                    3.  **DO NOT** add any other text outside of these two required tags.

                    **[YOUR CURRENT TASK]**
                    Now, apply this exact same optimization logic to the following IR.
                    Let's think step by step!
                    **User Request:** "{user_prompt}"
                    **Hardened IR to be optimized:**
                    ```json
                    {hardened_ir_str}
                    ```

                    **FINAL REMINDER: YOUR ENTIRE RESPONSE MUST CONSIST OF ONLY THE `<optimization_rationale>` AND `<optimized_ir>` TAGS. DO NOT INCLUDE ANY OTHER TEXT, GREETINGS, OR EXPLANATIONS.**
                    '''

                    with st.expander("执行精化与精简：业务流程优化师进行打磨", expanded=True):
                        with st.spinner("业务流程优化师正在从业务角度优化流程..."):
                            messages_optimizer = [{'role': 'system', 'content': optimizer_system_prompt}]
                            optimization_response = gpt_client.chat_completion(str(messages_optimizer), temperature=0)
                            print(f'optimization_response为{optimization_response}')
                            # --- 优化的解析逻辑 ---
                            report_match = re.search(r'<optimization_rationale>(.*?)</optimization_rationale>',
                                                     optimization_response, re.DOTALL)
                            ir_match = re.search(r'<optimized_ir>\s*```(json|python)(.*?)```\s*</optimized_ir>',
                                                 optimization_response, re.DOTALL)
                            print(f'report_match为{report_match}')

                            print(f'ir_match为{ir_match}')

                            optimization_report = "未能从AI响应中解析出优化报告。"
                            if report_match:
                                optimization_report = report_match.group(1).strip()
                                if not optimization_report:
                                    optimization_report = "AI提供了空的优化报告。"

                            optimized_ir = None
                            if ir_match:
                                try:
                                    optimized_ir_string = ir_match.group(2).strip()
                                    if optimized_ir_string:
                                        optimized_ir = ast.literal_eval(optimized_ir_string)
                                    else:
                                        st.warning("AI返回了空的优化版流程，将使用未优化版本。")
                                        optimized_ir = hardened_ir
                                except (ValueError, SyntaxError) as e:
                                    st.error(f"解析优化版IR时出错: {e}")
                                    optimized_ir = hardened_ir  # 出错时回退

                    # 如果在所有步骤后 optimized_ir 仍然是 None (例如 ir_match 失败)
                    if not optimized_ir:
                        st.warning("未能从AI响应中解析出优化版IR，将使用未优化版本。")
                        optimized_ir = hardened_ir

                    st.info("#### 优化报告:")
                    st.markdown(optimization_report)
                    st.success("#### 最终优化后的IR:")
                    st.code(json.dumps(optimized_ir, indent=2), language="json")
                    return optimized_ir


                def run_final_audit_phase(optimized_ir, user_prompt):
                    """
                        新增阶段：最终审计。使用一个包含具体、高质量示例的提示，检查流程的完整性、合规性和常识性。
                        输入：经过所有优化的最终IR。
                        输出：一个包含审计状态和（如果需要）修正版IR的元组。
                    """
                    st.markdown("---")
                    st.subheader("最终阶段：审计与核查 (增强版)")

                    ir_str = json.dumps(optimized_ir, indent=2)
                    # --- REVISED PROMPT WITH HIGH-QUALITY, SPECIFIC EXAMPLE ---
                    auditor_system_prompt = f'''
                        You are an exceptionally meticulous Final Vetting Auditor AI. Your function is to be the last line of defense, performing a final sanity check on a nearly complete workflow. You must identify subtle hallucinations, logical loopholes, and structural errors that specialist agents might have missed. Your analysis must be grounded in deep, real-world business and structural knowledge.

                        **[YOUR AUDIT CHECKLIST]**
                        You must critically evaluate the workflow against these four points:
                        1.  **Completeness Check:** Does this process for "{user_prompt}" miss any universally standard, self-evident steps? (e.g., A loan process missing a "disburse funds" step).
                        2.  **Structural Integrity Check:** Are there structural errors like duplicated element IDs? Do all process paths lead to a logical conclusion?
                        3.  **Logical Loophole Check:** Is there a scenario where the process behaves illogically? (e.g., Asking a user to accept an offer that was just rejected by a committee).
                        4.  **Role Sanity Check:** Are the roles assigned to each task logical and consistent with real-world responsibilities?


                        **[SPECIAL INSTRUCTION: HANDLING OF UNPAIRED GATEWAYS]**
                        This is a critical exception to your standard procedure. The workflow you receive may sometimes contain a `parallelGateway` or `inclusiveGateway` that splits the flow but **lacks a corresponding merge gateway**.
                        When you encounter this specific situation, you MUST follow these new rules:
                        1.  It is NOT an error: The absence of a corresponding merge gateway is normal and intentional. It is NOT an error or a flaw, because it is assumed that a corresponding merge gateway will be added in a later stage of the process.
                        2.  Report as OK: Under the "Structural Integrity Check," you must explicitly state that the absence of a merge gateway is acceptable and that one must not be added.
                        3.  DO NOT REJECT: A missing merge gateway is NEVER grounds for a REJECTED verdict.
                        4.  DO NOT ADD A GATEWAY: You are STRICTLY FORBIDDEN from "fixing" this by adding a merge gateway. You must preserve the structure exactly as you received it.
                                            
                        **[GOLD-STANDARD EXAMPLE OF A FAILED AUDIT]**
                        This is the level of detail and insight required.

                        **INPUT - Flawed Mortgage Loan IR:**
                        ```json
                        {{
                          "process": [
                            {{
                              "type": "activity",
                              "id": "act_1",
                              "description": "Applicant: Applicant submits mortgage application"
                            }},
                            {{
                              "type": "activity",
                              "id": "act_2",
                              "description": "Loan Officer: Loan Officer reviews application and orders credit report"
                            }},
                            {{
                              "type": "activity",
                              "id": "act_7",
                              "description": "Appraisal Company: Appraisal Company conducts property appraisal"
                            }},
                            {{
                              "type": "activity",
                              "id": "act_8",
                              "description": "Underwriter: Underwriter assesses risk and determines loan eligibility"
                            }},
                            {{
                              "type": "exclusiveGateway",
                              "id": "gate_3",
                              "description": "Underwriter: Does application meet underwriting guidelines?",
                              "branches": [
                                {{
                                  "condition": "Yes",
                                  "flow": [
                                    {{
                                      "type": "exclusiveGateway",
                                      "id": "gate_4",
                                      "description": "Loan Officer: Is loan amount above committee approval threshold?",
                                      "branches": [
                                        {{
                                          "condition": "Yes",
                                          "flow": [
                                            {{
                                              "type": "activity",
                                              "id": "act_12",
                                              "description": "Loan Committee: Loan Committee reviews and approves/rejects loan (if required)"
                                            }},
                                            {{
                                              "type": "exclusiveGateway",
                                              "id": "gate_5",
                                              "description": "Applicant: Does applicant accept loan options?",
                                              "branches": [
                                                {{
                                                  "condition": "Yes",
                                                  "flow": [
                                                    {{
                                                      "type": "activity",
                                                      "id": "act_15",
                                                      "description": "Loan Officer: Loan is funded"
                                                    }}
                                                  ]
                                                }},
                                                {{
                                                  "condition": "No",
                                                  "flow": [
                                                    {{
                                                      "type": "activity",
                                                      "id": "act_16",
                                                      "description": "Loan Officer: Loan Officer notifies applicant of rejection"
                                                    }}
                                                  ]
                                                }}
                                              ]
                                            }}
                                          ]
                                        }},
                                        {{
                                          "condition": "No",
                                          "flow": [
                                            {{
                                              "type": "exclusiveGateway",
                                              "id": "gate_5",
                                              "description": "Applicant: Does applicant accept loan options?",
                                              "branches": [
                                                {{
                                                  "condition": "Yes",
                                                  "flow": [
                                                    {{
                                                      "type": "activity",
                                                      "id": "act_15",
                                                      "description": "Loan Officer: Loan is funded"
                                                    }}
                                                  ]
                                                }},
                                                {{
                                                  "condition": "No",
                                                  "flow": [
                                                    {{
                                                      "type": "activity",
                                                      "id": "act_16",
                                                      "description": "Loan Officer: Loan Officer notifies applicant of rejection"
                                                    }}
                                                  ]
                                                }}
                                              ]
                                            }}
                                          ]
                                        }}
                                      ]
                                    }}
                                  ]
                                }},
                                {{
                                  "condition": "No",
                                  "flow": [
                                    {{
                                      "type": "activity",
                                      "id": "act_16",
                                      "description": "Loan Officer: Loan Officer notifies applicant of rejection"
                                    }}
                                  ]
                                }}
                              ]
                            }}
                          ]
                        }}
                        ```

                        **YOUR CORRECT OUTPUT FOR THIS EXAMPLE:**
                        <audit_report>
                        *   **Completeness Check:** OK. The main steps of a mortgage process are present.
                        *   **Structural Integrity Check:** CRITICAL - The ID `gate_5` is used for two different gateway elements. All element IDs in a process must be unique. This is a structural violation.
                        *   **Logical Loophole Check:** CRITICAL - There is a major logical flaw. After the 'Loan Committee' (`act_12`) reviews the loan, the process flows directly to asking the applicant to accept options (`gate_5`). It completely ignores the outcome of the committee's decision. If the committee rejects the loan, the process should not proceed as if it were approved. A decision gateway is missing after `act_12`.
                        *   **Role Sanity Check:** OK. Roles are assigned logically.
                        </audit_report>
                        <verdict>REJECTED</verdict>
                        <revised_ir>
                        ```python
                        {{
                          "process": [
                            {{
                              "type": "activity",
                              "id": "act_1",
                              "description": "Applicant: Applicant submits mortgage application"
                            }},
                            {{
                              "type": "activity",
                              "id": "act_2",
                              "description": "Loan Officer: Loan Officer reviews application and orders credit report"
                            }},
                            {{
                              "type": "activity",
                              "id": "act_7",
                              "description": "Appraisal Company: Appraisal Company conducts property appraisal"
                            }},
                            {{
                              "type": "activity",
                              "id": "act_8",
                              "description": "Underwriter: Underwriter assesses risk and determines loan eligibility"
                            }},
                            {{
                              "type": "exclusiveGateway",
                              "id": "gate_3",
                              "description": "Underwriter: Does application meet underwriting guidelines?",
                              "branches": [
                                {{
                                  "condition": "Yes",
                                  "flow": [
                                    {{
                                      "type": "exclusiveGateway",
                                      "id": "gate_4",
                                      "description": "Loan Officer: Is loan amount above committee approval threshold?",
                                      "branches": [
                                        {{
                                          "condition": "Yes",
                                          "flow": [
                                            {{
                                              "type": "activity",
                                              "id": "act_12",
                                              "description": "Loan Committee: Loan Committee reviews and approves/rejects loan"
                                            }},
                                            {{
                                              "type": "exclusiveGateway",
                                              "id": "gate_committee_decision",
                                              "description": "Loan Committee: Is loan approved by committee?",
                                              "branches": [
                                                {{
                                                  "condition": "Yes",
                                                  "flow": [
                                                    {{
                                                      "type": "exclusiveGateway",
                                                      "id": "gate_5",
                                                      "description": "Applicant: Does applicant accept loan options?",
                                                      "branches": [
                                                        {{
                                                          "condition": "Yes",
                                                          "flow": [
                                                            {{
                                                              "type": "activity",
                                                              "id": "act_15",
                                                              "description": "Loan Officer: Loan is funded"
                                                            }}
                                                          ]
                                                        }},
                                                        {{
                                                          "condition": "No",
                                                          "flow": [
                                                            {{
                                                              "type": "activity",
                                                              "id": "act_16",
                                                              "description": "Loan Officer: Loan Officer notifies applicant of rejection"
                                                            }}
                                                          ]
                                                        }}
                                                      ]
                                                    }}
                                                  ]
                                                }},
                                                {{
                                                  "condition": "No",
                                                  "flow": [
                                                    {{
                                                      "type": "activity",
                                                      "id": "act_16",
                                                      "description": "Loan Officer: Loan Officer notifies applicant of rejection"
                                                    }}
                                                  ]
                                                }}
                                              ]
                                            }}
                                          ]
                                        }},
                                        {{
                                          "condition": "No",
                                          "flow": [
                                            {{
                                              "type": "exclusiveGateway",
                                              "id": "gate_6",
                                              "description": "Applicant: Does applicant accept loan options?",
                                              "branches": [
                                                {{
                                                  "condition": "Yes",
                                                  "flow": [
                                                    {{
                                                      "type": "activity",
                                                      "id": "act_15",
                                                      "description": "Loan Officer: Loan is funded"
                                                    }}
                                                  ]
                                                }},
                                                {{
                                                  "condition": "No",
                                                  "flow": [
                                                    {{
                                                      "type": "activity",
                                                      "id": "act_16",
                                                      "description": "Loan Officer: Loan Officer notifies applicant of rejection"
                                                    }}
                                                  ]
                                                }}
                                              ]
                                            }}
                                          ]
                                        }}
                                      ]
                                    }}
                                  ]
                                }},
                                {{
                                  "condition": "No",
                                  "flow": [
                                    {{
                                      "type": "activity",
                                      "id": "act_16",
                                      "description": "Loan Officer: Loan Officer notifies applicant of rejection"
                                    }}
                                  ]
                                }}
                              ]
                            }}
                          ]
                        }}
                        ```
                        </revised_ir>
                        
                        **[EXAMPLE 2: APPROVED AUDIT (Handling the Special Case)]**
                        This new example demonstrates exactly how to apply the **SPECIAL INSTRUCTION**.
                    
                        *INPUT - IR with an Unpaired Parallel Gateway:*
                        
                         ```json
                        {{
                          "process": [
                            {{
                              "type": "activity",
                              "id": "act_1",
                              "description": "Clerk: Receive and log application"
                            }},
                            {{
                              "type": "parallelGateway",
                              "id": "gate_split",
                              "description": "Split for parallel checks",
                              "branches": [
                                {{
                                  "condition": "",
                                  "flow": [{{ "type": "activity", "id": "act_2", "description": "System: Run credit check" }}]
                                }},
                                {{
                                  "condition": "",
                                  "flow": [{{ "type": "activity", "id": "act_3", "description": "Analyst: Review documents" }}]
                                }}
                              ]
                            }},
                            {{
                              "type": "activity",
                              "id": "act_4",
                              "description": "Manager: Make final decision"
                            }}
                          ]
                        }}
                        ```
                        
                        *YOUR CORRECT OUTPUT FOR THIS EXAMPLE:*
                        <audit_report>
                        *   **Completeness Check:** OK. The core steps are present.
                        *   **Structural Integrity Check:It is normal not to have a merged gateway. There is nothing wrong with that. Please do not add a merged gateway.
                        *   **Logical Loophole Check:** OK.
                        *   **Role Sanity Check:** OK.
                        </audit_report>
                        <verdict>APPROVED</verdict>
                        
                        
                        **[CRITICAL OUTPUT INSTRUCTION]**
                        Your entire response MUST strictly follow the XML-like tag structure shown in the example.
                        1.  Provide your analysis in the `<audit_report>` tag.
                        2.  Provide your final verdict (`APPROVED` or `REJECTED`) in the `<verdict>` tag.
                        3.  If and ONLY IF the verdict is `REJECTED`, provide a corrected version in the `<revised_ir>` tag.

                        **[YOUR CURRENT TASK]**
                        Now, apply this exact same rigorous auditing process, including the **SPECIAL INSTRUCTION** for unpaired gateways, to the following workflow.
                        Please prohibit the addition of any merge gateways. The absence of a merge gateway is not an error.
                        Please prohibit the addition of any merge gateways. The absence of a merge gateway is not an error.
                        Let's think step by step!
                        
                        **User Request:** "{user_prompt}"
                        **Finalized IR to be audited:**
                        ```json
                        {ir_str}
                        ```
                        '''
                    with st.expander("执行最终审计 (增强版)", expanded=True):
                        with st.spinner("最终审计师正在进行最后的核查..."):
                            messages = [{'role': 'system', 'content': auditor_system_prompt},
                                        {'role': 'user',
                                         'content': f'Now you need to tackle this problem:**User Request:** "{user_prompt}",**Finalized IR to be audited:**```json {ir_str}```'}]
                            response = gpt_client.chat_completion(str(messages), temperature=0)
                            print(f'审计为：{response}')
                            report_match = re.search(r'<audit_report>(.*?)</audit_report>', response, re.DOTALL)
                            verdict_match = re.search(r'<verdict>(.*?)</verdict>', response, re.DOTALL)
                            ir_match = re.search(r'<revised_ir>\s*```(json|python)(.*?)```\s*</revised_ir>', response,
                                                 re.DOTALL)

                            report = report_match.group(1).strip() if report_match else "未能解析审计报告。"
                            verdict = verdict_match.group(1).strip() if verdict_match else "NO_VERDICT"

                            st.info("#### 最终审计报告:")
                            st.markdown(report)

                            if verdict == "APPROVED":
                                st.success("#### 审计结论: **通过** (APPROVED)")
                                return optimized_ir, True
                            elif verdict == "REJECTED":
                                st.error("#### 审计结论: **驳回** (REJECTED)")
                                if ir_match:
                                    revised_ir_str = ir_match.group(2).strip()
                                    try:
                                        revised_ir = ast.literal_eval(revised_ir_str)
                                        st.warning("已采纳审计师的修改建议:")
                                        st.code(json.dumps(revised_ir, indent=2), language="json")
                                        return revised_ir, True
                                    except (ValueError, SyntaxError) as e:
                                        st.error(f"解析审计师修正版IR时出错: {e}")
                                        return optimized_ir, False
                                else:
                                    st.error("审计师驳回了流程，但未提供有效的修正版本。")
                                    return optimized_ir, False
                            else:
                                st.warning("未能明确获取审计结论，将采用原始版本。")
                                return optimized_ir, True


                # --- REVISED Main Execution Flow ---

                # 1. Brainstorm a comprehensive list of components
                inventory_ir = run_debate_phase(prompt)

                inventory_ir_string = None  # 初始化为 None
                # 在进入下一阶段前，进行解析和验证
                if inventory_ir and inventory_ir.strip() not in ["", "{}"]:
                    try:
                        # 使用 ast.literal_eval 安全地将字符串转换为字典
                        inventory_ir_string = ast.literal_eval(inventory_ir)
                        st.success("阶段一成功完成，组件清单已生成。")
                    except (ValueError, SyntaxError) as e:
                        st.error(f"阶段一失败：无法将总工程师的裁决解析为有效的Python字典。错误：{e}")
                        st.code(inventory_ir, language="text")  # 显示原始字符串以供调试
                else:
                    st.error("阶段一失败：未能从“元结构进化式辩论”中生成任何组件清单。流程已中止。")

                # 只有在 inventory_ir 有效时才继续执行后续阶段
                if inventory_ir_string:
                    # 2. First Pass of Simplification: Cull the component list
                    lean_inventory_ir = run_inventory_simplification(inventory_ir_string, prompt)

                    # 3. Build the structured process from the LEANER inventory
                    draft_ir = run_detail_filling_debate(lean_inventory_ir, prompt)

                    # 4. Validate the logic of the structured process
                    hardened_ir = run_critical_validation(draft_ir, prompt)

                    # 5. Second Pass of Simplification: Optimize the final, robust process
                    optimized_ir = run_refinement_and_simplification(hardened_ir, prompt)

                    # ---> 新增的最终审计阶段 <---
                    if optimized_ir:
                        audited_ir, is_approved = run_final_audit_phase(optimized_ir, prompt)
                        if is_approved:
                            # 将最终的IR存入会话状态
                            st.session_state.current_workflow_ir = audited_ir

                            # 使用经过最终审计的IR生成BPMN
                            # final_bpmn = generate_bpmn_xml(audited_ir)
                        else:
                            st.error("最终审计未通过，无法生成BPMN。请检查审计报告并考虑修改您的需求后重试。")
                    # --------------------------------------------------------------------
                    # ---> 就是在这里！<---
                    # 将最终的IR存入会话状态，为后续的“修改”操作做准备
                    # st.session_state.current_workflow_ir = optimized_ir
                    # --------------------------------------------------------------------


                # # 2. First Pass of Simplification: Cull the component list
                # lean_inventory_ir = run_inventory_simplification(inventory_ir, prompt)
                #
                # # 3. Build the structured process from the LEANER inventory
                # draft_ir = run_detail_filling_debate(lean_inventory_ir, prompt)
                #
                # # 4. Validate the logic of the structured process
                # hardened_ir = run_critical_validation(draft_ir, lean_inventory_ir, prompt)
                #
                # # 5. Second Pass of Simplification: Optimize the final, robust process
                # optimized_ir = run_refinement_and_simplification(hardened_ir, prompt)

                def generate_bpmn_xml(optimized_ir):
                    """
                    Converts the final optimized IR into a BPMN 2.0 XML string with layout.
                    """
                    st.markdown("---")
                    st.subheader("阶段六：BPMN 2.0 XML 生成")

                    if not optimized_ir or not optimized_ir.get('process'):
                        st.warning("无有效的优化版IR，无法生成BPMN。")
                        return

                    with st.spinner("正在将最终流程图转换为BPMN 2.0 XML..."):
                        try:
                            # Instantiate the robust generator
                            generator = BpmnXmlGenerator(optimized_ir)
                            bpmn_xml = generator.generate()
                            st.success("BPMN XML 生成成功！")
                            st.code(bpmn_xml, language='xml')
                            return bpmn_xml
                        except Exception as e:
                            st.error(f"生成BPMN时发生错误: {e}")
                            # Displaying the traceback helps in debugging future issues
                            st.error(traceback.format_exc())
                            return None


                class BpmnXmlGenerator:
                    """
                    Generates a SINGLE-LANE BPMN 2.0 XML file with a robust layout engine.
                    This version correctly handles paired gateways, ensures a single end event,
                    and uses Manhattan routing for clean, right-angled sequence flows.
                    FINAL FIX: Implements intelligent branch labeling and vertical alignment for converging gateways.
                    """
                    # --- Layout Constants ---
                    X_START, Y_START = 150, 250
                    TASK_BASE_WIDTH, TASK_BASE_HEIGHT = 100, 60
                    GATEWAY_SIZE, EVENT_SIZE = 50, 36
                    X_SPACING = 80
                    Y_SPACING = 60
                    CHARS_PER_LINE = 18
                    LINE_HEIGHT = 15
                    # New constant for the gap above the gateway
                    GATEWAY_LABEL_GAP = 5

                    def __init__(self, ir_dict, process_name="Process"):
                        self.ir = ir_dict
                        self.process_name = process_name
                        self.nodes = {}
                        self.flows = []
                        self.graph = {}
                        self.node_dims = {}
                        self.in_degree = {}

                        self.process_id = self._generate_id("Process")
                        self.collaboration_id = self._generate_id("Collaboration")
                        self.participant_id = self._generate_id("Participant")
                        self.lane_id = self._generate_id("Lane")
                        self.diagram_id = "BPMNDiagram_1"
                        self.plane_id = "BPMNPlane_1"

                    def _generate_id(self, prefix):
                        return f"{prefix}_{uuid.uuid4().hex[:8]}"

                    def _get_node_dimensions(self, node):
                        node_type = node['type']
                        if 'Event' in node_type: return self.EVENT_SIZE, self.EVENT_SIZE
                        if 'Gateway' in node_type: return self.GATEWAY_SIZE, self.GATEWAY_SIZE
                        text = node.get('name', '')
                        num_lines = max(1, (len(text) // self.CHARS_PER_LINE) + 1)
                        height = max(self.TASK_BASE_HEIGHT, num_lines * self.LINE_HEIGHT + 20)
                        return self.TASK_BASE_WIDTH, height

                    def generate(self):
                        if not self.ir.get('process'): return None
                        start_id, end_id = self._build_graph_from_ir(self.ir['process'])
                        self._calculate_dimensions(start_id)
                        self._position_nodes(start_id, self.X_START, self.Y_START)
                        return self._build_xml_structure()

                    def _build_graph_from_ir(self, flow_elements):
                        start_id = self._generate_id("StartEvent")
                        self.nodes[start_id] = {'type': 'startEvent', 'name': ''}
                        entry_points, exit_points = self._build_graph_recursively(flow_elements, [start_id])
                        end_id = self._generate_id("EndEvent")
                        self.nodes[end_id] = {'type': 'endEvent', 'name': ''}
                        for pred_id in exit_points:
                            self._add_flow(pred_id, end_id)
                        return start_id, end_id

                    def _build_graph_recursively(self, flow_elements, predecessor_ids):
                        if not flow_elements:
                            return predecessor_ids, predecessor_ids

                        entry_points = []

                        for i, element in enumerate(flow_elements):
                            node_id = self._generate_id(element.get('type', 'task').capitalize())
                            self.nodes[node_id] = {'type': element.get('type', 'task'),
                                                   'name': element.get('description', '')}

                            if i == 0:
                                entry_points.append(node_id)

                            for pred_id in predecessor_ids:
                                self._add_flow(pred_id, node_id)

                            if not element.get('type', '').endswith('Gateway'):
                                predecessor_ids = [node_id]
                            else:
                                self.nodes[node_id]['type'] = element['type']
                                merge_gateway_id = self._generate_id(f"Merge_{element['type']}")
                                self.nodes[merge_gateway_id] = {'type': element['type'], 'name': ''}
                                self.nodes[node_id]['merge_id'] = merge_gateway_id

                                for branch in element.get('branches', []):
                                    condition = branch.get('condition', '')
                                    branch_entry_points, branch_exit_ids = self._build_graph_recursively(
                                        branch.get('flow', []), [node_id])

                                    if branch_entry_points:
                                        first_node_in_branch = branch_entry_points[0]
                                        for flow in self.flows:
                                            if flow['source'] == node_id and flow['target'] == first_node_in_branch:
                                                flow['name'] = condition
                                                break

                                    for b_exit_id in branch_exit_ids:
                                        self._add_flow(b_exit_id, merge_gateway_id)

                                predecessor_ids = [merge_gateway_id]

                        return entry_points, predecessor_ids

                    def _add_flow(self, source_id, target_id, name=''):
                        if source_id not in self.graph: self.graph[source_id] = []
                        flow_id = self._generate_id("Flow")
                        self.graph[source_id].append({'target': target_id, 'id': flow_id, 'name': name})
                        self.flows.append({'id': flow_id, 'source': source_id, 'target': target_id, 'name': name})
                        self.in_degree[target_id] = self.in_degree.get(target_id, 0) + 1

                    def _calculate_dimensions(self, node_id):
                        if node_id in self.node_dims: return self.node_dims[node_id]
                        node = self.nodes[node_id]
                        w, h = self._get_node_dimensions(node)
                        if 'merge_id' not in node:
                            self.node_dims[node_id] = {'width': w, 'height': h}
                            successors = [edge['target'] for edge in self.graph.get(node_id, [])]
                            if successors:
                                child_dims = self._calculate_dimensions(successors[0])
                                self.node_dims[node_id]['width'] += self.X_SPACING + child_dims['width']
                                self.node_dims[node_id]['height'] = max(h, child_dims['height'])
                        else:
                            merge_id = node['merge_id']
                            branch_starts = [edge['target'] for edge in self.graph.get(node_id, [])]
                            branch_dims = [self._calculate_dimensions(bs_id) for bs_id in branch_starts]
                            max_branch_width = max([d['width'] for d in branch_dims]) if branch_dims else 0
                            total_branch_height = sum([d['height'] for d in branch_dims]) + max(0,
                                                                                                len(branch_dims) - 1) * self.Y_SPACING
                            gateway_width = w + self.X_SPACING + max_branch_width + self.X_SPACING + self.GATEWAY_SIZE
                            gateway_height = total_branch_height
                            self.node_dims[node_id] = {'width': gateway_width, 'height': gateway_height}
                            successors = [edge['target'] for edge in self.graph.get(merge_id, [])]
                            if successors:
                                child_dims = self._calculate_dimensions(successors[0])
                                self.node_dims[node_id]['width'] += self.X_SPACING + child_dims['width']
                                self.node_dims[node_id]['height'] = max(gateway_height, child_dims['height'])
                        return self.node_dims[node_id]

                    def _position_nodes(self, node_id, x, y):
                        if 'x' in self.nodes[node_id]: return
                        node = self.nodes[node_id]
                        dims = self.node_dims[node_id]
                        w, h = self._get_node_dimensions(node)
                        node['x'] = x
                        node['y'] = y + (dims['height'] - h) / 2
                        if 'merge_id' not in node:
                            successors = [edge['target'] for edge in self.graph.get(node_id, [])]
                            if successors:
                                self._position_nodes(successors[0], x + w + self.X_SPACING, y)
                        else:
                            merge_id = node['merge_id']
                            branch_starts = [edge['target'] for edge in self.graph.get(node_id, [])]
                            branch_dims = [self.node_dims[bs_id] for bs_id in branch_starts]
                            max_branch_width = max([d['width'] for d in branch_dims]) if branch_dims else 0
                            y_cursor = y
                            for i, bs_id in enumerate(branch_starts):
                                branch_height = branch_dims[i]['height']
                                self._position_nodes(bs_id, x + w + self.X_SPACING, y_cursor)
                                y_cursor += branch_height + self.Y_SPACING
                            merge_x = x + w + self.X_SPACING + max_branch_width + self.X_SPACING
                            merge_w, merge_h = self._get_node_dimensions(self.nodes[merge_id])
                            self.nodes[merge_id]['x'] = merge_x
                            self.nodes[merge_id]['y'] = y + (dims['height'] - merge_h) / 2
                            successors = [edge['target'] for edge in self.graph.get(merge_id, [])]
                            if successors:
                                self._position_nodes(successors[0], merge_x + merge_w + self.X_SPACING, y)

                    def _build_xml_structure(self):
                        NS = {'bpmn': "http://www.omg.org/spec/BPMN/20100524/MODEL"}
                        for prefix, uri in NS.items(): ET.register_namespace(prefix, uri)
                        ET.register_namespace('bpmndi', "http://www.omg.org/spec/BPMN/20100524/DI")
                        ET.register_namespace('dc', "http://www.omg.org/spec/DD/20100524/DC")
                        ET.register_namespace('di', "http://www.omg.org/spec/DD/20100524/DI")

                        self.root = ET.Element(f"{{{NS['bpmn']}}}definitions", {'id': self._generate_id('Definitions'),
                                                                                'targetNamespace': 'http://bpmn.io/schema/bpmn'})
                        collaboration = ET.SubElement(self.root, f"{{{NS['bpmn']}}}collaboration",
                                                      {'id': self.collaboration_id})
                        ET.SubElement(collaboration, f"{{{NS['bpmn']}}}participant",
                                      {'id': self.participant_id, 'processRef': self.process_id,
                                       'name': self.process_name})

                        process = ET.SubElement(self.root, f"{{{NS['bpmn']}}}process",
                                                {'id': self.process_id, 'isExecutable': 'false'})
                        lane_set = ET.SubElement(process, f"{{{NS['bpmn']}}}laneSet",
                                                 {'id': self._generate_id('LaneSet')})
                        lane_el = ET.SubElement(lane_set, f"{{{NS['bpmn']}}}lane",
                                                {'id': self.lane_id, 'name': "Process"})
                        for node_id in self.nodes:
                            ET.SubElement(lane_el, f"{{{NS['bpmn']}}}flowNodeRef").text = node_id

                        for node_id, node in self.nodes.items():
                            el_tag = node['type'] if 'Event' in node['type'] or 'Gateway' in node['type'] else 'task'
                            ET.SubElement(process, f"{{{NS['bpmn']}}}{el_tag}", {'id': node_id, 'name': node['name']})

                        for flow in self.flows:
                            ET.SubElement(process, f"{{{NS['bpmn']}}}sequenceFlow",
                                          {'id': flow['id'], 'sourceRef': flow['source'], 'targetRef': flow['target'],
                                           'name': flow['name']})

                        self._build_diagram_info()
                        return self._prettify_xml(self.root)

                    def _build_diagram_info(self):
                        NS_DI = {'bpmndi': "http://www.omg.org/spec/BPMN/20100524/DI",
                                 'dc': "http://www.omg.org/spec/DD/20100524/DC",
                                 'di': "http://www.omg.org/spec/DD/20100524/DI"}

                        diagram = ET.SubElement(self.root, f"{{{NS_DI['bpmndi']}}}BPMNDiagram", {'id': self.diagram_id})
                        plane = ET.SubElement(diagram, f"{{{NS_DI['bpmndi']}}}BPMNPlane",
                                              {'id': self.plane_id, 'bpmnElement': self.collaboration_id})

                        min_x, max_x, min_y, max_y = float('inf'), float('-inf'), float('inf'), float('-inf')
                        for node in self.nodes.values():
                            if 'x' not in node: continue
                            w, h = self._get_node_dimensions(node)
                            min_x, max_x = min(min_x, node['x']), max(max_x, node['x'] + w)
                            min_y, max_y = min(min_y, node['y']), max(max_y, node['y'] + h)

                        participant_width = (max_x - min_x) + 2 * self.X_SPACING
                        participant_height = (max_y - min_y) + 2 * self.Y_SPACING

                        ET.SubElement(plane, f"{{{NS_DI['bpmndi']}}}BPMNShape",
                                      {'id': f'{self.participant_id}_di', 'bpmnElement': self.participant_id,
                                       'isHorizontal': 'true'}).append(ET.Element(f"{{{NS_DI['dc']}}}Bounds",
                                                                                  {'x': str(
                                                                                      int(min_x - self.X_SPACING)),
                                                                                   'y': str(
                                                                                       int(min_y - self.Y_SPACING)),
                                                                                   'width': str(int(participant_width)),
                                                                                   'height': str(
                                                                                       int(participant_height))}))
                        ET.SubElement(plane, f"{{{NS_DI['bpmndi']}}}BPMNShape",
                                      {'id': f"{self.lane_id}_di", 'bpmnElement': self.lane_id,
                                       'isHorizontal': 'true'}).append(ET.Element(f"{{{NS_DI['dc']}}}Bounds", {
                            'x': str(int(min_x - self.X_SPACING + 30)), 'y': str(int(min_y - self.Y_SPACING)),
                            'width': str(int(participant_width - 30)), 'height': str(int(participant_height))}))

                        for node_id, node in self.nodes.items():
                            if 'x' not in node: continue
                            w, h = self._get_node_dimensions(node)

                            shape = ET.SubElement(plane, f"{{{NS_DI['bpmndi']}}}BPMNShape",
                                                  {'id': f'{node_id}_di', 'bpmnElement': node_id})
                            ET.SubElement(shape, f"{{{NS_DI['dc']}}}Bounds",
                                          {'x': str(int(node['x'])), 'y': str(int(node['y'])), 'width': str(w),
                                           'height': str(h)})

                            if node['name']:
                                label = ET.SubElement(shape, f"{{{NS_DI['bpmndi']}}}BPMNLabel")
                                is_gateway = 'Gateway' in node.get('type', '')

                                if is_gateway:
                                    # --- START OF THE FIX ---
                                    # Define a standard height for the label's text box
                                    num_lines = max(1, (len(node['name']) // self.CHARS_PER_LINE) + 1)
                                    label_box_height = num_lines * self.LINE_HEIGHT

                                    # Estimate width for centering
                                    label_width = len(node['name']) * 6 + 10

                                    # Center the label horizontally over the gateway
                                    label_x = node['x'] + (w / 2) - (label_width / 2)

                                    # Calculate Y to place the label's bottom edge a set gap above the gateway's top edge
                                    label_y = node['y'] - label_box_height - self.GATEWAY_LABEL_GAP

                                    ET.SubElement(label, f"{{{NS_DI['dc']}}}Bounds",
                                                  {'x': str(int(label_x)), 'y': str(int(label_y)),
                                                   'width': str(int(label_width)),
                                                   'height': str(int(label_box_height))})
                                    # --- END OF THE FIX ---
                                else:
                                    # Original logic for Tasks and Events
                                    node_label_height = self._get_node_dimensions(node)[1]
                                    ET.SubElement(label, f"{{{NS_DI['dc']}}}Bounds",
                                                  {'x': str(int(node['x'])), 'y': str(int(node['y'])), 'width': str(w),
                                                   'height': str(node_label_height)})

                        for flow in self.flows:
                            self._create_edge_waypoints(plane, flow)

                    def _create_edge_waypoints(self, plane, flow):
                        NS_DI = {'bpmndi': "http://www.omg.org/spec/BPMN/20100524/DI",
                                 'di': "http://www.omg.org/spec/DD/20100524/DI",
                                 'dc': "http://www.omg.org/spec/DD/20100524/DC"}
                        source_node, target_node = self.nodes[flow['source']], self.nodes[flow['target']]

                        s_w, s_h = self._get_node_dimensions(source_node)
                        t_w, t_h = self._get_node_dimensions(target_node)

                        s_cy = source_node['y'] + s_h / 2
                        t_cy = target_node['y'] + t_h / 2

                        edge = ET.SubElement(plane, f"{{{NS_DI['bpmndi']}}}BPMNEdge",
                                             {'id': f"{flow['id']}_di", 'bpmnElement': flow['id']})

                        start_x, start_y = source_node['x'] + s_w, s_cy
                        end_x, end_y = target_node['x'], t_cy

                        is_merge_target = self.in_degree.get(flow['target'], 1) > 1 and 'Gateway' in target_node['type']

                        ET.SubElement(edge, f"{{{NS_DI['di']}}}waypoint",
                                      {'x': str(int(start_x)), 'y': str(int(start_y))})

                        mid_x = start_x + self.X_SPACING / 2
                        if is_merge_target:
                            mid_x = end_x - self.X_SPACING / 2

                        if abs(start_y - end_y) > 1:
                            ET.SubElement(edge, f"{{{NS_DI['di']}}}waypoint",
                                          {'x': str(int(mid_x)), 'y': str(int(start_y))})
                            ET.SubElement(edge, f"{{{NS_DI['di']}}}waypoint",
                                          {'x': str(int(mid_x)), 'y': str(int(end_y))})

                        ET.SubElement(edge, f"{{{NS_DI['di']}}}waypoint", {'x': str(int(end_x)), 'y': str(int(end_y))})

                        if flow['name']:
                            label = ET.SubElement(edge, f"{{{NS_DI['bpmndi']}}}BPMNLabel")

                            label_x = mid_x - (len(flow['name']) * 7 / 2)
                            label_y = (start_y + end_y) / 2 - 7

                            if abs(start_y - end_y) <= 1:
                                label_x = start_x + 10
                                label_y = start_y - 20

                            ET.SubElement(label, f"{{{NS_DI['dc']}}}Bounds",
                                          {'x': str(int(label_x)), 'y': str(int(label_y)),
                                           'width': str(len(flow['name']) * 7), 'height': '14'})

                    def _prettify_xml(self, elem):
                        rough_string = ET.tostring(elem, 'utf-8', xml_declaration=True)
                        reparsed = minidom.parseString(rough_string)
                        return reparsed.toprettyxml(indent="  ", encoding="UTF-8").decode('utf-8')


                final_bpmn = generate_bpmn_xml(audited_ir)








            elif cleaned_result == 'MODIFY_WORKFLOW':
                if not st.session_state.current_workflow_ir:
                    response = "抱歉，当前没有可以修改的工作流。请先创建一个新的工作流。"
                    st.write(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                else:
                    response = f'''好的，收到您的修改指令："{prompt}"。即将对当前工作流进行修改...'''
                    st.write(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})


                    # 新增：工作流修改函数
                    def run_modification_phase(current_ir, modification_prompt):
                        st.markdown("---")
                        st.subheader("工作流修改阶段")
                        st.info("目标：根据您的指令，智能地修改当前的工作流。")

                        current_ir_str = json.dumps(current_ir, indent=2)

                        modifier_system_prompt = f'''
                        You are an expert BPMN Workflow Editor. Your task is to intelligently modify an existing workflow based on a user's natural language request. You will be given the current workflow's Intermediate Representation (IR) and a modification instruction. You must analyze both and produce the new, modified IR.

                        **[Core Principles]**
                        1.  **Understand the Intent:** Accurately interpret the user's request, whether it's to add, delete, rename, or re-sequence activities or gateways.
                        2.  **Preserve Structure:** Make the minimum necessary changes to the IR. Do not regenerate the entire structure from scratch.
                        3.  **Maintain Logic:** Ensure the resulting workflow remains logically coherent. For example, if adding a step, correctly identify where it should be inserted.
                        4.  **Be Explicit:** In your reasoning, clearly state what you are changing, adding, or removing.

                        **[GOLD-STANDARD EXAMPLE]**

                        **INPUT - Current IR:**
                        ```json
                        {{
                            "process": [
                                {{
                                    "type": "activity",
                                    "id": "act_1",
                                    "description": "Employee: Submit travel request"
                                }},
                                {{
                                    "type": "activity",
                                    "id": "act_2",
                                    "description": "Manager: Approve request"
                                }}
                            ]
                        }}
                        ```

                        **INPUT - User's Modification Request:**
                        "Add a 'Finance Department review' step after the manager's approval."

                        **YOUR CORRECT OUTPUT:**
                        <modification_reasoning>
                        *   **Action:** Add a new activity.
                        *   **Details:** A new activity 'Finance Department: Review travel request' will be inserted.
                        *   **Location:** It will be placed directly after the 'Manager: Approve request' activity.
                        </modification_reasoning>
                        <modified_ir>
                        ```python
                        {{
                            "process": [
                                {{
                                    "type": "activity",
                                    "id": "act_1",
                                    "description": "Employee: Submit travel request"
                                }},
                                {{
                                    "type": "activity",
                                    "id": "act_2",
                                    "description": "Manager: Approve request"
                                }},
                                {{
                                    "type": "activity",
                                    "id": "act_3_new",
                                    "description": "Finance Department: Review travel request"
                                }}
                            ]
                        }}
                        ```
                        </modified_ir>

                        **[CRITICAL OUTPUT INSTRUCTION]**
                        Your entire response MUST strictly follow the XML-like tag structure.
                        1.  You MUST include a `<modification_reasoning>` section explaining your changes.
                        2.  You MUST include a `<modified_ir>` section containing the final, modified Python code block.
                        3.  DO NOT add any other text, greetings, or explanations outside of these two required tags.

                        **[YOUR CURRENT TASK]**
                        Now, apply this logic to the following workflow modification task.

                        **Current Workflow IR:**
                        ```json
                        {current_ir_str}
                        ```

                        **User's Modification Request:**
                        "{modification_prompt}"
                        '''

                        with st.expander("执行工作流修改", expanded=True):
                            with st.spinner("AI 正在理解您的修改并更新工作流..."):
                                messages = [{'role': 'system', 'content': modifier_system_prompt},
                                            {'role': 'user',
                                             'content': f'Now you need to update this {current_ir_str} based on this modification request: "{modification_prompt}'}]
                                response = gpt_client.chat_completion(str(messages), temperature=0)

                                reasoning_match = re.search(r'<modification_reasoning>(.*?)</modification_reasoning>',
                                                            response, re.DOTALL)
                                ir_match = re.search(r'<modified_ir>\s*```python(.*?)```\s*</modified_ir>', response,
                                                     re.DOTALL)

                                reasoning = reasoning_match.group(1).strip() if reasoning_match else "未能解析修改报告。"
                                modified_ir = None
                                if ir_match:
                                    try:
                                        modified_ir_string = ir_match.group(1).strip()
                                        modified_ir = ast.literal_eval(modified_ir_string)
                                    except (ValueError, SyntaxError) as e:
                                        st.error(f"解析修改后的IR时出错: {e}")
                                        modified_ir = current_ir

                        st.info("#### 修改报告:")
                        st.markdown(reasoning)
                        if modified_ir:
                            st.success("#### 修改后的工作流 IR:")
                            st.code(json.dumps(modified_ir, indent=2), language="json")
                            return modified_ir
                        return current_ir


                    def generate_bpmn_xml(optimized_ir):
                        """
                        Converts the final optimized IR into a BPMN 2.0 XML string with layout.
                        """
                        st.markdown("---")
                        st.subheader("阶段六：BPMN 2.0 XML 生成")

                        if not optimized_ir or not optimized_ir.get('process'):
                            st.warning("无有效的优化版IR，无法生成BPMN。")
                            return

                        with st.spinner("正在将最终流程图转换为BPMN 2.0 XML..."):
                            try:
                                # Instantiate the robust generator
                                generator = BpmnXmlGenerator(optimized_ir)
                                bpmn_xml = generator.generate()
                                st.success("BPMN XML 生成成功！")
                                st.code(bpmn_xml, language='xml')
                                return bpmn_xml
                            except Exception as e:
                                st.error(f"生成BPMN时发生错误: {e}")
                                # Displaying the traceback helps in debugging future issues
                                st.error(traceback.format_exc())
                                return None


                    class BpmnXmlGenerator:
                        """
                        Generates a SINGLE-LANE BPMN 2.0 XML file with a robust layout engine.
                        This version correctly handles paired gateways, ensures a single end event,
                        and uses Manhattan routing for clean, right-angled sequence flows.
                        FINAL FIX: Implements intelligent branch labeling and vertical alignment for converging gateways.
                        """
                        # --- Layout Constants ---
                        X_START, Y_START = 150, 250
                        TASK_BASE_WIDTH, TASK_BASE_HEIGHT = 100, 60
                        GATEWAY_SIZE, EVENT_SIZE = 50, 36
                        X_SPACING = 80
                        Y_SPACING = 60
                        CHARS_PER_LINE = 18
                        LINE_HEIGHT = 15
                        # New constant for the gap above the gateway
                        GATEWAY_LABEL_GAP = 5

                        def __init__(self, ir_dict, process_name="Process"):
                            self.ir = ir_dict
                            self.process_name = process_name
                            self.nodes = {}
                            self.flows = []
                            self.graph = {}
                            self.node_dims = {}
                            self.in_degree = {}

                            self.process_id = self._generate_id("Process")
                            self.collaboration_id = self._generate_id("Collaboration")
                            self.participant_id = self._generate_id("Participant")
                            self.lane_id = self._generate_id("Lane")
                            self.diagram_id = "BPMNDiagram_1"
                            self.plane_id = "BPMNPlane_1"

                        def _generate_id(self, prefix):
                            return f"{prefix}_{uuid.uuid4().hex[:8]}"

                        def _get_node_dimensions(self, node):
                            node_type = node['type']
                            if 'Event' in node_type: return self.EVENT_SIZE, self.EVENT_SIZE
                            if 'Gateway' in node_type: return self.GATEWAY_SIZE, self.GATEWAY_SIZE
                            text = node.get('name', '')
                            num_lines = max(1, (len(text) // self.CHARS_PER_LINE) + 1)
                            height = max(self.TASK_BASE_HEIGHT, num_lines * self.LINE_HEIGHT + 20)
                            return self.TASK_BASE_WIDTH, height

                        def generate(self):
                            if not self.ir.get('process'): return None
                            start_id, end_id = self._build_graph_from_ir(self.ir['process'])
                            self._calculate_dimensions(start_id)
                            self._position_nodes(start_id, self.X_START, self.Y_START)
                            return self._build_xml_structure()

                        def _build_graph_from_ir(self, flow_elements):
                            start_id = self._generate_id("StartEvent")
                            self.nodes[start_id] = {'type': 'startEvent', 'name': ''}
                            entry_points, exit_points = self._build_graph_recursively(flow_elements, [start_id])
                            end_id = self._generate_id("EndEvent")
                            self.nodes[end_id] = {'type': 'endEvent', 'name': ''}
                            for pred_id in exit_points:
                                self._add_flow(pred_id, end_id)
                            return start_id, end_id

                        def _build_graph_recursively(self, flow_elements, predecessor_ids):
                            if not flow_elements:
                                return predecessor_ids, predecessor_ids

                            entry_points = []

                            for i, element in enumerate(flow_elements):
                                node_id = self._generate_id(element.get('type', 'task').capitalize())
                                self.nodes[node_id] = {'type': element.get('type', 'task'),
                                                       'name': element.get('description', '')}

                                if i == 0:
                                    entry_points.append(node_id)

                                for pred_id in predecessor_ids:
                                    self._add_flow(pred_id, node_id)

                                if not element.get('type', '').endswith('Gateway'):
                                    predecessor_ids = [node_id]
                                else:
                                    self.nodes[node_id]['type'] = element['type']
                                    merge_gateway_id = self._generate_id(f"Merge_{element['type']}")
                                    self.nodes[merge_gateway_id] = {'type': element['type'], 'name': ''}
                                    self.nodes[node_id]['merge_id'] = merge_gateway_id

                                    for branch in element.get('branches', []):
                                        condition = branch.get('condition', '')
                                        branch_entry_points, branch_exit_ids = self._build_graph_recursively(
                                            branch.get('flow', []), [node_id])

                                        if branch_entry_points:
                                            first_node_in_branch = branch_entry_points[0]
                                            for flow in self.flows:
                                                if flow['source'] == node_id and flow['target'] == first_node_in_branch:
                                                    flow['name'] = condition
                                                    break

                                        for b_exit_id in branch_exit_ids:
                                            self._add_flow(b_exit_id, merge_gateway_id)

                                    predecessor_ids = [merge_gateway_id]

                            return entry_points, predecessor_ids

                        def _add_flow(self, source_id, target_id, name=''):
                            if source_id not in self.graph: self.graph[source_id] = []
                            flow_id = self._generate_id("Flow")
                            self.graph[source_id].append({'target': target_id, 'id': flow_id, 'name': name})
                            self.flows.append({'id': flow_id, 'source': source_id, 'target': target_id, 'name': name})
                            self.in_degree[target_id] = self.in_degree.get(target_id, 0) + 1

                        def _calculate_dimensions(self, node_id):
                            if node_id in self.node_dims: return self.node_dims[node_id]
                            node = self.nodes[node_id]
                            w, h = self._get_node_dimensions(node)
                            if 'merge_id' not in node:
                                self.node_dims[node_id] = {'width': w, 'height': h}
                                successors = [edge['target'] for edge in self.graph.get(node_id, [])]
                                if successors:
                                    child_dims = self._calculate_dimensions(successors[0])
                                    self.node_dims[node_id]['width'] += self.X_SPACING + child_dims['width']
                                    self.node_dims[node_id]['height'] = max(h, child_dims['height'])
                            else:
                                merge_id = node['merge_id']
                                branch_starts = [edge['target'] for edge in self.graph.get(node_id, [])]
                                branch_dims = [self._calculate_dimensions(bs_id) for bs_id in branch_starts]
                                max_branch_width = max([d['width'] for d in branch_dims]) if branch_dims else 0
                                total_branch_height = sum([d['height'] for d in branch_dims]) + max(0,
                                                                                                    len(branch_dims) - 1) * self.Y_SPACING
                                gateway_width = w + self.X_SPACING + max_branch_width + self.X_SPACING + self.GATEWAY_SIZE
                                gateway_height = total_branch_height
                                self.node_dims[node_id] = {'width': gateway_width, 'height': gateway_height}
                                successors = [edge['target'] for edge in self.graph.get(merge_id, [])]
                                if successors:
                                    child_dims = self._calculate_dimensions(successors[0])
                                    self.node_dims[node_id]['width'] += self.X_SPACING + child_dims['width']
                                    self.node_dims[node_id]['height'] = max(gateway_height, child_dims['height'])
                            return self.node_dims[node_id]

                        def _position_nodes(self, node_id, x, y):
                            if 'x' in self.nodes[node_id]: return
                            node = self.nodes[node_id]
                            dims = self.node_dims[node_id]
                            w, h = self._get_node_dimensions(node)
                            node['x'] = x
                            node['y'] = y + (dims['height'] - h) / 2
                            if 'merge_id' not in node:
                                successors = [edge['target'] for edge in self.graph.get(node_id, [])]
                                if successors:
                                    self._position_nodes(successors[0], x + w + self.X_SPACING, y)
                            else:
                                merge_id = node['merge_id']
                                branch_starts = [edge['target'] for edge in self.graph.get(node_id, [])]
                                branch_dims = [self.node_dims[bs_id] for bs_id in branch_starts]
                                max_branch_width = max([d['width'] for d in branch_dims]) if branch_dims else 0
                                y_cursor = y
                                for i, bs_id in enumerate(branch_starts):
                                    branch_height = branch_dims[i]['height']
                                    self._position_nodes(bs_id, x + w + self.X_SPACING, y_cursor)
                                    y_cursor += branch_height + self.Y_SPACING
                                merge_x = x + w + self.X_SPACING + max_branch_width + self.X_SPACING
                                merge_w, merge_h = self._get_node_dimensions(self.nodes[merge_id])
                                self.nodes[merge_id]['x'] = merge_x
                                self.nodes[merge_id]['y'] = y + (dims['height'] - merge_h) / 2
                                successors = [edge['target'] for edge in self.graph.get(merge_id, [])]
                                if successors:
                                    self._position_nodes(successors[0], merge_x + merge_w + self.X_SPACING, y)

                        def _build_xml_structure(self):
                            NS = {'bpmn': "http://www.omg.org/spec/BPMN/20100524/MODEL"}
                            for prefix, uri in NS.items(): ET.register_namespace(prefix, uri)
                            ET.register_namespace('bpmndi', "http://www.omg.org/spec/BPMN/20100524/DI")
                            ET.register_namespace('dc', "http://www.omg.org/spec/DD/20100524/DC")
                            ET.register_namespace('di', "http://www.omg.org/spec/DD/20100524/DI")

                            self.root = ET.Element(f"{{{NS['bpmn']}}}definitions",
                                                   {'id': self._generate_id('Definitions'),
                                                    'targetNamespace': 'http://bpmn.io/schema/bpmn'})
                            collaboration = ET.SubElement(self.root, f"{{{NS['bpmn']}}}collaboration",
                                                          {'id': self.collaboration_id})
                            ET.SubElement(collaboration, f"{{{NS['bpmn']}}}participant",
                                          {'id': self.participant_id, 'processRef': self.process_id,
                                           'name': self.process_name})

                            process = ET.SubElement(self.root, f"{{{NS['bpmn']}}}process",
                                                    {'id': self.process_id, 'isExecutable': 'false'})
                            lane_set = ET.SubElement(process, f"{{{NS['bpmn']}}}laneSet",
                                                     {'id': self._generate_id('LaneSet')})
                            lane_el = ET.SubElement(lane_set, f"{{{NS['bpmn']}}}lane",
                                                    {'id': self.lane_id, 'name': "Process"})
                            for node_id in self.nodes:
                                ET.SubElement(lane_el, f"{{{NS['bpmn']}}}flowNodeRef").text = node_id

                            for node_id, node in self.nodes.items():
                                el_tag = node['type'] if 'Event' in node['type'] or 'Gateway' in node[
                                    'type'] else 'task'
                                ET.SubElement(process, f"{{{NS['bpmn']}}}{el_tag}",
                                              {'id': node_id, 'name': node['name']})

                            for flow in self.flows:
                                ET.SubElement(process, f"{{{NS['bpmn']}}}sequenceFlow",
                                              {'id': flow['id'], 'sourceRef': flow['source'],
                                               'targetRef': flow['target'],
                                               'name': flow['name']})

                            self._build_diagram_info()
                            return self._prettify_xml(self.root)

                        def _build_diagram_info(self):
                            NS_DI = {'bpmndi': "http://www.omg.org/spec/BPMN/20100524/DI",
                                     'dc': "http://www.omg.org/spec/DD/20100524/DC",
                                     'di': "http://www.omg.org/spec/DD/20100524/DI"}

                            diagram = ET.SubElement(self.root, f"{{{NS_DI['bpmndi']}}}BPMNDiagram",
                                                    {'id': self.diagram_id})
                            plane = ET.SubElement(diagram, f"{{{NS_DI['bpmndi']}}}BPMNPlane",
                                                  {'id': self.plane_id, 'bpmnElement': self.collaboration_id})

                            min_x, max_x, min_y, max_y = float('inf'), float('-inf'), float('inf'), float('-inf')
                            for node in self.nodes.values():
                                if 'x' not in node: continue
                                w, h = self._get_node_dimensions(node)
                                min_x, max_x = min(min_x, node['x']), max(max_x, node['x'] + w)
                                min_y, max_y = min(min_y, node['y']), max(max_y, node['y'] + h)

                            participant_width = (max_x - min_x) + 2 * self.X_SPACING
                            participant_height = (max_y - min_y) + 2 * self.Y_SPACING

                            ET.SubElement(plane, f"{{{NS_DI['bpmndi']}}}BPMNShape",
                                          {'id': f'{self.participant_id}_di', 'bpmnElement': self.participant_id,
                                           'isHorizontal': 'true'}).append(ET.Element(f"{{{NS_DI['dc']}}}Bounds",
                                                                                      {'x': str(
                                                                                          int(min_x - self.X_SPACING)),
                                                                                          'y': str(
                                                                                              int(min_y - self.Y_SPACING)),
                                                                                          'width': str(
                                                                                              int(participant_width)),
                                                                                          'height': str(
                                                                                              int(participant_height))}))
                            ET.SubElement(plane, f"{{{NS_DI['bpmndi']}}}BPMNShape",
                                          {'id': f"{self.lane_id}_di", 'bpmnElement': self.lane_id,
                                           'isHorizontal': 'true'}).append(ET.Element(f"{{{NS_DI['dc']}}}Bounds", {
                                'x': str(int(min_x - self.X_SPACING + 30)), 'y': str(int(min_y - self.Y_SPACING)),
                                'width': str(int(participant_width - 30)), 'height': str(int(participant_height))}))

                            for node_id, node in self.nodes.items():
                                if 'x' not in node: continue
                                w, h = self._get_node_dimensions(node)

                                shape = ET.SubElement(plane, f"{{{NS_DI['bpmndi']}}}BPMNShape",
                                                      {'id': f'{node_id}_di', 'bpmnElement': node_id})
                                ET.SubElement(shape, f"{{{NS_DI['dc']}}}Bounds",
                                              {'x': str(int(node['x'])), 'y': str(int(node['y'])), 'width': str(w),
                                               'height': str(h)})

                                if node['name']:
                                    label = ET.SubElement(shape, f"{{{NS_DI['bpmndi']}}}BPMNLabel")
                                    is_gateway = 'Gateway' in node.get('type', '')

                                    if is_gateway:
                                        # --- START OF THE FIX ---
                                        # Define a standard height for the label's text box
                                        num_lines = max(1, (len(node['name']) // self.CHARS_PER_LINE) + 1)
                                        label_box_height = num_lines * self.LINE_HEIGHT

                                        # Estimate width for centering
                                        label_width = len(node['name']) * 6 + 10

                                        # Center the label horizontally over the gateway
                                        label_x = node['x'] + (w / 2) - (label_width / 2)

                                        # Calculate Y to place the label's bottom edge a set gap above the gateway's top edge
                                        label_y = node['y'] - label_box_height - self.GATEWAY_LABEL_GAP

                                        ET.SubElement(label, f"{{{NS_DI['dc']}}}Bounds",
                                                      {'x': str(int(label_x)), 'y': str(int(label_y)),
                                                       'width': str(int(label_width)),
                                                       'height': str(int(label_box_height))})
                                        # --- END OF THE FIX ---
                                    else:
                                        # Original logic for Tasks and Events
                                        node_label_height = self._get_node_dimensions(node)[1]
                                        ET.SubElement(label, f"{{{NS_DI['dc']}}}Bounds",
                                                      {'x': str(int(node['x'])), 'y': str(int(node['y'])),
                                                       'width': str(w),
                                                       'height': str(node_label_height)})

                            for flow in self.flows:
                                self._create_edge_waypoints(plane, flow)

                        def _create_edge_waypoints(self, plane, flow):
                            NS_DI = {'bpmndi': "http://www.omg.org/spec/BPMN/20100524/DI",
                                     'di': "http://www.omg.org/spec/DD/20100524/DI",
                                     'dc': "http://www.omg.org/spec/DD/20100524/DC"}
                            source_node, target_node = self.nodes[flow['source']], self.nodes[flow['target']]

                            s_w, s_h = self._get_node_dimensions(source_node)
                            t_w, t_h = self._get_node_dimensions(target_node)

                            s_cy = source_node['y'] + s_h / 2
                            t_cy = target_node['y'] + t_h / 2

                            edge = ET.SubElement(plane, f"{{{NS_DI['bpmndi']}}}BPMNEdge",
                                                 {'id': f"{flow['id']}_di", 'bpmnElement': flow['id']})

                            start_x, start_y = source_node['x'] + s_w, s_cy
                            end_x, end_y = target_node['x'], t_cy

                            is_merge_target = self.in_degree.get(flow['target'], 1) > 1 and 'Gateway' in target_node[
                                'type']

                            ET.SubElement(edge, f"{{{NS_DI['di']}}}waypoint",
                                          {'x': str(int(start_x)), 'y': str(int(start_y))})

                            mid_x = start_x + self.X_SPACING / 2
                            if is_merge_target:
                                mid_x = end_x - self.X_SPACING / 2

                            if abs(start_y - end_y) > 1:
                                ET.SubElement(edge, f"{{{NS_DI['di']}}}waypoint",
                                              {'x': str(int(mid_x)), 'y': str(int(start_y))})
                                ET.SubElement(edge, f"{{{NS_DI['di']}}}waypoint",
                                              {'x': str(int(mid_x)), 'y': str(int(end_y))})

                            ET.SubElement(edge, f"{{{NS_DI['di']}}}waypoint",
                                          {'x': str(int(end_x)), 'y': str(int(end_y))})

                            if flow['name']:
                                label = ET.SubElement(edge, f"{{{NS_DI['bpmndi']}}}BPMNLabel")

                                label_x = mid_x - (len(flow['name']) * 7 / 2)
                                label_y = (start_y + end_y) / 2 - 7

                                if abs(start_y - end_y) <= 1:
                                    label_x = start_x + 10
                                    label_y = start_y - 20

                                ET.SubElement(label, f"{{{NS_DI['dc']}}}Bounds",
                                              {'x': str(int(label_x)), 'y': str(int(label_y)),
                                               'width': str(len(flow['name']) * 7), 'height': '14'})

                        def _prettify_xml(self, elem):
                            rough_string = ET.tostring(elem, 'utf-8', xml_declaration=True)
                            reparsed = minidom.parseString(rough_string)
                            return reparsed.toprettyxml(indent="  ", encoding="UTF-8").decode('utf-8')


                    # 调用新的修改函数
                    modified_ir = run_modification_phase(st.session_state.current_workflow_ir, prompt)

                    if modified_ir:
                        # 使用修改后的IR重新生成BPMN
                        final_bpmn = generate_bpmn_xml(modified_ir)
                        # 更新会话状态中的工作流
                        st.session_state.current_workflow_ir = modified_ir
else:
    st.warning("请输入您的 Google Gemini API Key 以启动CoRePro构造器。")
    st.info("您可以从 Google AI for Developers 网站获取您的 API Key。")


