# HealthPulse Agent

A proof-of-concept **M365 Agents Toolkit declarative agent** that connects to a remote MCP server (exposed via Azure DevTunnels) to retrieve fictional healthcare data from "Contoso Health Services" and render it as charts using **Code Interpreter**.

This demonstrates the end-to-end pattern of:
1. Building a custom MCP server with domain-specific tools
2. Exposing it publicly via DevTunnels
3. Connecting a Microsoft 365 Copilot declarative agent to it
4. Using Code Interpreter to visualise the returned data as charts

---

## Architecture

```
┌─────────────────────────────┐                      ┌────────────────────────────┐
│  Microsoft 365 Copilot      │   DevTunnels (HTTPS) │  HealthPulse MCP Server    │
│  ┌───────────────────────┐  │ ◄──────────────────► │  (Python / FastMCP)        │
│  │ Declarative Agent     │  │                      │  Port 3001                 │
│  │ + Code Interpreter    │  │                      │                            │
│  └───────────────────────┘  │                      │  Tools:                    │
│         │                   │                      │  • get_ambulance_wait_times │
│         ▼                   │                      │  • get_ae_waiting_times     │
│   Generates matplotlib      │                      │  • get_bed_occupancy        │
│   charts from data          │                      │  • get_regional_health_     │
│                             │                      │    summary                 │
└─────────────────────────────┘                      └────────────────────────────┘
```

---

## Prerequisites

- **Python 3.10+** (for the MCP server)
- **Azure DevTunnels CLI** (`devtunnel`) — [Install guide](https://learn.microsoft.com/en-us/azure/developer/dev-tunnels/get-started)
- **VS Code** with the [M365 Agents Toolkit extension](https://marketplace.visualstudio.com/items?itemName=TeamsDevApp.ms-teams-vscode-extension)
- **Microsoft 365 developer tenant** with Copilot license

---

## Project Structure

```
healthpulse-agent/
├── mcp-server/
│   ├── server.py              # MCP server (FastMCP, stateless HTTP)
│   └── requirements.txt       # Python dependencies
├── appPackage/
│   ├── manifest.json          # Teams/M365 app manifest (v1.24)
│   ├── declarativeAgent.json  # Agent definition (v1.5) with Code Interpreter
│   ├── ai-plugin.json         # Plugin manifest with RemoteMCPServer runtime
│   ├── instruction.txt        # Agent system instructions
│   ├── color.png              # App icon (192x192)
│   └── outline.png            # Outline icon (32x32, transparent)
├── env/
│   └── .env.dev               # Environment variables for provisioning
├── m365agents.yml             # M365 Agents Toolkit project file
├── .env                       # Local config (MCP server URL)
├── USER_JOURNEYS.md           # Demo scripts with suggested prompts
└── README.md
```

---

## Part 1: MCP Server

### How It Works

The MCP server is built with [FastMCP](https://github.com/modelcontextprotocol/python-sdk) (Python) and exposes 4 tools that return fictional healthcare performance data:

| Tool | Description |
|------|-------------|
| `get_ambulance_wait_times` | Response times by category (1-4) per region |
| `get_ae_waiting_times` | A&E 4-hour target performance and patient volumes |
| `get_bed_occupancy` | Bed occupancy rates by trust and bed type |
| `get_regional_health_summary` | Comprehensive regional summary with 8-week trends |

Key configuration:
- **`stateless_http=True`** — no session state needed between requests
- **`json_response=True`** — returns JSON instead of SSE streams
- **`EnsureHeadersMiddleware`** — injects `Content-Type` and `Accept` headers that some MCP clients omit

### Running the MCP Server

```bash
cd mcp-server
pip install -r requirements.txt
python server.py
```

The server starts on `http://localhost:3001`.

### Exposing via DevTunnels

```bash
devtunnel host -p 3001 --allow-anonymous
```

This gives you a public URL like `https://abc123-3001.uks1.devtunnels.ms`. Your MCP endpoint will be at that URL + `/mcp`.

Copy the full MCP URL and update:
1. **`.env`** — set `MCP_SERVER_URL=https://abc123-3001.uks1.devtunnels.ms/mcp`
2. The toolkit will substitute `${{MCP_SERVER_URL}}` in `ai-plugin.json` during build.

---

## Part 2: Declarative Agent

### How It Works

The declarative agent is defined in `appPackage/` and uses two capabilities:

1. **Code Interpreter** — generates Python charts (matplotlib) from data
2. **RemoteMCPServer action** — connects to the HealthPulse MCP server via the `ai-plugin.json` runtime definition

The `ai-plugin.json` declares all 4 MCP tools as functions and points the runtime at your DevTunnels URL:

```json
"runtimes": [{
    "type": "RemoteMCPServer",
    "spec": {
        "url": "${{MCP_SERVER_URL}}",
        "enable_dynamic_discovery": false
    },
    "run_for_functions": ["get_ambulance_wait_times", ...]
}]
```

### Deploying the Agent

1. **Open this folder in VS Code** with the M365 Agents Toolkit extension installed.

2. **Set your MCP server URL** in `.env`:
   ```
   MCP_SERVER_URL=https://your-tunnel-id.devtunnels.ms/mcp
   ```

3. **Provision** — press `F5` or use the Agents Toolkit sidebar → "Provision":
   - Creates the Teams app in Developer Portal
   - Builds and validates the app package
   - Extends to M365 Copilot

4. **Sideload** — the toolkit will sideload the agent to your tenant.

5. **Open Microsoft 365 Copilot** (https://m365.cloud.microsoft/chat) and select the **HealthPulse** agent from the agent picker.

### Testing

Try these prompts:
- "What are the current ambulance wait times across all regions?"
- "Show me a bar chart of Category 1 ambulance response times with the 7-minute target line"
- "Give me the regional health summary for London and create a dashboard chart"

See `USER_JOURNEYS.md` for complete demo scripts.

---

## Configuration Reference

| File | Variable | Purpose |
|------|----------|---------|
| `.env` | `MCP_SERVER_URL` | Full URL to your MCP endpoint (including `/mcp`) |
| `env/.env.dev` | `TEAMS_APP_ID` | Auto-generated during provision |
| `env/.env.dev` | `APP_NAME_SUFFIX` | Appended to agent name (e.g. "dev") |

---

## Data Disclaimer

⚠️ **All healthcare data in this demo is entirely fictional** and generated randomly for demonstration purposes. It does not represent real healthcare performance data.

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Agent can't connect to MCP server | Ensure DevTunnel is running and URL in `.env` is correct |
| 500 error from MCP endpoint | Check `python server.py` is running and responding at `/mcp` |
| Provision fails with icon error | Ensure `outline.png` is 32x32 with transparent background |
| Agent doesn't appear in Copilot | Wait a few minutes after provision; try refreshing the page |
| Code Interpreter not generating charts | Explicitly ask for "a chart" or "a visualisation" in your prompt |

