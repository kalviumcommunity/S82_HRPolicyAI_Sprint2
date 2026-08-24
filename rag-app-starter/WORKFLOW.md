# GitHub Workflow

## 1. Branching Strategy

The `main` branch contains only stable and releasable code.

All new features, fixes, documentation changes, and refactoring work must be developed in separate branches.

### Branch Naming

Branches follow this format:

`[type]/[short-description]`

Examples:

- `feature/document-ingestion`
- `fix/retrieval-error`
- `docs/github-workflow`
- `refactor/rag-pipeline`
- `chore/update-dependencies`

For this project, feature branches are created from `main`.

After a pull request is reviewed and merged, the branch should be deleted.

---

## 2. Commit Message Convention

Commit messages follow this format:

`[type]: [description]`

Allowed types:

- `feat` - new functionality
- `fix` - bug fixes
- `docs` - documentation changes
- `refactor` - code restructuring
- `chore` - maintenance work

Examples:

- `feat: add HR document ingestion`
- `fix: handle empty policy documents`
- `docs: update project setup instructions`
- `refactor: improve document processing`
- `chore: update project dependencies`

This keeps the Git history clear and makes it easier to understand what changed and why. Consistent commit messages can also support automated changelog generation.

---

## 3. Pull Request Review Process

Every feature or significant change must be submitted through a pull request.

Pull requests require at least one approval before merging.

Code review focuses on:

- Correctness
- Code clarity
- Data integrity
- Test coverage
- Appropriate documentation

Commit messages are also reviewed as part of the pull request.

The pull request should explain what changed, why it changed, and which GitHub issue it addresses.

---

## 4. GitHub Issue Tracking

Every feature or fix should begin with a GitHub issue.

Each issue should contain:

- Clear action-oriented title
- Description explaining why the work matters
- Definition of done
- Appropriate label
- Assigned developer

Issues provide context and make responsibilities visible to the team.

Issues are closed when the corresponding pull request is merged.

---

## 5. HRPolicyAI Development Flow

The team's standard workflow is:

1. Create a GitHub issue.
2. Create a feature branch from `main`.
3. Implement the required change.
4. Make meaningful commits using the commit convention.
5. Push the branch to GitHub.
6. Open a pull request.
7. Link the pull request to the relevant issue.
8. Get at least one review approval.
9. Merge the pull request into `main`.
10. Delete the feature branch.
11. Close the related issue.