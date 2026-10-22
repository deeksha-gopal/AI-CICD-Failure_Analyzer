# Publish this project on GitHub

## 1. Review and run the code first

- Read `README.md` and `docs/architecture.md`.
- Run `docker compose up --build` (or follow the local-development commands in `README.md`).
- Analyze one of the sample logs and examine the report and saved history.
- Inspect the FastAPI route handlers, the Docker Compose configuration, and the React UI.
- Verify that the AI/API project claims in your CV match what you can personally demonstrate.

The supplied project was generated as an initial working implementation for you. It is not evidence of a prior independently completed project; run it and customize it before presenting it as your own engineering work.

## 2. Create a GitHub repository

1. Sign in to https://github.com/new.
2. Name the repository `ai-cicd-failure-analyzer`.
3. Choose **Public** if you want recruiters to inspect it.
4. Do not initialize the repository with an extra README, license, or `.gitignore`—those are already included.
5. Create the empty repository.

## 3. Push all files from your computer

Open Terminal in the **extracted `ai-cicd-failure-analyzer` folder**:

```bash
git init
git add .
git commit -m "Add CI/CD failure analyzer portfolio project"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ai-cicd-failure-analyzer.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub username. The GitHub website may ask you to authenticate with a supported method (for example Git Credential Manager or SSH keys); GitHub does not support account passwords for command-line pushes.

## 4. Once npm can access the internet

```bash
cd frontend
npm install
cd ..
git add frontend/package-lock.json
git commit -m "Add reproducible npm dependency lockfile"
git push
```

This project archive omits `node_modules` (as standard) and does not include an npm lockfile because the original generation environment could not reach the npm registry. On a network-connected computer, `npm install` resolves dependencies and creates that lockfile.

## 5. Improve the repository for a technical recruiter

- Pin the project repository on your GitHub profile.
- Add **one real screenshot** or short screen recording after launching the dashboard.
- In the repository "About" field, describe it as: "React + TypeScript and FastAPI dashboard for CI/CD failure logs, SQL history, Docker deployment, and optional LLM diagnostics."
- Use topics such as `python`, `fastapi`, `react`, `typescript`, `devops`, `docker`, `github-actions`, `llm`, `cicd`.
- Add a brief personal write-up explaining which components you tested and improved, what you learned, and what you'd change for production.
- Never upload a real `.env`, production logs, credentials, or private employer/university data.
