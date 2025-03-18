from autogen import AssistantAgent, UserProxyAgent
import os

# Define the configuration for the Code Llama model
config_list = [
    {
        "model": "codellama:7b-instruct",
        # "model": "ollama/codellama:7b-instruct",
        "base_url": "http://localhost:11434/v1",
        "api_key": "ollama",
    }
]

# Create the directory if it doesn't exist
os.makedirs("/Users/td/Code/ai-templates/AGENTS", exist_ok=True)

# Create an AssistantAgent with the Code Llama model and better instructions
system_message = """You are a helpful AI assistant that writes Python code.
For finance-related tasks, always use yfinance library, not yahoo_finance.
Keep your code concise and ensure you properly import all required libraries including matplotlib.pyplot.
Always include code to display and save plots when generating charts."""

assistant = AssistantAgent(
    "assistant", 
    system_message=system_message,
    llm_config={"config_list": config_list},
    # Limit the number of consecutive auto-replies to prevent loops
    max_consecutive_auto_reply=2
)

# Create a UserProxyAgent that automatically executes code without user confirmation
# user_proxy = UserProxyAgent("user_proxy", code_execution_config={"work_dir": "coding", "use_docker": False})
user_proxy = UserProxyAgent(
    "user_proxy", 
    code_execution_config={
        "work_dir": "/Users/td/Code/ai-templates/AGENTS/coding",
        "use_docker": False,
    },
    human_input_mode="NEVER",  # This prevents asking for user input
    max_consecutive_auto_reply=3,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE")
)

# Initiate a chat between the user proxy and the assistant
user_proxy.initiate_chat(
    assistant, 
    message="Plot a chart of TSLA stock price change YTD and save in a file. Use yfinance to get the data and matplotlib to create the chart.",
    max_turns=2  # Limit the conversation to 2 turns
)