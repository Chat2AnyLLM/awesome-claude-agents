# GitHub Workflow Setup

## Personal Access Token (PAT) Setup

The automated README generation workflow requires a Personal Access Token (PAT) with the following permissions:

### Required Permissions:
- **repo** (Full control of private repositories) - OR for public repos:
  - `public_repo` (Access public repositories)
  - `workflow` (Update GitHub Action workflows)

### Steps to Create PAT:

1. Go to [GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Give it a descriptive name like "Awesome Claude Agents Workflow"
4. Select the required scopes (see above)
5. Copy the generated token (save it securely - you won't see it again!)

### Repository Secret Setup:

1. Go to your repository settings: **Settings → Secrets and variables → Actions**
2. Click "New repository secret"
3. Name: `PERSONAL_ACCESS_TOKEN`
4. Value: Paste your PAT from step 5 above
5. Click "Add secret"

### Workflow Features:
- ✅ **Hourly automated updates** (runs every hour at minute 0)
- ✅ **Manual trigger support** (via GitHub Actions tab)
- ✅ **Change detection** (only commits when README actually changes)
- ✅ **Proper authentication** (uses PAT for secure operations)

The workflow will now use your PAT for all Git operations, providing more reliable authentication and avoiding potential rate limiting issues.