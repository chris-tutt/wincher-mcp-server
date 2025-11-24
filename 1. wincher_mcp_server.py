import os
import asyncio
import httpx
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

# Initialize the MCP server
app = Server("wincher-mcp")

# Wincher API configuration
WINCHER_API_KEY = os.getenv("WINCHER_API_KEY")
BASE_URL = "https://api.wincher.com"

async def make_wincher_request(endpoint: str, params: dict = None):
    """Make an authenticated request to Wincher API"""
    if not WINCHER_API_KEY:
        raise ValueError("WINCHER_API_KEY environment variable not set")
    
    headers = {
        "Authorization": f"Bearer {WINCHER_API_KEY}",
        "Accept": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}{endpoint}",
            headers=headers,
            params=params,
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available Wincher API tools"""
    return [
        Tool(
            name="get_websites",
            description="List all websites tracked in your Wincher account with keyword counts and competitor information",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_keywords",
            description="Get all keywords for a specific website with their current rankings, search volume, CPC, competition, and difficulty data",
            inputSchema={
                "type": "object",
                "properties": {
                    "website_id": {
                        "type": "integer",
                        "description": "The ID of the website (get from get_websites)"
                    }
                },
                "required": ["website_id"]
            }
        ),
        Tool(
            name="get_keyword_rankings",
            description="Get detailed ranking history for a specific keyword over time",
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword_id": {
                        "type": "integer",
                        "description": "The ID of the keyword (get from get_keywords)"
                    },
                    "website_id": {
                        "type": "integer",
                        "description": "The ID of the website"
                    }
                },
                "required": ["keyword_id", "website_id"]
            }
        ),
        Tool(
            name="get_competitor_ranking_summaries",
            description="Get ranking summary comparison between your website and all tracked competitors including traffic, share of voice, and position distribution",
            inputSchema={
                "type": "object",
                "properties": {
                    "website_id": {
                        "type": "integer",
                        "description": "The ID of the website"
                    }
                },
                "required": ["website_id"]
            }
        ),
        Tool(
            name="get_competitor_keyword_positions",
            description="Get detailed keyword-by-keyword position comparison between your website and competitors",
            inputSchema={
                "type": "object",
                "properties": {
                    "website_id": {
                        "type": "integer",
                        "description": "The ID of the website"
                    }
                },
                "required": ["website_id"]
            }
        ),
        Tool(
            name="get_serps",
            description="Get SERP (Search Engine Results Page) data for a keyword showing who ranks in top positions and what SERP features are present",
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword_id": {
                        "type": "integer",
                        "description": "The ID of the keyword"
                    },
                    "website_id": {
                        "type": "integer",
                        "description": "The ID of the website"
                    }
                },
                "required": ["keyword_id", "website_id"]
            }
        ),
        Tool(
            name="get_keyword_groups",
            description="List all keyword groups for a website with their aggregate performance metrics",
            inputSchema={
                "type": "object",
                "properties": {
                    "website_id": {
                        "type": "integer",
                        "description": "The ID of the website"
                    }
                },
                "required": ["website_id"]
            }
        ),
        Tool(
            name="get_bulk_ranking_history",
            description="Get historical ranking data for multiple keywords at once (more efficient than getting them one by one)",
            inputSchema={
                "type": "object",
                "properties": {
                    "website_id": {
                        "type": "integer",
                        "description": "The ID of the website"
                    },
                    "keyword_ids": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "Array of keyword IDs to get history for"
                    },
                    "start_at": {
                        "type": "string",
                        "description": "Start date in ISO-8601 format (e.g., 2024-01-01T00:00:00Z)"
                    },
                    "end_at": {
                        "type": "string",
                        "description": "End date in ISO-8601 format (e.g., 2024-12-31T23:59:59Z)"
                    }
                },
                "required": ["website_id", "keyword_ids", "start_at", "end_at"]
            }
        ),
        Tool(
            name="get_annotations",
            description="Get annotations (notes about SEO activities, ranking changes, etc.) for a website",
            inputSchema={
                "type": "object",
                "properties": {
                    "website_id": {
                        "type": "integer",
                        "description": "The ID of the website"
                    }
                },
                "required": ["website_id"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls to Wincher API"""
    
    try:
        if name == "get_websites":
            data = await make_wincher_request("/v1/websites")
            result = "Tracked Websites:\n\n"
            
            for site in data.get("data", []):
                result += f"ID: {site.get('id', 'N/A')}\n"
                result += f"Domain: {site.get('domain', 'N/A')}\n"
                
                # Search engine is an object
                search_engine = site.get('search_engine', {})
                result += f"Search Engine: {search_engine.get('domain', 'N/A')}\n"
                
                # Location is an object
                location = site.get('location', {})
                result += f"Location: {location.get('name', 'N/A')} ({location.get('code', 'N/A')})\n"
                
                result += f"Language: {site.get('language', 'N/A')}\n"
                result += f"Keywords: {site.get('keyword_count', 0)}\n"
                result += f"Competitors: {site.get('competitor_count', 0)}\n"
                result += f"Mobile: {site.get('is_mobile', False)}\n"
                
                # Show competitor domains
                competitors = site.get('competitors', [])
                if competitors:
                    comp_domains = [c.get('domain', '') for c in competitors]
                    result += f"Tracking: {', '.join(comp_domains)}\n"
                
                result += "\n"
            
            return [TextContent(type="text", text=result)]
        
        elif name == "get_keywords":
            website_id = arguments["website_id"]
            data = await make_wincher_request(f"/v1/websites/{website_id}/keywords")
            
            result = f"Keywords for Website ID {website_id}:\n\n"
            for kw in data.get("data", []):
                result += f"ID: {kw.get('id', 'N/A')}\n"
                result += f"Keyword: {kw.get('keyword', 'N/A')}\n"
                result += f"Current Rank: {kw.get('position', 'N/A')}\n"
                result += f"Previous Rank: {kw.get('previous_position', 'N/A')}\n"
                result += f"Best Rank: {kw.get('best_position', 'N/A')}\n"
                result += f"Search Volume: {kw.get('search_volume', 'N/A')}\n"
                result += f"URL: {kw.get('url', 'N/A')}\n"
                result += f"Last Updated: {kw.get('updated_at', 'N/A')}\n\n"
            
            return [TextContent(type="text", text=result)]
        
        elif name == "get_keyword_rankings":
            keyword_id = arguments["keyword_id"]
            website_id = arguments["website_id"]
            data = await make_wincher_request(f"/v1/websites/{website_id}/keyword/{keyword_id}/ranking-history")
            
            result = f"Ranking History for Keyword ID {keyword_id}:\n\n"
            for series in data.get("data", []):
                if series.get("label"):
                    result += f"Series: {series['label']}\n"
                for point in series.get("data", []):
                    result += f"Date: {point.get('date', 'N/A')}\n"
                    result += f"Position: {point.get('position', 'N/A')}\n"
                    if point.get('url'):
                        result += f"URL: {point['url']}\n"
                    result += "\n"
            
            return [TextContent(type="text", text=result)]
        
        elif name == "get_competitor_ranking_summaries":
            website_id = arguments["website_id"]
            data = await make_wincher_request(f"/v1/websites/{website_id}/competitors/ranking-summaries")
            
            result = f"Competitor Ranking Comparison:\n\n"
            for summary in data.get("data", []):
                result += f"Domain: {summary.get('domain', 'N/A')}\n"
                result += f"Is Your Website: {summary.get('is_tracked_website', False)}\n"
                
                ranking = summary.get('ranking', {})
                avg_pos = ranking.get('avg_position', {})
                result += f"Average Position: {avg_pos.get('value', 'N/A')}\n"
                result += f"Position Change: {avg_pos.get('change', 'N/A')}\n"
                
                traffic = ranking.get('traffic', {})
                result += f"Estimated Traffic: {traffic.get('value', 'N/A')}\n"
                
                sov = ranking.get('share_of_voice', {})
                result += f"Share of Voice: {sov.get('value', 'N/A')}%\n"
                
                volume = ranking.get('volume', {})
                result += f"Total Search Volume: {volume.get('value', 'N/A')}\n"
                
                result += "\n"
            
            return [TextContent(type="text", text=result)]
        
        elif name == "get_competitor_keyword_positions":
            website_id = arguments["website_id"]
            data = await make_wincher_request(f"/v1/websites/{website_id}/competitors/keyword-positions")
            
            result = f"Keyword Position Comparison:\n\n"
            for item in data.get("data", []):
                result += f"Keyword: {item.get('keyword', 'N/A')}\n"
                result += f"Search Volume: {item.get('volume', 'N/A')}\n"
                
                positions = item.get('positions', [])
                for pos in positions:
                    result += f"  • {pos.get('domain', 'N/A')}: Position {pos.get('position', 'N/A')}"
                    if pos.get('is_tracked_website'):
                        result += " (YOUR SITE)"
                    result += "\n"
                result += "\n"
            
            return [TextContent(type="text", text=result)]
        
        elif name == "get_serps":
            keyword_id = arguments["keyword_id"]
            website_id = arguments["website_id"]
            data = await make_wincher_request(f"/v1/websites/{website_id}/keywords/{keyword_id}/serps")
            
            result = f"SERP Data for Keyword ID {keyword_id}:\n\n"
            for serp in data.get("data", []):
                result += f"Date: {serp.get('date', 'N/A')}\n"
                result += f"Search Volume: {serp.get('volume', {}).get('value', 'N/A')}\n"
                
                # SERP features
                features = serp.get('features', [])
                if features:
                    result += f"SERP Features: {', '.join(features)}\n"
                
                # Top ranking results
                results = serp.get('results', [])
                result += "\nTop Rankings:\n"
                for i, res in enumerate(results[:10], 1):
                    result += f"{i}. {res.get('domain', 'N/A')}\n"
                    result += f"   Title: {res.get('title', 'N/A')[:80]}...\n"
                    if res.get('url'):
                        result += f"   URL: {res['url']}\n"
                result += "\n"
            
            return [TextContent(type="text", text=result)]
        
        elif name == "get_keyword_groups":
            website_id = arguments["website_id"]
            data = await make_wincher_request(f"/v1/websites/{website_id}/groups")
            
            result = f"Keyword Groups:\n\n"
            for group in data.get("data", []):
                result += f"Group: {group.get('name', 'N/A')}\n"
                result += f"Keywords: {len(group.get('keyword_ids', []))}\n"
                
                ranking = group.get('ranking', {})
                avg_pos = ranking.get('avg_position', {})
                result += f"Average Position: {avg_pos.get('value', 'N/A')}\n"
                
                traffic = ranking.get('traffic', {})
                result += f"Estimated Traffic: {traffic.get('value', 'N/A')}\n"
                
                volume = ranking.get('volume', {})
                result += f"Total Search Volume: {volume.get('value', 'N/A')}\n"
                
                result += f"Average Difficulty: {group.get('avg_keyword_difficulty', 'N/A')}\n"
                result += "\n"
            
            return [TextContent(type="text", text=result)]
        
        elif name == "get_bulk_ranking_history":
            website_id = arguments["website_id"]
            keyword_ids = arguments["keyword_ids"]
            start_at = arguments["start_at"]
            end_at = arguments["end_at"]
            
            payload = {
                "keyword_ids": keyword_ids,
                "start_at": start_at,
                "end_at": end_at
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{BASE_URL}/v1/websites/{website_id}/ranking-history",
                    headers={
                        "Authorization": f"Bearer {WINCHER_API_KEY}",
                        "Accept": "application/json",
                        "Content-Type": "application/json"
                    },
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
            
            result = f"Bulk Ranking History ({start_at} to {end_at}):\n\n"
            for item in data.get("data", []):
                result += f"Keyword ID: {item.get('keyword_id', 'N/A')}\n"
                result += f"Keyword: {item.get('keyword', 'N/A')}\n"
                
                for point in item.get('data', []):
                    result += f"  {point.get('date', 'N/A')}: Position {point.get('position', 'N/A')}\n"
                result += "\n"
            
            return [TextContent(type="text", text=result)]
        
        elif name == "get_annotations":
            website_id = arguments["website_id"]
            data = await make_wincher_request(f"/v1/websites/{website_id}/annotations")
            
            result = f"Annotations:\n\n"
            for annotation in data.get("data", []):
                result += f"Date: {annotation.get('date', 'N/A')}\n"
                result += f"Type: {annotation.get('type', 'N/A')}\n"
                result += f"Description: {annotation.get('description', 'N/A')}\n"
                
                author = annotation.get('author', {})
                if author.get('profile'):
                    name = f"{author['profile'].get('first_name', '')} {author['profile'].get('last_name', '')}"
                    result += f"Author: {name.strip()}\n"
                
                result += "\n"
            
            return [TextContent(type="text", text=result)]
        
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    
    except httpx.HTTPStatusError as e:
        error_details = f"API Error: {e.response.status_code}\n"
        error_details += f"URL: {e.request.url}\n"
        error_details += f"Response: {e.response.text}\n"
        return [TextContent(type="text", text=error_details)]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}\nType: {type(e).__name__}")]

async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
