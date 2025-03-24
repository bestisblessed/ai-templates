import pandas as pd
from ydata_profiling import ProfileReport
import json
import os
import mcp.types as types
from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server
import traceback
import sys
import signal
from functools import partial

# Create server
app = Server("ds-analysis-server")

# Add timeout handling
class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("Operation timed out")

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    print("Tool list requested")
    tools = [
        types.Tool(
            name="analyze_csv",
            description="Analyze a CSV file with pandas-profiling",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {"type": "string"},
                    "minimal": {"type": "boolean", "default": True},
                    "timeout": {"type": "number", "default": 60},
                    "columns": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["filepath"]
            }
        )
    ]
    print(f"Returning tools: {tools}")
    return tools

@app.call_tool()
async def analyze_csv_handler(name: str, arguments: dict) -> list[types.TextContent]:
    print(f"Tool call received: {name} with arguments: {arguments}")
    if name != "analyze_csv":
        print(f"Unknown tool: {name}")
        raise ValueError(f"Unknown tool: {name}")
    
    try:
        filepath = arguments["filepath"]
        minimal = arguments.get("minimal", True)  # Default to minimal now
        timeout_seconds = arguments.get("timeout", 60)
        columns = arguments.get("columns", None)
        
        print(f"Starting analysis of {filepath}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Python version: {sys.version}")
        print(f"Pandas version: {pd.__version__}")
        
        # Check if file exists
        if not os.path.exists(filepath):
            error_msg = f"File not found: {filepath}"
            print(error_msg)
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "isError": True,
                    "message": error_msg
                })
            )]
        
        # Read CSV
        try:
            df = pd.read_csv(filepath)
            print(f"CSV loaded successfully with shape: {df.shape}")
        except Exception as e:
            error_msg = f"Error reading CSV file: {str(e)}"
            print(error_msg)
            traceback.print_exc()
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "isError": True,
                    "message": error_msg
                })
            )]
        
        # Print column names for debugging
        print(f"Columns in the CSV: {list(df.columns)}")
        
        # Filter columns if specified
        if columns:
            # Check if specified columns exist
            missing_cols = [col for col in columns if col not in df.columns]
            if missing_cols:
                print(f"Columns not found: {missing_cols}")
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "isError": True,
                        "message": f"Error: Columns not found in CSV: {missing_cols}"
                    })
                )]
            df = df[columns]
        
        # First create basic statistics without profile report
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        date_cols = df.select_dtypes(include=['datetime']).columns.tolist()
        
        # Extract key statistics
        stats = {
            "rows": len(df),
            "columns": len(df.columns),
            "missing_cells": int(df.isna().sum().sum()),
            "missing_cells_ratio": float(df.isna().sum().sum() / (len(df) * len(df.columns) if len(df) * len(df.columns) > 0 else 1)),
            "duplicates": int(df.duplicated().sum()),
            "column_types": {
                "numeric": numeric_cols,
                "categorical": categorical_cols,
                "date": date_cols
            },
            "column_stats": {},
        }
        
        # Add basic statistics for each column
        for col in df.columns:
            if col in numeric_cols:
                try:
                    stats["column_stats"][col] = {
                        "min": float(df[col].min()) if not pd.isna(df[col].min()) else None,
                        "max": float(df[col].max()) if not pd.isna(df[col].max()) else None,
                        "mean": float(df[col].mean()) if not pd.isna(df[col].mean()) else None,
                        "median": float(df[col].median()) if not pd.isna(df[col].median()) else None,
                        "missing": int(df[col].isna().sum())
                    }
                except Exception as e:
                    print(f"Error calculating stats for column {col}: {str(e)}")
                    stats["column_stats"][col] = {"error": str(e)}
            elif col in categorical_cols:
                try:
                    value_counts = df[col].value_counts().head(5).to_dict()
                    # Convert keys to strings for JSON serialization
                    value_counts = {str(k): int(v) for k, v in value_counts.items()}
                    stats["column_stats"][col] = {
                        "unique_values": int(df[col].nunique()),
                        "top_values": value_counts,
                        "missing": int(df[col].isna().sum())
                    }
                except Exception as e:
                    print(f"Error calculating stats for column {col}: {str(e)}")
                    stats["column_stats"][col] = {"error": str(e)}
        
        # Now try to generate profile report with timeout
        try:
            print(f"Generating profile report with timeout: {timeout_seconds} seconds...")
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout_seconds)
            
            # Create reports directory if it doesn't exist
            os.makedirs("reports", exist_ok=True)
            
            # Generate profile with minimal settings
            profile = ProfileReport(df, minimal=True, title="CSV Analysis")
            
            # Save report
            report_filename = os.path.basename(filepath).split('.')[0] + "_report.html"
            report_path = os.path.join("reports", report_filename)
            profile.to_file(report_path)
            print(f"Report saved to {report_path}")
            
            # Add report path to stats
            stats["report_path"] = report_path
            
            # Turn off alarm
            signal.alarm(0)
            
        except TimeoutError:
            print(f"Profile report generation timed out after {timeout_seconds} seconds")
            stats["profile_error"] = f"Profile report generation timed out after {timeout_seconds} seconds"
        except Exception as e:
            print(f"Error generating profile report: {str(e)}")
            traceback.print_exc()
            stats["profile_error"] = str(e)
        
        print("Analysis completed successfully")
        result = [types.TextContent(
            type="text",
            text=json.dumps(stats, indent=2)
        )]
        print(f"Returning result type: {type(result)}")
        return result
    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        traceback.print_exc()
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "isError": True,
                "message": f"Error analyzing CSV: {str(e)}"
            })
        )]

# Anyio run pattern
async def arun():
    print("Starting MCP Data Science Server...")
    try:
        async with stdio_server() as (read_stream, write_stream):
            await app.run(read_stream, write_stream, app.create_initialization_options())
    except Exception as e:
        print(f"Server error: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    import anyio
    anyio.run(arun)

