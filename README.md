# Wincher MCP Server for Claude Desktop

> Natural language SEO analysis - Query your Wincher data through Claude Desktop

## What This Does

This MCP (Model Context Protocol) server connects Claude Desktop to Wincher's SEO API, enabling you to analyze keyword rankings, competitors, and SERP data using natural conversation instead of navigating dashboards.

**Ask Claude things like:**
- "Compare our rankings vs Splunk for all keywords"
- "Show me SERP features for 'SIEM software'"
- "Which keywords are declining this month?"
- "What's our share of voice compared to competitors?"

## Features

✅ **Competitor Analysis** - Compare rankings, traffic, and share of voice  
✅ **Keyword Performance** - Track positions, volume, CPC, and difficulty  
✅ **SERP Intelligence** - See who ranks where and what features appear  
✅ **Historical Trends** - Analyze ranking changes over time  
✅ **Bulk Operations** - Query multiple keywords efficiently  
✅ **Keyword Groups** - Aggregate performance by topic/category  

## Prerequisites

- Python 3.10+
- Claude Desktop app
- Wincher account with API access

## Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/wincher-mcp-server.git
cd wincher-mcp-server
```

### 2. Create virtual environment
```bash
python3 -m venv wincher-mcp-env
source wincher-mcp-env/bin/activate  # On Windows: wincher-mcp-env\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Get your Wincher API key
1. Log into Wincher
2. Navigate to Settings → Personal Access Tokens
3. Generate a new token
4. Copy the token

### 5. Configure Claude Desktop

Edit your Claude Desktop config file:
- **Mac:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

Add this configuration:
```json
{
  "mcpServers": {
    "wincher": {
      "command": "/full/path/to/wincher-mcp-env/bin/python",
      "args": ["/full/path/to/wincher_mcp_server.py"],
      "env": {
        "WINCHER_API_KEY": "your_wincher_api_key_here"
      }
    }
  }
}
```

Replace:
- `/full/path/to/` with your actual paths
- `your_wincher_api_key_here` with your API key

### 6. Restart Claude Desktop

Quit and reopen Claude Desktop completely.

## Usage Examples

See [EXAMPLES.md](docs/EXAMPLES.md) for 50+ example prompts.

**Quick examples:**
```
"Show me all my tracked websites in Wincher"
"List keywords where we rank in the top 10"
"Compare our SEO performance vs [competitor]"
"Show me the SERP for 'your target keyword'"
"Which keyword group has the best average position?"
```

## Available Tools

The MCP server provides these tools to Claude:

- `get_websites` - List tracked websites
- `get_keywords` - Get keywords and rankings for a website
- `get_keyword_rankings` - Historical ranking data
- `get_competitor_ranking_summaries` - Compare vs competitors
- `get_competitor_keyword_positions` - Keyword-by-keyword comparison
- `get_serps` - SERP analysis with features
- `get_keyword_groups` - Group performance metrics
- `get_bulk_ranking_history` - Bulk historical data
- `get_annotations` - SEO activity notes

## Troubleshooting

**Server not connecting?**
- Verify paths in `claude_desktop_config.json` are absolute paths
- Check that virtual environment is in the correct location
- Ensure API key is valid

**No data returning?**
- Verify you have websites and keywords tracked in Wincher
- Check API key has proper permissions
- Try testing the API key with a curl command

**Need help?**
- Open an issue on GitHub
- Check the [detailed setup guide](docs/SETUP.md)

## Why I Built This

As a marketing professional at Graylog (a cybersecurity SIEM company), I was spending hours each week manually pulling SEO data, comparing competitor rankings, and building reports. This integration saves ~4 hours per week by enabling instant analysis through natural conversation.

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Security Note

⚠️ Never commit your API key to version control. Always use environment variables or the configuration method shown above.

## License

MIT License - see [LICENSE](LICENSE) file for details

## Acknowledgments

- Built with [Anthropic's MCP SDK](https://github.com/anthropic-ai/mcp)
- Uses [Wincher's API](https://www.wincher.com/docs/api)

## Connect

Built by Chris Tutt | [LinkedIn](your-linkedin-url)

If this helped your SEO workflow, give it a ⭐!
```

## `.env.example` Content:
```
# Wincher API Configuration
# Get your API key from: https://www.wincher.com (Settings → Personal Access Tokens)
WINCHER_API_KEY=your_api_key_here
