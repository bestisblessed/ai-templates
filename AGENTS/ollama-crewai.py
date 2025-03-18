import os
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from crewai_tools import FileReadTool

os.environ["OPENAI_API_KEY"] = "sk-proj-1111"

llm = ChatOpenAI(
    # model="phi3:3.8b",
    model="ollama/codellama:7b",
    base_url="http://localhost:11434/v1"
)

# Create file tools for accessing the CSV data
file_tool_fighter_info = FileReadTool(file_path="./data/fighter_info.csv")
file_tool_event_data = FileReadTool(file_path="./data/event_data_sherdog.csv")

# Define fighters for analysis
fighter1 = "Paddy Pimblett"
fighter2 = "Michael Chandler"

# Create agents
agent1 = Agent(
    role='Fight Researcher & Analyst',
    goal='Gather comprehensive information about upcoming UFC fights',
    backstory=
        """As a seasoned analyst with a deep understanding of MMA/UFC, you specialize
        in breaking down fights and understanding fighter tendencies and histories.""",
    tools=[file_tool_fighter_info, file_tool_event_data],
    allow_delegation=True,
    verbose=True,
    llm=llm
)

agent2 = Agent(
    role='Expert MMA Handicapper',
    goal='Predict the outcome of the upcoming UFC fight based on gathered data and professional techniques',
    backstory=
        """As a expert analyst and oddsmaker with a deep understanding of MMA/UFC,
        you specialize in breaking down and handicapping fights.
        Equipped with advanced predictive modeling and professional handicapping knowledge,
        you use and evaluate data to predict hypothetical fight outcomes with high accuracy.""",
    tools=[file_tool_fighter_info, file_tool_event_data],
    allow_delegation=True,
    verbose=True,
    llm=llm
)

# Create tasks
task1 = Task(
    description=f'Research the fighters involved in the upcoming UFC fight between {fighter1} and {fighter2} and gather relevant data such as fight history, style, and recent performance.',
    expected_output='A detailed report on the fighters, including their strengths, weaknesses, and recent fight outcomes.',
    agent=agent1,
    max_iter=10,
    output_file='upcoming_fight_research.md'
)

# New task to find and summarize recent fights
task_recent_fights = Task(
    description=f'Find and summarize the most recent 5 fights for both {fighter1} and {fighter2}. For each fight, include: date, opponent, result (win/loss), method of victory/defeat (KO, submission, decision), and a brief description of how the fight played out.',
    expected_output='A detailed summary of the 10 most recent fights (5 for each fighter) with all relevant information organized chronologically for each fighter.',
    agent=agent1,
    max_iter=8,
    output_file='recent_fights_summary.md'
)

task_final = Task(
    description='Analyze the research report and predict the outcome of the upcoming UFC fight. Provide a rationale for the prediction.',
    expected_output='A prediction of the fight outcome with a clear explanation of the reasoning behind it.',
    agent=agent2,
    max_iter=10,
    output_file='upcoming_fight_prediction.md'
)

# Create the crew
crew = Crew(
    agents=[agent1, agent2],
    tasks=[task1, task_recent_fights, task_final],
    verbose=True
)

# Run the crew
result = crew.kickoff()
print("############")
print(result)
