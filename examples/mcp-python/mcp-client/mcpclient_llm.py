from mcp import ClientSession
from mcp.client.sse import sse_client
# Import Google Gemini SDK or API client
from google import genai
from google.genai import types
import os

# Initialize Gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
model = "gemini-2.0-flash"


async def call_mcp_server(prompt: str, client: genai.Client, session: ClientSession):
    """
    Handles the interaction between Gemini and the MCP server.
    """
    contents = [types.Content(role="user", parts=[types.Part(text=prompt)])]
    
    # Initialize MCP session
    await session.initialize()
    
    # List available tools from the MCP server
    mcp_tools = await session.list_tools()
    
    # Create tool declarations for Gemini from MCP tools
    # Gemini requires tools to be in a specific format
    tools = [
        types.Tool(
            function_declarations=[
                {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": {
                        k: v
                        for k, v in tool.inputSchema.items()
                        if k not in ["additionalProperties", "$schema"]
                    },
                }
            ]
        )
        for tool in mcp_tools.tools
    ]    
    # Call Gemini with the prompt and available tools
    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=types.GenerateContentConfig(
            temperature=0.5,
            tools=tools,
        ),
    )
        
    # Check for function calls in the response
    function_calls = response.candidates[0].content.parts[0].function_call
    if not function_calls:
        print("No function call detected.")
        result ="No function call detected."
        return
    
    # Execute the function call on the MCP server
    tool_name = function_calls.name
    tool_args = function_calls.args
    print(f"Calling tool: {tool_name} with args: {tool_args}")
    
    # Call the MCP tool
    result = await session.call_tool(
        name=tool_name,
        arguments=tool_args,
    )
    result = result.content[0].text    
    return result

async def main():
    """
    Main function to run the Gemini-MCP integration.
    """
    async with sse_client(url="http://localhost:8000/sse") as streams:
        async with ClientSession(*streams) as session:
            # Example prompt
            prompt = "what is the temprature in Bengaluru?"
            print(f"Running with prompt: {prompt}")
            
            # Run the agent loop
            response = await call_mcp_server(prompt, client, session)
            
            # Print the final response
            print(response)
            

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
