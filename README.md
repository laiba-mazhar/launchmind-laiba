# launchmind-laiba
<<<<<<< HEAD
# LaunchMind 🚀

> A Multi-Agent System that autonomously runs a micro-startup — from idea to GitHub PR, Slack launch post, and cold outreach email — without any human intervention.

---

## Startup Idea

**TutorConnect** — A mobile app that connects university students with verified local tutors for affordable, on-demand study sessions. Students post what subject they need help with, tutors respond with availability and rates, and sessions are booked in under 2 minutes.

---

## Agent Architecture

```
                        ┌─────────────────┐
                        │   CEO Agent     │  ← Orchestrator
                        │  (orchestrator) │     LLM: GPT-4o
                        └────────┬────────┘
                                 │  decomposes idea, dispatches tasks,
                                 │  reviews all outputs, runs feedback loops
                ┌────────────────┼────────────────┐
                │                │                │
                ▼                ▼                ▼
      ┌─────────────────┐   ┌──────────┐   ┌──────────────────┐
      │  Product Agent  │   │ Engineer │   │ Marketing Agent  │
      │  (spec writer)  │   │  Agent   │   │  (growth hacker) │
      │   LLM: GPT-4o   │   │ GPT-4o   │   │   LLM: GPT-4o    │
      └────────┬────────┘   └────┬─────┘   └────────┬─────────┘
               │                 │                  │
               │ product spec    │ PR + issue URL   │ copy JSON
               └─────────────────┼──────────────────┘
                                 │ all results
                                 ▼
                        ┌─────────────────┐
                        │    QA Agent     │
                        │  (reviewer)     │
                        │   LLM: GPT-4o   │
                        └─────────────────┘
                                 │ review report
                                 ▼
                        ┌─────────────────┐
                        │   CEO Agent     │ ← acts on QA verdict
                        │  (final review) │   may trigger re-runs
                        └─────────────────┘
```

### Message Flow (simplified)

```
CEO → product (task)
product → engineer (task)
product → marketing (task)
product → CEO (confirmation)
CEO → product (revision_request)  ← FEEDBACK LOOP 1
engineer → CEO (result: pr_url, issue_url, html)
CEO → engineer (revision_request) ← FEEDBACK LOOP 2
marketing → CEO (result: copy JSON)
CEO → qa (task: html + copy + spec + pr_url)
qa → CEO (result: review_report)
CEO → engineer (revision_request) ← FEEDBACK LOOP 4 (if QA fails)
CEO → CEO (result: complete)
```

All messages follow the schema:
```json
{
  "message_id": "uuid",
  "from_agent": "ceo",
  "to_agent": "product",
  "message_type": "task | result | revision_request | confirmation",
  "payload": { ... },
  "timestamp": "2025-10-01T09:00:00Z",
  "parent_message_id": "uuid or null"
}
```

---

## Platform Integrations

| Platform | Agent | What it does |
|---|---|---|
| **GitHub** | Engineer | Creates branch, commits `index.html`, opens pull request, creates issue |
| **GitHub** | QA | Posts inline review comments on the PR |
| **Slack** | Marketing | Posts product launch message to `#launches` using Block Kit |
| **Slack** | CEO | Posts final mission summary to `#launches` |
| **SendGrid** | Marketing | Sends cold outreach email to test inbox |
| **OpenAI GPT-4o** | All agents | LLM reasoning, generation, and review |

---

## Setup

### 1. Clone and install

```bash
git clone https://github.com/your-username/launchmind-your-group.git
cd launchmind-your-group
pip install -r requirements.txt
```

### 2. Set up platforms

**GitHub**
- Create a public repo named `launchmind-your-group`
- Go to Settings → Developer Settings → Personal Access Tokens (classic)
- Generate token with `repo` + `workflow` scopes
- Add an empty `main` branch (create a README.md commit so the repo is non-empty)

**Slack**
- Create a free Slack workspace
- Go to [api.slack.com/apps](https://api.slack.com/apps) → Create New App → From scratch
- Under *OAuth & Permissions* add bot scopes: `chat:write`, `channels:read`, `channels:join`
- Install to workspace, copy the `xoxb-...` token
- Create a `#launches` channel and invite the bot: `/invite @LaunchMindBot`

**SendGrid**
- Free account at [sendgrid.com](https://sendgrid.com) (100 emails/day, no credit card)
- Settings → API Keys → create key with *Mail Send* permission
- Settings → Sender Authentication → verify your sender email

### 3. Configure environment

```bash
cp .env.example .env
# Fill in all values in .env
```

### 4. Run

```bash
python main.py
# Or with a custom idea:
python main.py "A SaaS tool that auto-generates invoices from Slack messages"
```

---

## Links

- **GitHub PR** (created by Engineer agent): [link added after first run]
- **Slack workspace** (invite): [add your workspace invite link here]

---

## Group Members

| Name | Agent |
|---|---|
| Student A | CEO Agent |
| Student B | Engineer Agent + Product Agent |
| Student C | Marketing Agent + QA Agent |
=======
# launchmind-laiba
>>>>>>> 363633fb88404e34d3fc3a6a05d11fce23bca139
