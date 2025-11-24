from dotenv import load_dotenv
import os
import sys
import subprocess
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

def read_file(filename: str) -> str:
    """Reads the content of a file in the hell_fire directory."""
    filepath = os.path.join("hell_fire", filename)
    try:
        with open(filepath, "r") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

def write_file(filename: str, content: str) -> str:
    """Writes content to a file in the hell_fire directory. Creates it if it doesn't exist."""
    filepath = os.path.join("hell_fire", filename)
    try:
        with open(filepath, "w") as f:
            f.write(content)
        return f"Successfully wrote to {filename}"
    except Exception as e:
        return f"Error writing file: {e}"

def delete_file(filename: str) -> str:
    """Deletes a file in the hell_fire directory."""
    filepath = os.path.join("hell_fire", filename)
    try:
        os.remove(filepath)
        return f"Successfully deleted {filename}"
    except Exception as e:
        return f"Error deleting file: {e}"

def list_files() -> str:
    """Lists all files in the hell_fire directory."""
    try:
        files = os.listdir("hell_fire")
        return str(files)
    except Exception as e:
        return f"Error listing files: {e}"

def run_terminal_command(command: str, input_text: str = None) -> str:
    """Runs a terminal command and returns the output.
    
    Args:
        command: The command to run.
        input_text: Optional text to send to the command's stdin (e.g., for interactive scripts).
    """
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, input=input_text, timeout=60)
        output = f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        return output
    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 60 seconds."
    except Exception as e:
        return f"Error running command: {e}"

def main():
    load_dotenv()
    
    # Check for Azure OpenAI environment variables
    # Support both AZURE_OPENAI_API_VERSION and OPENAI_API_VERSION
    api_version = os.environ.get("AZURE_OPENAI_API_VERSION") or os.environ.get("OPENAI_API_VERSION")
    
    required_vars = ["AZURE_OPENAI_API_KEY", "AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_DEPLOYMENT_NAME"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if not api_version:
        missing_vars.append("AZURE_OPENAI_API_VERSION (or OPENAI_API_VERSION)")
    
    if missing_vars:
        print(f"Error: Missing environment variables: {', '.join(missing_vars)}")
        print("Please set them in your .env file.")
        return

    print("Args: "+str(sys.argv))
    
    if(len(sys.argv) < 2):
        print("Please provide a query")
        return

    query = sys.argv[1]

    # Initialize Azure OpenAI Chat Model
    llm = AzureChatOpenAI(
        azure_deployment=os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME"),
        api_version=api_version,
    )

    tools = [read_file, write_file, delete_file, list_files, run_terminal_command]
    llm_with_tools = llm.bind_tools(tools)

    # Create the hell_fire directory if it doesn't exist
    if not os.path.exists("hell_fire"):
        os.makedirs("hell_fire")

    system_prompt = """You are an autonomous agent capable of file operations and terminal execution.
    
    Your goal is to complete the user's request by following this rigorous process:
    1. **Plan**: Analyze the request and list the step-by-step actions you will take.
    2. **Execute**: Use your tools to perform the planned actions.
    3. **Verify**: After execution, ALWAYS verify the result. For example, if you create a file, read it back or run it to ensure it works.
    4. **Fix**: If verification fails, analyze the error, adjust your plan, and try again.
    
    Do not ask the user for confirmation unless you are stuck. Proceed through the steps autonomously.
    """

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=query)
    ]

    print("\n--- Agent Started ---\n")

    while True:
        response = llm_with_tools.invoke(messages)
        messages.append(response)

        if response.tool_calls:
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                tool_call_id = tool_call["id"]
                
                print(f"\n[Tool Call] {tool_name}({tool_args})")
                
                tool_result = None
                if tool_name == "read_file":
                    tool_result = read_file(**tool_args)
                elif tool_name == "write_file":
                    tool_result = write_file(**tool_args)
                elif tool_name == "delete_file":
                    tool_result = delete_file(**tool_args)
                elif tool_name == "list_files":
                    tool_result = list_files()
                elif tool_name == "run_terminal_command":
                    tool_result = run_terminal_command(**tool_args)
                
                print(f"[Tool Result] {str(tool_result)[:200]}...") # Truncate log output
                
                messages.append(ToolMessage(tool_call_id=tool_call_id, content=str(tool_result)))
        else:
            print("\n[Final Answer]")
            print(response.content)
            break

if __name__ == "__main__":
    main()