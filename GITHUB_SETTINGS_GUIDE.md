# GitHub Repository Settings Guide

## Step-by-Step Configuration for Public Read-Only Repository

### 1. Set Default Branch to Main

1. Go to your repository: `https://github.com/VinayKDH/Infosys_Agentic`
2. Click **Settings** (top right, gear icon)
3. Click **Branches** (left sidebar)
4. Under **Default branch**, select `main`
5. Click **Update** if needed

### 2. Protect Main Branch (Prevent Pushes)

1. In **Settings** → **Branches**
2. Click **Add branch protection rule**
3. Branch name pattern: `main`
4. Enable these settings:
   - ✅ **Require a pull request before merging**
     - Require approvals: 1
   - ✅ **Require status checks to pass before merging**
   - ✅ **Require branches to be up to date before merging**
   - ✅ **Restrict who can push to matching branches**
     - Add yourself as an exception if needed
   - ✅ **Include administrators** (so even you need PRs)
5. Click **Create**

### 3. Remove Collaborators (Optional)

1. Go to **Settings** → **Collaborators and teams**
2. Remove any collaborators you don't want to have write access
3. For a truly read-only public repo, remove all collaborators

### 4. Verify Repository is Public

1. Go to **Settings** → **General**
2. Scroll to **Danger Zone**
3. Ensure "Change repository visibility" shows "Public"
4. If not, click and change to Public

### 5. Disable Issues/Wiki (Optional)

1. Go to **Settings** → **General**
2. Scroll to **Features**
3. Uncheck:
   - ❌ Issues
   - ❌ Wiki
   - ❌ Projects
   (Keep only what you want public users to access)

## Result

After these settings:
- ✅ Public users can clone and read the repository
- ✅ Public users **cannot** push changes
- ✅ Only `main` branch is visible by default
- ✅ Day2 branch is not in remote (hidden from public)
- ✅ Even you need pull requests to make changes (if you enabled that)

## Testing

To test as a public user would:

```bash
# Create a test directory
mkdir test-public-clone
cd test-public-clone

# Clone the repository
git clone https://github.com/VinayKDH/Infosys_Agentic.git
cd Infosys_Agentic

# Check branches
git branch -a
# Should only show: remotes/origin/main

# Try to push (should fail)
git checkout -b test-branch
echo "test" > test.txt
git add test.txt
git commit -m "test"
git push origin test-branch
# Should get: remote: Permission denied
```

## Important Notes

1. **Day2 Branch:** Has been removed from remote. It only exists locally on your machine.
2. **Making Changes:** If you enabled branch protection, you'll need to:
   - Create a branch
   - Make changes
   - Create a pull request
   - Approve and merge
3. **Secrets:** Double-check that no `.env` files with API keys are committed
4. **`.gitignore`:** Ensure sensitive files are in `.gitignore`

