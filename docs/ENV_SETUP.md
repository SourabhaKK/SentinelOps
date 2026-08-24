# Environment Setup Guide

This document guides you through setting up your `.env` file with API keys for SentinelOps Phase 0 prerequisites.

## Quick Start

1. **Copy the template:**
   ```bash
   npm run setup:env
   # or manually:
   cp .env.example .env
   ```

2. **Fill in your API keys** (see instructions below)

3. **Verify setup:**
   ```bash
   npm run check:env
   ```

---

## API Keys Required

### 1. Daytona API Key
**Purpose**: Sandbox execution environment for drift-computation SKILL.md

**Steps**:
1. Go to https://daytona.io
2. Sign up for free account (or log in)
3. Navigate to **Dashboard → API Keys**
4. Click **Generate New Key**
5. Copy the key
6. Paste into `.env` file:
   ```
   DAYTONA_API_KEY=your_key_here
   ```

**Verify**: Run `npm run check:env` — should show ✅ under "Keys Present"

---

### 2. Gemini 2.0 Flash API Key
**Purpose**: Primary LLM model for TrueForge agent

**Steps**:
1. Go to https://ai.google.dev/
2. Click **Get API Key** (top right)
3. Select or create a Google Cloud project
4. Click **Create API Key**
5. Copy the API key
6. Paste into `.env` file:
   ```
   GOOGLE_API_KEY=your_key_here
   ```

**Verify**: Run `npm run check:env` — should show ✅ under "Keys Present"

**Note**: Free tier includes generous quotas. No credit card required if using free tier.

---

### 3. Groq API Key
**Purpose**: Fallback LLM model (same purpose as Gemini, used if primary fails)

**Steps**:
1. Go to https://console.groq.com/
2. Sign up for free account (or log in)
3. Navigate to **API Keys** section
4. Click **Create New Key**
5. Copy the key
6. Paste into `.env` file:
   ```
   GROQ_API_KEY=your_key_here
   ```

**Verify**: Run `npm run check:env` — should show ✅ under "Keys Present"

**Note**: Free tier includes quota reset monthly. Perfect for hackathon use.

---

## Optional: GitHub Token

If you need to access private repositories or increase GitHub API rate limits:

1. Go to https://github.com/settings/tokens
2. Click **Generate new token** → **Generate new token (classic)**
3. Select scopes: `repo`, `read:org`
4. Generate and copy
5. Add to `.env`:
   ```
   GITHUB_TOKEN=your_token_here
   ```

This is optional for Phase 0 (public repo access works without it).

---

## Checking Your Setup

### Command: `npm run check:env`
This validates that all required keys are present:

```
=== Phase 0 Prerequisites Status ===

✅ Keys Present:
  • DAYTONA_API_KEY = abc123def...
  • GOOGLE_API_KEY = ghi789jkl...

❌ Missing Keys (1 of 3):
  • GROQ_API_KEY

⏳ Still need 1 key(s). Update .env file and run this script again.
```

Once all 3 required keys are present:
```
✨ All required keys configured! Ready for Phase 1.3 (TrueForge setup)
```

---

## Security Notes

⚠️ **IMPORTANT**:
- `.env` is in `.gitignore` — it will NOT be committed to git
- Never share your `.env` file or paste keys into public channels
- If you accidentally commit keys, revoke them immediately and generate new ones
- Each key should be isolated per TECHSTACK.md (not shared between services)

---

## Troubleshooting

### "❌ .env file not found"
**Solution**: Run `npm run setup:env` to create it from template

### "Empty value for DAYTONA_API_KEY"
**Solution**: Make sure you pasted the key correctly (no leading/trailing spaces):
```
DAYTONA_API_KEY=abc123   ❌ (space after)
DAYTONA_API_KEY=abc123  ✅ (correct)
```

### "Keys present but Phase 1.3 still fails"
**Solution**: Check that environment is loaded before starting TrueForge:
```bash
# Verify keys are loaded:
npm run check:env

# Then start TrueForge:
npm run trueforge
```

### API key not recognized
**Solution**: 
- Double-check you copied the entire key (sometimes keys are long)
- Verify the key hasn't expired or been revoked
- Try generating a new key from the service dashboard

---

## What's Next?

Once `npm run check:env` shows ✨ all keys configured:
1. Proceed to Phase 1.3 (TrueForge setup)
2. Start TrueForge with: `npm run trueforge`
3. Test connection with: basic chat turn

See [WORKFLOW.md](../WORKFLOW.md) for phase sequencing.
