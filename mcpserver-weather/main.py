from mcp.server.fastmcp import FastMCP
import requests

mcp = FastMCP()

@mcp.tool(name="add", description="Add two numbers.")
def add(a: int, b: int) -> int:
    """
    Add two numbers.
    """
    print(f"Adding {a} and {b}")
    return a + b    

@mcp.tool(name="getweather", description="Fetch weather information for a given city.")
def getweather(city: str) -> str:
    """
    Fetch weather information for a given city.

    Args:
        city (str): The name of the city.

    Returns:
        str: JSON response containing weather details.
    """
    url = f"http://localhost:3000/api/weather/city/{city}"
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for HTTP request issues
    return response.json()

if __name__ == "__main__":
    mcp.run(transport="sse")
