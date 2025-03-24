from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import anthropic
import os
import json
import traceback
import asyncio

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
                    
                    # Call the analyze_csv tool
                    print(f"Calling analyze_csv tool with arguments: {json.dumps(arguments)}")
                    
                    # Add timeout for the call_tool operation
                    try:
                        result = await asyncio.wait_for(
                            session.call_tool("analyze_csv", arguments=arguments),
                            timeout=12  # 12 second timeout for the tool call
                        )
                        print(f"Tool call completed! Result type: {type(result)}")
                    except asyncio.TimeoutError:
                        print("Tool call timed out!")
                        raise TimeoutError("Tool call timed out after 12 seconds")
                    
                    # Simplified result handling with more debug info
                    print("Processing result...")
                    try:
                        if hasattr(result, 'content') and result.content:
                            print(f"Result has content field with {len(result.content)} items")
                            text_value = result.content[0].text
                            print(f"Got text of length: {len(text_value)}")
                            return text_value
                        elif isinstance(result, (list, tuple)) and result:
                            print(f"Result is list/tuple with {len(result)} items")
                            if hasattr(result[0], 'text'):
                                text_value = result[0].text
                                print(f"Got text of length: {len(text_value)}")
                                return text_value
                            else:
                                print(f"Result item has no 'text' attribute: {type(result[0])}")
                                return str(result[0])
                        else:
                            print(f"Unexpected result format: {type(result)}")
                            return str(result)
                    except Exception as e:
                        print(f"Error extracting text from result: {str(e)}")
                        return f"Error: {str(e)}"
                        
            except Exception as e:
                print(f"Error in ClientSession: {str(e)}")
                traceback.print_exc()
                raise
    except Exception as e:
        print(f"Error in stdio_client: {str(e)}")
        traceback.print_exc()
        raise
    finally:
        # Force cleanup of resources
        print("Cleaning up resources...")
        if 'session' in locals() and session is not None:
            await session.close()
        if 'read' in locals() and 'write' in locals():
            await read.aclose()
            await write.aclose()
        print("Cleanup complete!")

async def get_claude_insights(result_text):
    claude_client = get_claude_client()
    try:
        print("Parsing analysis results...")
        analysis_results = json.loads(result_text)
        
        # Check if there was an error
        if isinstance(analysis_results, dict) and analysis_results.get("isError", False):
            return f"Error during analysis: {analysis_results.get('message', 'Unknown error')}"
        
        print("Building prompt for Claude...")
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
        
        print("\nGetting insights from Claude (streaming response)...")
        try:
            # Create streaming response with explicit timeout
            stream = await asyncio.wait_for(
                claude_client.messages.create(
                    max_tokens=1024,
                    model="claude-3.5-sonnet-20241022",
                    messages=[{"role": "user", "content": prompt}],
                    stream=True
                ),
                timeout=15  # 15 second timeout for initial connection
            )
            
            # Collect the full response
            full_response = ""
            
            # Print each chunk as it arrives - use async iteration with timeout
            print("Starting stream processing...")
            async for chunk in stream:
                print(f"Received chunk type: {chunk.type}", end="\r")
                if chunk.type == "content_block_delta":
                    text = chunk.delta.text
                    print(text, end="", flush=True)
                    full_response += text
            
            print("\nStreaming complete!")
            return full_response
                
        except asyncio.TimeoutError:
            print("\nTimeout while waiting for Claude's response")
            return "Analysis timed out while waiting for Claude's response"
            
    except json.JSONDecodeError as e:
        print(f"\nError parsing JSON result: {str(e)}")
        # Fallback to non-JSON handling
        prompt = f"Here are the analysis results of my CSV file. Please interpret these results and provide insights:\n\n{result_text}"
        
        try:
            # Non-streaming fallback
            message = await asyncio.wait_for(
                claude_client.messages.create(
                    model="claude-3.5-sonnet-20241022",
                    max_tokens=1024,
                    messages=[{"role": "user", "content": prompt}]
                ),
                timeout=30
            )
            return message.content
        except Exception as e:
            return f"Error getting insights (fallback): {str(e)}"
    except Exception as e:
        print(f"\nError in streaming response: {str(e)}")
        traceback.print_exc()
        return f"Error getting insights: {str(e)}"

async def amain():
    try:
        # Add overall timeout for the entire process
        result_text = await asyncio.wait_for(
            analyze_csv_with_mcp(),
            timeout=30  # 30 second timeout for the entire CSV analysis
        )
        
        print("\nRaw Analysis Results:")
        print(result_text)
        
        print("\nStreaming Claude's analysis...")
        try:
            insights = await asyncio.wait_for(
                get_claude_insights(result_text),
                timeout=45  # 45 second timeout for Claude's analysis
            )
            print("\nAnalysis complete!")
        except asyncio.TimeoutError:
            print("\nTimed out waiting for Claude's analysis!")
            insights = "Analysis timed out. Please try again later."
        
    except asyncio.TimeoutError:
        print("\nTimed out during CSV analysis!")
    except Exception as e:
        print(f"\nError during analysis: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    import anyio
    try:
        anyio.run(amain)  # Remove the clock_rate parameter
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    print("\nProgram completed")

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