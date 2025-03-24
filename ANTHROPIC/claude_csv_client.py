from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import anthropic
import os
import json
import traceback

# Anthropic client
def get_claude_client():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
    return anthropic.Anthropic(api_key=api_key)

async def analyze_csv_with_mcp():
    # Updated file path to use the tiny sample file
    filepath = "/Users/td/Code/ai-templates/ANTHROPIC/data/event_data_sherdog_tiny.csv"
    
    # Check if file exists
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"CSV file not found: {filepath}")
    
    server_params = StdioServerParameters(
        command="python",
        args=["claude_csv_server.py"],
        timeout=15  # Add 15 second timeout for entire operation
    )
    
    print(f"Starting full analysis of: {filepath}")
    
    arguments = {
        "filepath": filepath,
        "minimal": True,  # Use minimal profile for faster processing
        "timeout": 10     # Set a 10 second timeout for profiling
    }
    
    try:
        async with stdio_client(server_params) as (read, write):
            try:
                async with ClientSession(read, write) as session:
                    print("Initializing session...")
                    await session.initialize()
                    
                    # Get available tools
                    print("Listing available tools...")
                    tools_result = await session.list_tools()
                    print(f"Tools response type: {type(tools_result)}")
                    
                    tool_names = []
                    analyze_csv_available = False
                    
                    # Handle ListToolsResult specifically
                    if hasattr(tools_result, 'tools'):
                        for tool in tools_result.tools:
                            if hasattr(tool, 'name'):
                                tool_names.append(tool.name)
                                if tool.name == "analyze_csv":
                                    analyze_csv_available = True
                                    print(f"Found analyze_csv tool with schema: {tool.inputSchema}")
                    
                    print(f"Available tool names: {json.dumps(tool_names, indent=2)}")
                    
                    if not analyze_csv_available:
                        print("Warning: analyze_csv tool not found in available tools")
                        print("Attempting to call it anyway...")
                    
                    # # Call the analyze_csv tool
                    # print(f"Calling analyze_csv tool with arguments: {json.dumps(arguments)}")
                    # result = await session.call_tool("analyze_csv", arguments=arguments)
                    
                    # print(f"Result type: {type(result)}")
                    
                    
                    # Call the analyze_csv tool
                    print(f"Calling analyze_csv tool with arguments: {json.dumps(arguments)}")
                    result = await session.call_tool("analyze_csv", arguments=arguments)
                    
                    print(f"Result type: {type(result)}")
                    
                    # Simplified result handling
                    if hasattr(result, 'content'):
                        return result.content[0].text
                    elif isinstance(result, (list, tuple)) and result:
                        return result[0].text if hasattr(result[0], 'text') else str(result[0])
                    else:
                        return str(result)
                    
                    # # Handle ToolResult specifically
                    # if hasattr(result, 'content') and len(result.content) > 0:
                    #     content = result.content[0]
                    #     if hasattr(content, 'text'):
                    #         return content.text
                    #     else:
                    #         print(f"Content has no 'text' attribute: {content}")
                    #         return json.dumps(content.__dict__)
                    # elif isinstance(result, list) and len(result) > 0:
                    #     if hasattr(result[0], 'text'):
                    #         return result[0].text
                    #     else:
                    #         print(f"Result item has no 'text' attribute: {result[0]}")
                    #         return json.dumps(result[0].__dict__ if hasattr(result[0], '__dict__') else str(result[0]))
                    # else:
                    #     raise ValueError(f"Unable to extract text from result: {result}")
            except Exception as e:
                print(f"Error in ClientSession: {str(e)}")
                traceback.print_exc()
                raise
    # except Exception as e:
    #     print(f"Error in stdio_client: {str(e)}")
    #     traceback.print_exc()
    #     raise
    except Exception as e:
        print(f"Error in stdio_client: {str(e)}")
        traceback.print_exc()
        raise
    finally:
        # Force cleanup of resources
        if 'session' in locals():
            await session.close()
        if 'read' in locals() and 'write' in locals():
            await read.aclose()
            await write.aclose()
            
async def get_claude_insights(result_text):
    claude_client = get_claude_client()
    try:
        analysis_results = json.loads(result_text)
        
        # Check if there was an error
        if isinstance(analysis_results, dict) and analysis_results.get("isError", False):
            return f"Error during analysis: {analysis_results.get('message', 'Unknown error')}"
        
        prompt = f"""
Here are the analysis results of my CSV file:

File Statistics:
- Rows: {analysis_results.get('rows')}
- Columns: {analysis_results.get('columns')}
- Missing cells: {analysis_results.get('missing_cells')} ({analysis_results.get('missing_cells_ratio', 0)*100:.2f}%)
- Duplicates: {analysis_results.get('duplicates')}

Column Types:
- Numeric columns: {analysis_results.get('column_types', {}).get('numeric', [])}
- Categorical columns: {analysis_results.get('column_types', {}).get('categorical', [])}
- Date columns: {analysis_results.get('column_types', {}).get('date', [])}

Detailed Column Statistics:
{json.dumps(analysis_results.get('column_stats', {}), indent=2)}

Please interpret these results and provide insights. Focus on:
1. Overall data quality assessment
2. Any anomalies or patterns
3. Recommendations for further analysis or preprocessing
"""
    except json.JSONDecodeError:
        prompt = f"Here are the analysis results of my CSV file. Please interpret these results and provide insights:\n\n{result_text}"
    
    message = claude_client.messages.create(
        model="claude-3.5-sonnet-20241022",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content

async def amain():
    try:
        result_text = await analyze_csv_with_mcp()
        print("\nRaw Analysis Results:")
        print(result_text)
        
        insights = await get_claude_insights(result_text)
        print("\nClaude's Insights:")
        print(insights)
        
        print("\nAnalysis complete! Check the 'reports' directory for the full HTML report.")
    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    import anyio
    anyio.run(amain)

# from mcp import ClientSession, StdioServerParameters
# from mcp.client.stdio import stdio_client
# import anthropic
# import os
# import json

# # Anthropic client
# claude_client = anthropic.Anthropic(
#     api_key=os.environ.get("ANTHROPIC_API_KEY"),
# )

# # Server parameters
# server_params = StdioServerParameters(
#     command="python",
#     args=["csv_server.py"],
# )

# async def main():
#     async with stdio_client(server_params) as (read, write):
#         async with ClientSession(read, write) as session:
#             # Initialize
#             await session.initialize()
            
#             # List available tools
#             tools = await session.list_tools()
            
#             # Call the analyze_csv tool
#             result = await session.call_tool(
#                 "analyze_csv", 
#                 arguments={
#                     "filepath": "/Users/td/Code/mma-ai/Scrapers/data/event_data_sherdog.csv",
#                     "operations": ["head", "count", "describe"],
#                     "columns": ["column1", "column2"]  # Replace with actual column names
#                 }
#             )
            
#             # Get the result text
#             result_text = result.content[0].text
            
#             # Use Claude to interpret the results
#             message = claude_client.messages.create(
#                 model="claude-3.5-sonnet-20241022",
#                 max_tokens=1024,
#                 messages=[
#                     {"role": "user", "content": f"Here are the analysis results of my CSV file. Please interpret these results and provide insights:\n\n{result_text}"}
#                 ]
#             )
            
#             print(message.content)

# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(main())