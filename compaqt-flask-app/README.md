# Compaqt - Prompt Packing Tool

A post-retrieval prompt packing tool for LLM coding agents. Compaqt takes retrieved code files, minimizes them, and packs them into a token budget so the LLM receives fewer tokens without losing reasoning quality.

## Features

- **Token Counting**: Uses OpenAI's tiktoken BPE tokenizer (with fallback)
- **Code Minimization**: Removes comments, docstrings, and blank lines
- **Greedy Packing**: Fits maximum code into your token budget
- **Token Savings Report**: See exactly how much you're saving
- **Download**: Export packed prompts as `.txt` files

## Installation

1. Clone or download this project
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Running Locally

```bash
python app.py
```

Then open your browser to: **http://localhost:5000**

## Usage

1. View the sample Python files in the "Retrieved Files" column
2. Adjust the token budget slider (default: 4000 tokens)
3. Click "Pack Context" to minimize and pack the files
4. Review the token savings report
5. Download the packed prompt if needed

## Project Structure

```
compaqt/
├── app.py                 # Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/
│   └── index.html        # Web UI template
├── static/
│   └── styles.css        # Styling
└── compaqt/
    ├── __init__.py
    ├── packer.py         # Minimization and packing logic
    ├── tokenizer.py      # Token counting
    └── sample_repo/      # Sample Python files
        ├── file1.py
        ├── file2.py
        ├── file3.py
        └── file4.py
```

## How It Works

1. **Tokenization**: Each file's token count is calculated using tiktoken
2. **Minimization**: Comments, docstrings, and blank lines are stripped
3. **Packing**: Files are sorted by size and greedily packed into budget
4. **Output**: A packed prompt with metadata headers for each file

---

## Deployment

### Railway (Recommended - Easiest)

1. Push your code to GitHub
2. Go to [railway.app](https://railway.app) and sign in with GitHub
3. Click **"New Project"** → **"Deploy from GitHub repo"**
4. Select your repository
5. Railway auto-detects `railway.toml` and deploys automatically
6. Click **"Generate Domain"** to get your public URL

**Or via CLI:**
```bash
npm install -g @railway/cli
railway login
railway init
railway up
```

---

### Render

1. Push your code to GitHub
2. Go to [render.com](https://render.com) and sign in
3. Click **"New"** → **"Web Service"**
4. Connect your GitHub repo
5. Render detects `render.yaml` and configures automatically
6. Click **"Create Web Service"**

Your app will be live at `https://compaqt.onrender.com` (or similar)

---

### Fly.io

1. Install Fly CLI: 
```bash
curl -L https://fly.io/install.sh | sh
```

2. Sign up and authenticate:
```bash
fly auth signup
# or
fly auth login
```

3. Launch your app:
```bash
fly launch
```

4. Deploy:
```bash
fly deploy
```

Your app will be live at `https://compaqt-demo.fly.dev`

---

## Configuration Files

| File | Platform | Purpose |
|------|----------|---------|
| `Procfile` | Heroku/Railway | Defines web process |
| `railway.toml` | Railway | Build & deploy config |
| `render.yaml` | Render | Service definition |
| `fly.toml` | Fly.io | App configuration |
