# Copilot Instructions: Branching and PR Workflow

When working in this repository, you must strictly adhere to the following branching and Pull
Request workflow:

## 1. Branching Strategy

- **Never commit directly to the `main` branch.**
- Always create a new branch for any changes, features, or bug fixes.
- Use descriptive branch names following this convention:
  - `feature/<short-description>` for new features or projects.
  - `fix/<short-description>` for bug fixes.
  - `docs/<short-description>` for documentation updates.
  - `chore/<short-description>` for maintenance tasks (e.g., linting, CI updates).

## 2. Committing Changes

- Write clear, concise, and descriptive commit messages.
- Use the imperative mood in the subject line (e.g., "Add project tracking structure", not "Added"
  or "Adds").
- Group related changes into logical commits.

## 3. Pull Request Workflow

- Once changes are committed to your branch, push the branch to the remote repository.
- Create a Pull Request (PR) targeting the `main` branch.
- The PR title should clearly summarize the changes.
- The PR description must include:
  - A summary of the changes made.
  - The motivation or context for the changes.
  - Any relevant issue numbers or project references.
- Ensure all CI checks (linting, formatting) pass before requesting a review or merging.
- Do not merge your own PR without approval (if branch protection rules are in place).

## 4. Project Tracking Structure

- Projects are tracked within their respective category folders (e.g., `01-audio-midi/`).
- Project files must be placed directly in the category folder (no `projects/` subfolder).
- Project files must be named using a category prefix, a project number, and a slug (e.g.,
  `01-001-midi-controller.md`).
- The main `projects.md` file in each category serves as an index/dashboard linking to the
  individual project files.
- Use Markdown and YAML frontmatter for structured data within project files.
- Every project file MUST include an `## Exit Criteria` section with checkboxes defining what "done"
  looks like.
- These design choices are **MUST DO** when making agentic changes to this rep

### Supporting documentation & assets

The flat `NN-NNN-slug.md` file stays the single canonical entry for each project. Two optional
affordances exist for when a project or category accumulates real documentation:

- **Optional per-project folder:** a project may add a sibling folder `NN-NNN-slug/` next to its
  canonical file to hold as-built notes, photos, datasheets, or research digests.
- **Per-category `_reference/`:** shared or reference material not tied to a single project goes in
  a `_reference/` folder inside the category (e.g. `06-coffee-espresso/_reference/leva/`).
- Folders whose names start with `_`, and the optional per-project folders, are **not projects**:
  the invariant checker only counts flat `NN-NNN-*.md` files directly in each category folder, so
  these never affect project counts.
- Do not commit bulk third-party content (e.g. verbatim forum scrapes, vendor PDFs) to this
  **public** repo — keep those on local/NAS storage and link to them; commit only original
  synthesis.

## 5. Branch Protection

The "never commit to `main`" rule is backed by:

- `.github/CODEOWNERS` — every path requires review from `@gjcourt`.
- The `main` branch should be configured (in GitHub repository settings → Branches → Branch
  protection rules) with:
  - Require a pull request before merging.
  - Require approvals: 1.
  - Require review from Code Owners.
  - Require status checks to pass before merging:
    - `lint-and-format` (the CI job in `.github/workflows/ci.yml`).
  - Require branches to be up to date before merging.
  - Do not allow bypassing the above settings.
- The CI job runs `make check-invariants`, which fails if any project file is missing required
  frontmatter keys, an `## Exit Criteria` section, or if README/projects.md counts disagree with the
  actual file count.
