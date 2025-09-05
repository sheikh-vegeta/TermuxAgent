import click
import requests
import os
import subprocess

BACKEND_URL = 'http://localhost:8000'

@click.group()
def cli():
    """A CLI for the Termux AI Coding Agent."""
    pass

@cli.command()
@click.argument('prompt')
def refactor(prompt):
    """Sends a refactoring prompt to the agent."""
    click.echo(f"Sending refactor prompt: '{prompt}'")
    # In a real implementation, this would call the backend API.
    # response = requests.post(f"{BACKEND_URL}/api/refactor", json={'prompt': prompt})
    # click.echo(response.json())
    click.echo("This is a placeholder for the refactor command.")


@cli.command()
def self_update():
    """Updates the agent by pulling the latest changes from git."""
    click.echo("Updating agent by pulling from git...")
    subprocess.run(['git', 'pull'])
    click.echo("Re-installing dependencies...")
    subprocess.run(['pip', 'install', '-r', 'requirements.txt'])
    click.echo("Update complete.")

if __name__ == "__main__":
    cli()
