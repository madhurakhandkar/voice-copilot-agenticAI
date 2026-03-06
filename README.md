# AI Powered Copilot

Anlearning platform that tracks user engagement in real-time to provide personalized feedback. This project uses a **Chrome Extension** to track usr behvaior.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the App](#running-the-app)
- [Browser Extension](#browser-extension)

## Features

- **Behavioral Tracking:** Captures user clicks, scrolls, and navigation events across the web via a custom Chrome Extension.
- **AI Analysis:** Uses **Anthropic Claude 3 Haiku** (via AWS Bedrock) to analyze user actions and determine learning status.
- **Voice Feedback:** Synthesizes AI responses into speech using **AWS Polly** and plays them  via Pygame.
- **Interactive Dashboard:** A React & Material UI frontend that simulates a Learning Management System (LMS) and displays chat/feedback.

## Tech Stack

- **Backend:** Python, FastAPI, Uvicorn, Pydantic
- **AI & Cloud:** AWS Bedrock, AWS Polly, Boto3
- **Frontend:** React.js, Material UI (MUI), HTML5
- **Browser Automation:** Chrome Extension API (Manifest V3)
- **Audio:** Pygame, Wave

## Prerequisites

- Python 3.9+
- AWS Credentials configured locally (usually in `~/.aws/credentials`) with access to **Bedrock** and **Polly**.

## Installation

```bash
# 1. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install fastapi uvicorn boto3 pygame requests
```
