# Phase 1.3 — TrueForge Setup

Getting TrueForge running locally with Gemini 2.0 Flash (primary) and Groq (fallback) connected.

## Prerequisites

Before proceeding, verify:
```bash
npm run check:env
```

Should show all 3 keys present:
- ✅ DAYTONA_API_KEY
- ✅ GOOGLE_API_KEY
- ✅ GROQ_API_KEY

## Start TrueForge

```bash
npm run trueforge
```

This starts TrueForge with the configuration in `trueforge.config.json`.

**Expected output:**
```
TrueForge Agent Runtime starting...
Loading configuration from trueforge.config.json
Primary model: Gemini 2.0 Flash (Google)
Fallback model: Groq (Mixtral)
Sandbox: Daytona
Session storage: SQLite

Ready for chat. Type your message or 'help' for commands.
```

## Test a Basic Chat Turn

Once TrueForge is running, type a simple message to verify the agent works:

```
> Hello, I'm testing the SentinelOps agent. Can you confirm you're running?
```

**Expected response:**
- Agent responds with acknowledgment
- Uses Gemini 2.0 Flash (primary model)
- If Gemini fails, fallback to Groq
- No errors in logs

## What Should Work

✅ Agent responds to natural language
✅ Session persists between turns
✅ Model switching works (if primary fails)
✅ Basic tool-calling framework is ready (MCP integration)

## What's NOT Required Yet

❌ MCP servers fully operational (Phase 1.4-1.5)
❌ Investigation subagent (Phase 1)
❌ Incident scenarios (Phase 2)

## Troubleshooting

### "API key rejected"
- Check `npm run check:env` shows all 3 keys
- Verify keys are correctly copied (no trailing spaces)
- Try generating new keys from service dashboards

### "TrueForge command not found"
```bash
# Install globally if needed
npm install -g @truefoundry/trueforge

# Or use npx
npx @truefoundry/trueforge
```

### Model connection fails
- If Gemini fails, check Google API key
- If both fail, check internet connection
- Check API quotas in service dashboards

### Port already in use
- TrueForge uses port 3000 by default
- Kill existing process: `lsof -ti:3000 | xargs kill -9` (macOS/Linux)
- Or specify different port: `npm run trueforge -- --port 3001`

## Configuration

Edit `trueforge.config.json` to:
- Change model selection
- Configure sandbox provider
- Register additional MCP servers
- Adjust session storage

See [TrueForge Documentation](https://truefoundry.com/docs) for full configuration options.

## Next Steps

Once Phase 1.3 is complete (TrueForge running, models connected, basic chat works):

→ **Phase 1.4**: Register GitHub MCP server
→ **Phase 1.5**: Integrate telemetry MCP server

## Status Check

When `npm run trueforge` starts successfully and you can chat, Phase 1.3 is complete. Log the confirmation in BUILD_LOG.md.
