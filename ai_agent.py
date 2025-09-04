from typing import TypedDict, Annotated, Sequence, List, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph,END
from langgraph.prebuilt import ToolNode
from algorithm import choose_the_food
from langchain.tools import tool
from dotenv import load_dotenv
import time
import os

load_dotenv()

class AgentState(TypedDict):
    messages : Annotated[Sequence[BaseMessage],add_messages]



@tool
def suggest_recipe(ingredients:Optional[List[str]]=None):
    """Suggest recipe for user and save ingredients
    """

    filename = "../products.txt"
    if not filename.endswith('.txt'):
        filename = f"{filename}.txt"

    if ingredients is not None:
        with open(filename,'a') as file:
            for ingredient in ingredients:
                file.write(ingredient)
                file.write('\n')

    with open(filename,'r') as file:
        products = []
        for line in file:
            products.append(line.strip())
        percent,choice = choose_the_food(products)

    return f"We advice to you cook {choice} - {percent}%"


tools = [suggest_recipe]
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    api_key=os.getenv("GEMINI_API_KEY_2"),
    max_retries=2,
    temperature=.1
).bind_tools(tools)

def model_call(state:AgentState):
    system_prompt = SystemMessage(content=f""" 
    You are "Kitchen Assistant AI Agent".

    Your behavior is rule-based:

    1. If the user provides a list of ingredients (examples: "I have tomato and cucumber", "My ingredients are eggs and rice"):
        - Call the function save_ingredients(ingredients: List[str]) with all the ingredients mentioned.
        - Do not give the recipe yet. Just confirm by calling the function.

    2. If the user asks what to cook / prepare (examples: "What to cook today?", "What can I prepare?", "Suggest a dish"):
        - Call the function suggest_recipe() to generate a recipe suggestion.
        - After receiving the recipe suggestion, respond to the user with:
            🔹 The dish name  
            🔹 A short description of the dish  

    Important:
    - Always use function calls, not free text, when saving ingredients or suggesting recipes.
    - Never skip calling suggest_recipe when the user explicitly asks what to cook/prepare.

"""
                                  )

    response = llm.invoke([system_prompt] + state["messages"])
    return {"messages":[response]}

def continue_conversation(state:AgentState):
    messages = state["messages"]
    last_message = messages[-1]
    if not last_message.tool_calls:
        return "end"
    else:
        return "continue"


graph = StateGraph(AgentState)
graph.add_node('llm',model_call)

tool_node = ToolNode(tools = tools)
graph.add_node("tools",tool_node)

graph.set_entry_point('llm')
graph.add_conditional_edges(
    "llm",
    continue_conversation,
    {
        "continue":"tools",
        "end":END,
    }
)

graph.add_edge("llm","tools")

app = graph.compile()



