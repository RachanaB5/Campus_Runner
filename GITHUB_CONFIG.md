# GitHub Configuration Guide for Campus Runner

## Automated (Already Configured)

✅ **Dependabot** (`.github/dependabot.yml`)
- Automatically checks npm, pip, Docker, and GitHub Actions for updates weekly
- Creates PRs for new versions
- Assign reviewers: RachanaB5

✅ **CODEOWNERS** (`.github/CODEOWNERS`)
- Auto-assigns reviewers based on changed files
- Requires approval from code owners before merge

✅ **CodeQL Analysis** (`.github/workflows/codeql.yml`)
- Weekly static security scanning for Python and JavaScript
- Detects potential vulnerabilities and code quality issues

---

## Manual GitHub Settings (Required)

### 1. **Branch Protection Rules**
Go to: `Settings > Branches > main > Add Rule`

Configure:
- ✅ Require pull request reviews before merging
  - Required approving reviews: **1**
  - Dismiss stale PR approvals: **checked**
  - Require review from code owners: **checked**
- ✅ Require status checks to pass before merging
  - Required checks:
    - `Backend (Python 3.11)`
    - `Backend (Python 3.12)`
    - `Frontend Lint`
    - `Frontend Type Check`
    - `Frontend Tests`
    - `Frontend Build`
- ✅ Require branches to be up to date before merging
- ✅ Require conversation resolution before merging
- ✅ Automatically delete head branches

### 2. **GitHub Pages** (Optional - Currently Unused)
Go to: `Settings > Pages`
- Set Source to: **None** (to disable)

### 3. **Deploy Keys** (For Production Deployment)
Go to: `Settings > Deploy keys > Add deploy key`
- Add SSH key with push access for automated deployments
- Add comment: "Campus Runner production deployment automation"

### 4. **GitHub Environments** (For Staged Deployments)
Go to: `Settings > Environments`

Create **Staging** environment:
- Deployment branch filter: `develop`
- Protection rules: None (auto-deploy from develop)

Create **Production** environment:
- Deployment branch filter: `main`
- Protection rules: Require approval from RachanaB5 before deploy

### 5. **Secrets & Variables**
Go to: `Settings > Secrets and variables > Actions`

Add secrets:
```
GHCR_TOKEN           - GitHub Container Registry token
DOCKER_USERNAME      - Docker Hub username (if using DockerHub)
DOCKER_PASSWORD      - Docker Hub password
RAZORPAY_KEY_ID      - From Razorpay dashboard
RAZORPAY_KEY_SECRET  - From Razorpay dashboard
```

Add variables (non-sensitive):
```
GHCR_REGISTRY        - ghcr.io
DOCKER_REGISTRY      - docker.io (if using DockerHub)
```

### 6. **Required Status Checks**
Go to: `Settings > Branches > main`

Under "Require status checks to pass":
- ✅ All workflow jobs passing
- ✅ CodeQL analysis passing (when enabled)

---

## Optional GitHub Features to Consider

### **Auto-merge for Dependabot** (Skip PRs, merge directly)
Create workflow: `.github/workflows/dependabot-auto-merge.yml`
```yaml
- Automatically merges Dependabot patch updates
- Requires all CI/CD checks to pass
```

### **Issue Templates** (Standardize bug reports)
- Create `.github/ISSUE_TEMPLATE/bug_report.md`
- Create `.github/ISSUE_TEMPLATE/feature_request.md`

### **Pull Request Template** (Standardize PR descriptions)
- Create `.github/pull_request_template.md`

### **GitHub Discussions** (Community Q&A)
- Enable in: `Settings > Features > Discussions`

### **Release Automation** (Auto-generate release notes)
- Enable in: `Settings > General > Automatically generate release notes`
- Configure templates: `Settings > Automated security and version updates > Release automation`

---

## Monitoring & Maintenance

- **Actions** tab: View all workflow runs and logs
- **Security** tab: See CodeQL alerts and Dependabot updates
- **Insights > Network**: View commit history and branches
- **Insights > Traffic**: See repository stats

---

## Next Steps

1. Go to `Settings > Branches` and create branch protection rule for **main**
2. Go to `Settings > Pages` and set source to **None** to disable Pages
3. Add your Docker registry credentials to `Settings > Secrets`
4. Test: Make a PR and verify status checks + code owner review requirement
