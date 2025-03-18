import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from crewai import Agent, Task, Crew
from crewai_tools import (
    DirectoryReadTool,
    FileReadTool,
    SerperDevTool,
    WebsiteSearchTool
)

load_dotenv()
# os.environ["OPENAI_API_KEY"] = "sk-proj-1111"
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# SERPER_API_KEY = os.getenv("SERPER_API_KEY")

ollama_model = ChatOpenAI(
    # model="ollama/phi3:3.8b",
    model="ollama/llama3.2:latest",
    # model="ollama/codellama:7b",
    # model="ollama/deepseek-r1:8b",
    # model="ollama/qwen2.5",
    base_url="http://localhost:11434/v1"
)


### Instantiate tools ###
docs_tool = DirectoryReadTool(directory='./data')
file_tool = FileReadTool()
search_tool = SerperDevTool()
web_rag_tool = WebsiteSearchTool()



### Create agents ###
researcher = Agent(
    role='Market Research Analyst',
    goal='Provide up-to-date market analysis of the AI industry',
    backstory='An expert analyst with a keen eye for market trends.',
    tools=[search_tool, web_rag_tool],
    verbose=True
)
writer = Agent(
    role='Content Writer',
    goal='Craft engaging blog posts about the AI industry',
    backstory='A skilled writer with a passion for technology.',
    tools=[docs_tool, file_tool],
    verbose=True
)



### Run tasks ###
research = Task(
    description='Research the latest trends in the AI industry and provide a summary.',
    expected_output='A summary of the top 3 trending developments in the AI industry with a unique perspective on their significance.',
    agent=researcher
)
write = Task(
    description='Write an engaging blog post about the AI industry, based on the research analyst’s summary. Draw inspiration from the latest blog posts in the directory.',
    expected_output='A 4-paragraph blog post formatted in markdown with engaging, informative, and accessible content, avoiding complex jargon.',
    agent=writer,
    output_file='blog-posts/new_post.md'  # The final blog post will be saved here
)
crew = Crew(
    agents=[researcher, writer],
    tasks=[research, write],
    verbose=True,
    planning=True,  # Enable planning feature
)
crew.kickoff()