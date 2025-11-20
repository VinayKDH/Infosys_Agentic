# Repository Setup Guide

## Public Repository Configuration

This repository is configured to:
- ✅ Show only the `main` branch by default when cloning
- ✅ Prevent unauthorized pushes (read-only for public)
- ✅ Keep Day2 branch private (removed from remote)

## For Repository Administrators

### To Hide Day2 Branch from Public

The Day2 branch has been removed from the remote repository. If you need to access it:

1. **Keep Day2 locally only:**
   ```bash
   git checkout Day2
   # Work on Day2 branch locally
   # Don't push it to remote
   ```

2. **If you need to push Day2 to a private location:**
   - Create a separate private repository
   - Add it as a different remote:
     ```bash
     git remote add private <private-repo-url>
     git push private Day2
     ```

### To Prevent Pushes (GitHub Settings)

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Branches**
3. Add branch protection rule for `main`:
   - ✅ Require pull request reviews
   - ✅ Require status checks
   - ✅ Restrict who can push to matching branches
   - ✅ Include administrators

4. Go to **Settings** → **Collaborators**
   - Remove all collaborators (for public read-only repo)
   - Or set permissions to "Read" only

### Default Branch Configuration

1. Go to **Settings** → **Branches**
2. Under "Default branch", ensure `main` is selected
3. This ensures clones default to `main` branch

## For Users Cloning the Repository

### Standard Clone (Main Branch Only)

```bash
git clone https://github.com/VinayKDH/Infosys_Agentic.git
cd Infosys_Agentic
# You'll be on main branch by default
```

### What Users Will See

- ✅ Only `main` branch visible
- ✅ All Day 1-3 labs available
- ✅ Clean, production-ready code
- ❌ Day2 branch not visible (removed from remote)

### If Users Try to Push

They will get an error:
```
remote: Permission denied
```

This is expected - the repository is read-only for public users.

## Repository Structure

### Main Branch Contains:
- `labs/Day1_Medium/` - Day 1 Medium Lab
- `labs/Day1_Advanced/` - Day 1 Advanced Lab
- `labs/Day2_Medium/` - Day 2 Medium Lab
- `labs/Day2_Advanced/` - Day 2 Advanced Lab
- `labs/Day3_Medium/` - Day 3 Medium Lab
- `labs/Day3_Advanced/` - Day 3 Advanced Lab

### Day2 Branch (Local Only):
- All labs from main
- Trainer guides
- Documentation
- Additional projects (Amex, CustomerSupportAgent)

## Security Notes

1. **Public Repository:** All code in `main` branch is publicly visible
2. **No Secrets:** Ensure no API keys, passwords, or secrets are committed
3. **Read-Only:** Public users cannot push changes
4. **Branch Protection:** Configure branch protection rules on GitHub

## Verification

To verify the setup:

```bash
# Clone as a new user would
git clone https://github.com/VinayKDH/Infosys_Agentic.git test-clone
cd test-clone
git branch -a
# Should only show main branch
```

