import click
import requests
import os
import subprocess
import json
from safety import backup_file
from diff_match_patch import diff_match_patch

# --- Configuration ---
# In a real app, this would come from a shared config loader
BACKEND_URL = 'http://localhost:8000'

def get_code_from_file(file_path, start_line, end_line):
    """Extracts specific lines of code from a file."""
    if not os.path.exists(file_path):
        click.echo(f"Error: File not found at {file_path}", err=True)
        return None
    with open(file_path, 'r') as f:
        lines = f.readlines()

    if start_line and end_line:
        # Adjust for 0-based indexing and inclusive end line
        return ''.join(lines[start_line-1:end_line])
    return ''.join(lines)

def apply_patch_to_file(file_path, patch_text):
    """Applies a diff patch to a file using diff-match-patch."""
    if not patch_text:
        click.echo("No changes to apply.")
        return

    dmp = diff_match_patch()
    original_content = open(file_path, 'r').read()
    patches = dmp.patch_fromText(patch_text)

    new_content, results = dmp.patch_apply(patches, original_content)

    # Check if all patches were applied successfully
    if all(results):
        with open(file_path, 'w') as f:
            f.write(new_content)
        click.echo(f"Successfully patched {file_path}.")
    else:
        click.echo("Failed to apply patch automatically. Please review the diff manually.", err=True)

@click.group()
def cli():
    """A CLI for the Termux AI Coding Agent."""
    pass

@cli.command()
@click.argument('prompt')
@click.option('--code', help='Direct code snippet to process.')
@click.option('--file', help='Path to the file to process.')
@click.option('--line-start', type=int, help='Start line of the code selection.')
@click.option('--line-end', type=int, help='End line of the code selection.')
@click.option('--dry-run', is_flag=True, help="Simulate changes without applying them.")
def refactor(prompt, code, file, line_start, line_end, dry_run):
    """Refactor code with AI assistance."""
    click.echo("Refactoring code...")

    if file:
        code = get_code_from_file(file, line_start, line_end)
        if code is None: return

    context = subprocess.run(['ls', '-R'], capture_output=True, text=True).stdout

    try:
        response = requests.post(f'{BACKEND_URL}/api/chat', json={
            'code': code,
            'context': context,
            'prompt': prompt,
            'session_id': 'termux_cli_session'
        })
        response.raise_for_status()
        data = response.json()

        click.echo("\n--- AI Analysis ---")
        click.echo(f"Analysis: {data.get('analysis')}")
        click.echo(f"Decision: {data.get('decision')}")

        click.echo("\n--- Suggested Code ---")
        click.echo(data.get('code'))

        click.echo("\n--- Diff ---")
        click.echo(data.get('diff'))

        if not dry_run and file and data.get('diff'):
            if click.confirm('Do you want to apply these changes?'):
                backup_file(file)
                apply_patch_to_file(file, data['diff'])
        elif dry_run:
            click.echo("\nDry run mode: No changes were applied.")

    except requests.exceptions.RequestException as e:
        click.echo(f"Error connecting to backend: {e}", err=True)

@cli.command()
def self_update():
    """Updates the agent by pulling the latest changes from git."""
    click.echo("Pulling latest changes from git...")
    result = subprocess.run(['git', 'pull'], capture_output=True, text=True)
    if result.returncode == 0:
        click.echo("Update successful!")
        click.echo(result.stdout)
        click.echo("\nRe-installing dependencies...")
        subprocess.run(['pip', 'install', '-r', 'requirements.txt'])
    else:
        click.echo("Failed to update.", err=True)
        click.echo(result.stderr, err=True)

if __name__ == '__main__':
    cli()
