# Python wax library examples in UV pyproject

## First you need to install uv

```bash
# On macOS and Linux.
curl -LsSf https://astral.sh/uv/install.sh | sh
```

```powershell
# On Windows.
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

```bash
# Universal
pipx install uv
```

## Install the dependencies

```bash
uv sync --prerelease=allow --index-strategy=unsafe-best-match
```

## Move to the examples directory

```bash
cd src/examples
```

## Set the environment variables

```markdown
PASSWORD, WALLET_NAME, and HIVED_URL are optional - default values are used if not set
All variables: PASSWORD, WALLET_NAME, ACCOUNT_NAME, TRANSFER_RECEIVER, PRIVATE_KEY, PUBLIC_KEY, HIVED_ADDRESS
```

## Run the examples (create_and_sign_transaction.py in this case)

```bash
python3 create_and_sign_transaction.py
```
