# LingoBot — AI-powered Real-time Korean-English Translation Bot for Discord

![Image](/docs/thumbnail.png)

## Overview

**LingoBot** is an AI-powered Discord bot that provides real-time bidirectional translation between Korean and English in Discord servers.  
It helps global project teams and online communities communicate seamlessly across language barriers.

The bot leverages **OpenAI GPT API** for translation, combined with lightweight infrastructure designed for easy deployment and scalability.

## Features

- **Bidirectional translation** between Korean and English
- **Real-time translation** in selected Discord channels with 0.5-1.5 second response time
- **AI-powered translation** using GPT models with custom prompts for natural translation
- **Channel management** via slash commands (`/add_channel`, `/del_channel`)
- **Text preprocessing** with URL masking and message splitting
- **Discord formatting preservation** and bot conflict prevention

## Development Background

LingoBot (V1) was developed in September 2024 for an international game jam project to solve communication problems caused by language barriers between Korean and English users. The development resulted in immediate positive effects on team collaboration and atmosphere improvement.

**Detailed review**: [Lingo V1 - Real Team Adoption Case Study](https://educated-tarsier-f16.notion.site/GCP-Infra-Automation-Discord-Bot-Deployment-2109bf46184a805eaf06cf4851c47821?source=copy_link)

## LingoBot V1 vs V2 Comparison

| Feature | V1 | V2 |
|---|---|---|
| **User Interface** | Text-based commands (`!add_channel`, `!del_channel`) | App slash commands added (`/add_channel`, `/del_channel`) |
| **Language Detection** | Basic Korean character inclusion check (may be inaccurate) | Accurate language detection using `langdetect` library |
| **Environment Configuration** | Code variable modification at runtime (inconvenient management) | Separation and management via `.env` file (safer and more convenient) |
| **Deployment** | GCP Compute Engine Free Tier | GCP Compute Engine Free Tier with Terraform and GitHub Actions infrastructure deployment |

## Architecture

- **Language**: Python (discord.py, openai, langdetect)
- **Infrastructure**:
    - Deployed on **Google Cloud Platform (GCP) Compute Engine**
    - Infrastructure automated with **Terraform** and **GitHub Actions**
    - GitHub Secrets used for secure credential management
    - Current Terraform setup enables initial deployment; plans to implement remote tfstate backend for improved update workflows

## Prerequisites

- **Discord Bot Token**: Must be generated manually from Discord Developer Portal
- **OpenAI API Token**: Required for GPT API access

## GitHub Secrets

| Secret Name            | Purpose |
|------------------------|---------|
| DISCORD_BOT_TOKEN      | Discord bot authentication token |
| OPENAI_API_KEY         | OpenAI GPT API key for translations |
| GCP_SA_KEY             | Google Cloud Platform service account key for Compute Engine access |
| IGNORED_ROLE_IDS       | List of Discord role IDs to exclude from translation |
| REMOTE_SSH_HOST        | Target VM host for SSH-based deployment |
| REMOTE_SSH_USERNAME    | SSH username for VM access |
| REMOTE_SSH_KEY         | Private SSH key for deployment |
| REMOTE_SSH_PASSPHRASE  | SSH key passphrase for secure connection |

## Limitations & Future Plans

- Current version supports **bidirectional Korean ↔ English translation** only.
- Future enhancements planned:
    - Multi-language support beyond Korean-English
    - Configurable translation pairs per channel
    - Improved remote Terraform state management for safer incremental updates
    - Enhanced logging and monitoring

## Usage

### Commands

- `/add_channel` — Enable bidirectional Korean-English translation in the current channel
- `/del_channel` — Disable translation in the current channel

### Deployment

#### Infrastructure Setup
1. Configure GitHub Secrets with required credentials (see table above)
2. Manually trigger the **"Terraform GCP Deploy"** workflow to provision GCP infrastructure
3. Terraform creates a Compute Engine instance with the specified configuration

#### Bot Deployment
1. Manually trigger the **"Deploy Python Bot"** workflow 
2. GitHub Actions connects to the VM using pre-configured SSH credentials from GitHub Secrets
3. The workflow automatically:
   - Copies the Python bot source code to the VM
   - Sets up Python virtual environment
   - Installs dependencies from `requirements.txt`
   - Creates `.env` file with environment variables (`DISCORD_BOT_TOKEN`, `OPENAI_API_KEY`, `IGNORED_ROLE_IDS`)
   - Starts the bot service using `run.sh`
4. Invite the bot to your Discord server and manage translation via bot commands

**Deployment Flow**: Infrastructure (manual) → Deploy (manual)

**Note**: Both workflows use `workflow_dispatch` triggers, requiring manual execution through GitHub Actions interface.

## Bot Server Invitation

### 1. Generate Invitation Link from Discord Developer Portal
1. Access [Discord Developer Portal](https://discord.com/developers/applications)
2. Select your bot application
3. Navigate to **"OAuth2"** → **"URL Generator"**

### 2. Configure Required Permissions
**SCOPES:**
- ✅ `bot`
- ✅ `applications.commands` (for slash commands)

**BOT PERMISSIONS:**
- ✅ `Send Messages`
- ✅ `View Channels`
- ✅ `Read Message History`
- ✅ `Use Slash Commands`

### 3. Server Invitation & Setup
1. Copy the **GENERATED URL** and open in browser
2. Select target server and click **"Authorize"**
3. Ensure bot role has appropriate position in server hierarchy (avoid permission restrictions)
4. Use `/add_channel` command to activate bot in desired channels
5. Test translation functionality with sample messages

## Documentation & Support

This README provides a high-level overview and basic usage guide.  
More detailed technical documentation and advanced configuration guides will be added in future updates.

For questions or feedback, please contact: [hanzoom2000@gmail.com]

## License

MIT License
