# Import necessary libraries
from agents import Agent, Runner, function_tool, WebSearchTool
import pandas as pd
import matplotlib.pyplot as plt
import nest_asyncio
import os
from dotenv import load_dotenv
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_experimental.tools import PythonAstREPLTool

# Apply nest_asyncio to make async code work in Jupyter
nest_asyncio.apply()

# Load environment variables if needed
load_dotenv()

# Ensure data/ directory exists
if not os.path.exists("data"):
    os.makedirs("data")

# Define paths to your CSV files
FIGHTER_CSV_PATH = "data/fighter_info.csv"
EVENT_CSV_PATH = "data/event_data_sherdog.csv"

# Load the data using pandas
fighter_df = pd.read_csv(FIGHTER_CSV_PATH)
event_df = pd.read_csv(EVENT_CSV_PATH)

# MMA-specific tools
@function_tool
def execute_python_code(code: str) -> str:
    """Execute Python code to analyze UFC/MMA data and create visualizations.
    If matplotlib figures are generated, they are saved to the data/ directory."""
    namespace = {
        "pd": pd,
        "plt": plt,
        "fighter_df": fighter_df,
        "event_df": event_df,
        "os": os,
    }
    repl = PythonAstREPLTool(locals=namespace)
    
    try:
        result = repl.run(code)
        return f"Code executed successfully:\n{result}"
    except Exception as e:
        return f"Error executing code: {str(e)}"
    
    # Check for any generated figures
    fig_nums = plt.get_fignums()
    save_messages = ""
    if fig_nums:
        for fig_num in fig_nums:
            filename = f"data/figure_{fig_num}.png"
            plt.figure(fig_num).savefig(filename, dpi=100)
            save_messages += f"Figure {fig_num} saved to {filename}\n"
            plt.close(fig_num)
    
    return f"Code executed successfully:\n{result}\n{save_messages}"

# Create function tool for CSV analysis
@function_tool
def get_csv_data_info() -> str:
    """Get information about the available UFC/MMA CSV data."""
    fighter_info = f"Fighter DataFrame: {len(fighter_df)} rows, {len(fighter_df.columns)} columns\nColumns: {', '.join(fighter_df.columns)}\n"
    event_info = f"Event DataFrame: {len(event_df)} rows, {len(event_df.columns)} columns\nColumns: {', '.join(event_df.columns)}\n"
    fighter_sample = f"Sample fighter data:\n{fighter_df.head(3).to_string()}\n"
    event_sample = f"Sample event data:\n{event_df.head(3).to_string()}"
    return fighter_info + event_info + fighter_sample + event_sample

# Create your agents
web_search_agent = Agent(
    name="Web Search Agent",
    handoff_description="Specialist agent for web search for ONLY upcoming information or current information, not about fighter historical research ever.",
    instructions="You search the web for information. At the beginning of your response, print your name 'Web Search'.",
    model="gpt-4o-mini",
    tools=[WebSearchTool(search_context_size="low")]
)

fight_analyst_agent = Agent(
    name="Fight Analyst",
    handoff_description="Specialist agent for UFC/MMA fight analysis using CSV data",
    instructions="""You are a UFC/MMA fight analyst who can answer questions about fighters and events.
    
    At the beginning of your response, print your name 'Fight Analyst'.
    
    You have access to two dataframes:
    1. fighter_df - contains information about UFC fighters
    2. event_df - contains information about UFC events
    
    When asked a question:
    1. First use get_csv_data_info() if you need to understand what data is available
    2. Then write Python code using pandas and matplotlib to analyze the data and create visualizations
    3. Use execute_python_code() to run your analysis
    
    Always explain your reasoning and what insights can be gained from the data.
    
    IMPORTANT: When writing visualization code, add plt.close() at the end to prevent memory leaks.
    """,
    model="o3-mini",
    tools=[execute_python_code, get_csv_data_info]
)

# Define the triage agent
triage_agent = Agent(
    name="Triage Agent",
    instructions="You determine which agent to use based on the user's question. Print which agent you decide:",
    # model="gpt-4o-mini",
    model="gpt-3.5-turbo",
    handoffs=[web_search_agent, fight_analyst_agent]
)

# Function to run a user query
def ask_question(question):
    result = Runner.run_sync(triage_agent, question)
    print(result.final_output)
    return result
if __name__ == "__main__":
    
    ask_question("List the most recent 3 UFC events in your dataset")
    # ask_question("Tell me about Max Holloway's most recent 3 fights and outcomes in your dataset")
    # ask_question("Which weight class has the most fighters and can you create a visualization?")
    # ask_question("When is the very next UFC event?")
    # ask_question("What are the top 5 fighters by knockout wins and can you create a visualization?")
    # ask_question("Who has the longest winning streak in the dataset and can you create a visualization?")
    # ask_question("What is the average fight duration in the dataset?")
    ask_question("What are Paddy Pimblett's methods of victories in a pie chart?")