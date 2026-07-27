# Install and use the Neto Ecommerce API skill

This skill gives Codex a reusable workflow for building, reviewing, debugging, and safely executing Neto by Maropost Commerce Cloud product and content integrations. Installing it does not connect to a Neto store or execute API requests by itself.

## Supported operations

- Products: `GetItem`, `AddItem`, `UpdateItem`
- Content and CMS category pages: `GetContent`, `AddContent`, `UpdateContent`

Orders, customers, shipping, standalone category endpoints, and Maropost Marketing Cloud APIs are outside this skill's scope.

## Requirements

- Codex desktop app, Codex CLI, or the Codex IDE extension
- Git or a downloaded copy of this repository
- Python 3 when using the optional payload validator
- A Neto store domain, staff username, and user-based API key only when working with a live store

## Install for one repository

Use a repository-scoped installation when the skill should be available only to one project or shared with that project's team.

From this repository's checkout, copy the skill files into:

```text
<target-repository>/.agents/skills/neto-ecommerce-api/
```

The installed directory must contain `SKILL.md` at its root:

```text
<target-repository>/
└── .agents/
    └── skills/
        └── neto-ecommerce-api/
            ├── SKILL.md
            ├── agents/
            ├── assets/
            ├── references/
            └── scripts/
```

Run this PowerShell example from the skill repository:

```powershell
$skillTarget = "<target-repository>\.agents\skills\neto-ecommerce-api"
New-Item -ItemType Directory -Force $skillTarget | Out-Null
Copy-Item SKILL.md, agents, assets, references, scripts -Destination $skillTarget -Recurse -Force
```

On macOS or Linux:

```bash
skill_target="<target-repository>/.agents/skills/neto-ecommerce-api"
mkdir -p "$skill_target"
cp -R SKILL.md agents assets references scripts "$skill_target/"
```

## Install for your user account

Use a user-scoped installation when the skill should be available in every repository.

On Windows PowerShell, run these commands from the skill repository:

```powershell
$skillTarget = "$env:USERPROFILE\.agents\skills\neto-ecommerce-api"
New-Item -ItemType Directory -Force $skillTarget | Out-Null
Copy-Item SKILL.md, agents, assets, references, scripts -Destination $skillTarget -Recurse -Force
```

On macOS or Linux:

```bash
skill_target="$HOME/.agents/skills/neto-ecommerce-api"
mkdir -p "$skill_target"
cp -R SKILL.md agents assets references scripts "$skill_target/"
```

Codex normally detects skill changes automatically. If the skill does not appear, restart Codex.

## Verify the installation

- In the Codex desktop app, open **Skills** in the sidebar and find **Neto Ecommerce API**.
- In Codex CLI or the IDE extension, run `/skills` and find `neto-ecommerce-api`.
- Start a task with an explicit skill mention:

```text
Use $neto-ecommerce-api to explain the headers required for GetItem.
```

Codex can also select the skill automatically when a task clearly matches its description.

## Use the skill

Describe the Neto outcome and relevant repository context. Explicit invocation is recommended for important integration work.

Build a client:

```text
Use $neto-ecommerce-api to add a typed Neto client to this project and implement paginated GetItem syncing.
```

Review a mutation:

```text
Use $neto-ecommerce-api to review this UpdateItem stock payload for retry, idempotency, and deletion risks.
```

Work with CMS content:

```text
Use $neto-ecommerce-api to update the category named Gift Ideas by changing Description1 to the supplied HTML.
```

For content updates, identify the record with `ContentID` or an exact `ContentName`. `ContentURL` can be returned or updated but is not a supported `GetContent` lookup filter.

## Credentials and live API access

Use a user-based Neto API key with the minimum staff permissions required. Keep credentials in environment variables or the target project's secret manager; never place them in source code, logs, committed payloads, or prompts.

Live requests use HTTPS and these headers:

```text
NETOAPI_ACTION: <action>
NETOAPI_USERNAME: <staff username>
NETOAPI_KEY: <user-based API key>
Accept: application/json
Content-Type: application/json
```

The skill will not make a live mutation unless the task explicitly requests execution. Before a mutation, it should present a redacted dry-run payload unless immediate execution was explicitly requested.

## Validate request payloads

Run the validator from this repository or the installed skill directory:

```bash
python scripts/validate_neto_payload.py GetItem request.json
```

The validator checks the supported action envelope, required identifiers, pagination values, SKU length, and destructive nested updates.

Payloads containing `Delete: true` are blocked by default. Allow them only after confirming explicit deletion intent:

```bash
python scripts/validate_neto_payload.py UpdateItem request.json --allow-delete
```

## Update the installation

Pull or download the latest version of this repository, then repeat the copy command for the selected installation scope. Restart Codex only if the updated skill is not detected automatically.

For general Codex skill behavior and discovery locations, see [OpenAI's Build skills documentation](https://learn.chatgpt.com/docs/build-skills).
