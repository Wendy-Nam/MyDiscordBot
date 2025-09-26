# LingoBot — AI-powered Real-time Korean-English Translation Bot for Discord

![Image](/docs/thumbnail.png)

## [Project Details & Background](https://educated-tarsier-f16.notion.site/GCP-Infra-Automation-Discord-Bot-Deployment-2109bf46184a805eaf06cf4851c47821?source=copy_link)

## Overview

**LingoBot** is an AI-powered Discord bot that provides real-time bidirectional translation between Korean and English in Discord servers.  
It helps global project teams and online communities communicate seamlessly across language barriers.

The bot leverages **OpenAI GPT API** for translation, combined with lightweight infrastructure designed for easy deployment and scalability.

## Current Capabilities

- **Bidirectional translation** between Korean and English
- Real-time translation in selected Discord channels
- Simple command interface to enable/disable translation
- Designed for fast interaction and minimal latency

## Architecture

- **Language**: Python (discord.py, openai, langdetect)
- **Infrastructure**:
    - Deployed on **Google Cloud Platform (GCP) Compute Engine**
    - Infrastructure automated with **Terraform** and **GitHub Actions**
    - GitHub Secrets used for secure credential management
    - Current Terraform setup enables initial deployment; plans to implement remote tfstate backend for improved update workflows

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

## Limitations & Future Plans

- Current version supports **bidirectional Korean ↔ English translation** only.
- Future enhancements planned:
    - Multi-language support beyond Korean-English
    - Configurable translation pairs per channel
    - Improved remote Terraform state management for safer incremental updates
    - Enhanced logging and monitoring

## Documentation & Support

This README provides a high-level overview and basic usage guide.  
More detailed technical documentation and advanced configuration guides will be added in future updates.

For questions or feedback, please contact: [hanzoom2000@gmail.com]

## License

MIT License
