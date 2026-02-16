#!/usr/bin/env python3
"""
Backend Factory V1 - CLI
Deterministic, fail-fast code generator
"""

import typer
import json
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich import print as rprint

from src.validators import validate_spec
from src.generators import BackendGenerator, OpenAPIGenerator, FrontendGenerator
from src.analyzer import DecompositionAdvisor
from src.models import SpecModel

app = typer.Typer(
    name="backend-factory",
    help="Deterministic Backend Code Generator V1",
    add_completion=False
)
console = Console()


@app.command()
def validate(
    spec_file: str = typer.Argument(..., help="Path to spec JSON file"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")
):
    """
    Validate spec file.
    Fail-fast on errors.
    """
    console.print(f"\n[bold cyan]Validating spec:[/bold cyan] {spec_file}")
    
    is_valid, result = validate_spec(spec_file)
    
    if result.errors:
        console.print("\n[bold red]❌ Validation FAILED[/bold red]\n")
        for error in result.errors:
            console.print(f"  [red]✗[/red] {error}")
        raise typer.Exit(code=1)
    
    console.print("\n[bold green]✓ Validation PASSED[/bold green]\n")
    
    if result.warnings:
        console.print("[bold yellow]Warnings:[/bold yellow]")
        for warning in result.warnings:
            console.print(f"  [yellow]⚠[/yellow] {warning}")
    
    if verbose:
        console.print(f"\n[bold]Spec version:[/bold] {result.spec.spec_version}")
        console.print(f"[bold]Project:[/bold] {result.spec.project.name}")
        console.print(f"[bold]Modules:[/bold] {len(result.spec.modules)}")
    
    console.print("\n[green]✓[/green] Spec is valid and ready for code generation\n")


@app.command()
def generate(
    spec_file: str = typer.Argument(..., help="Path to spec JSON file"),
    output: str = typer.Option("./output", "--output", "-o", help="Output directory"),
    backend: str = typer.Option(
        "spring-boot",
        "--backend",
        "-b",
        help="Backend type: spring-boot | python"
    ),
    frontend: str = typer.Option(
        None,
        "--frontend",
        "-fe",
        help="Frontend type: react"
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing files")
):
    """
    Generate backend code from spec.
    Validates spec first (fail-fast).
    """
    console.print(f"\n[bold cyan]Backend Factory - Code Generation[/bold cyan]\n")
    console.print(f"Spec file: {spec_file}")
    console.print(f"Backend type: {backend}")
    console.print(f"Output directory: {output}\n")
    
    # Step 1: Validate
    console.print("[bold]Step 1:[/bold] Validating spec...")
    is_valid, result = validate_spec(spec_file)
    
    if not is_valid:
        console.print("\n[bold red]❌ Validation FAILED - Aborting[/bold red]\n")
        for error in result.errors:
            console.print(f"  [red]✗[/red] {error}")
        raise typer.Exit(code=1)
    
    console.print("[green]✓[/green] Validation passed")
    
    # Step 2: Check output directory
    output_path = Path(output)
    if output_path.exists() and not force:
        if not typer.confirm(
            f"\nOutput directory '{output}' exists. Overwrite?",
            default=False
        ):
            console.print("[yellow]Generation cancelled[/yellow]")
            raise typer.Exit(code=0)
    
    # Step 3: Generate code
    try:
        if backend:
            console.print(f"\n[bold]Step 2:[/bold] Generating {backend} backend code...")
            generator = BackendGenerator(backend_type=backend)
            generator.generate(result.spec, output)
            console.print(f"[green]✓[/green] Backend code generated in: {output}")
        
        if frontend:
            fe_output = Path(output) / "frontend"
            console.print(f"\n[bold]Step 3:[/bold] Generating {frontend} frontend code...")
            fe_generator = FrontendGenerator(frontend_type=frontend)
            fe_generator.generate(result.spec, str(fe_output))
            console.print(f"[green]✓[/green] Frontend code generated in: {fe_output}")
            
    except Exception as e:
        console.print(f"\n[bold red]❌ Generation failed:[/bold red] {str(e)}")
        import traceback
        if console.is_terminal:
            console.print(traceback.format_exc())
        raise typer.Exit(code=1)
    
    console.print(f"\n[bold green]✓ Generation completed successfully[/bold green]\n")


@app.command()
def openapi(
    spec_file: str = typer.Argument(..., help="Path to spec JSON file"),
    output: str = typer.Option(
        "./openapi.yaml",
        "--output",
        "-o",
        help="Output file path"
    ),
    format: str = typer.Option(
        "yaml",
        "--format",
        "-f",
        help="Output format: yaml | json"
    )
):
    """
    Generate OpenAPI 3.0 contract from spec.
    """
    console.print(f"\n[bold cyan]Generating OpenAPI contract[/bold cyan]\n")
    
    # Validate first
    is_valid, result = validate_spec(spec_file)
    
    if not is_valid:
        console.print("\n[bold red]❌ Validation FAILED[/bold red]\n")
        for error in result.errors:
            console.print(f"  [red]✗[/red] {error}")
        raise typer.Exit(code=1)
    
    # Generate OpenAPI
    try:
        openapi_doc = OpenAPIGenerator.generate(result.spec)
        
        if format == "yaml":
            OpenAPIGenerator.save_yaml(openapi_doc, output)
        else:
            OpenAPIGenerator.save_json(openapi_doc, output)
        
        console.print(f"[green]✓[/green] OpenAPI contract generated: {output}\n")
    except Exception as e:
        console.print(f"\n[bold red]❌ Generation failed:[/bold red] {str(e)}")
        raise typer.Exit(code=1)


@app.command()
def analyze(
    spec_file: str = typer.Argument(..., help="Path to spec JSON file"),
    output: str = typer.Option(None, "--output", "-o", help="Save report to file")
):
    """
    Analyze spec and generate decomposition advisory report.
    """
    console.print(f"\n[bold cyan]Decomposition Analysis[/bold cyan]\n")
    
    # Validate first
    is_valid, result = validate_spec(spec_file)
    
    if not is_valid:
        console.print("\n[bold red]❌ Validation FAILED[/bold red]\n")
        for error in result.errors:
            console.print(f"  [red]✗[/red] {error}")
        raise typer.Exit(code=1)
    
    # Analyze
    advisor = DecompositionAdvisor()
    report = advisor.analyze(result.spec)
    
    # Display report
    console.print(f"[bold]Policy:[/bold] {report.policy.value}")
    console.print(f"[bold]Complexity Score:[/bold] {report.complexity_score}/100")
    console.print(f"[bold]Recommendation:[/bold] {report.recommendation}\n")
    
    console.print("[bold]Reasoning:[/bold]")
    for reason in report.reasoning:
        console.print(f"  • {reason}")
    
    if report.candidates:
        console.print(f"\n[bold]Microservice Candidates ({len(report.candidates)}):[/bold]")
        
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Module", style="cyan")
        table.add_column("Entities", justify="right")
        table.add_column("Endpoints", justify="right")
        table.add_column("Rationale")
        
        for candidate in report.candidates:
            table.add_row(
                candidate["module_name"],
                str(candidate["entity_count"]),
                str(candidate["endpoint_count"]),
                candidate["rationale"]
            )
        
        console.print(table)
    
    # Display metrics
    console.print("\n[bold]Metrics:[/bold]")
    for key, value in report.metrics.items():
        console.print(f"  {key}: {value}")
    
    # Save to file if requested
    if output:
        with open(output, 'w') as f:
            json.dump(report.to_dict(), f, indent=2)
        console.print(f"\n[green]✓[/green] Report saved: {output}")
    
    console.print()


@app.command()
def version():
    """Show version information"""
    from src import __version__
    console.print(f"\n[bold]Backend Factory V1[/bold]")
    console.print(f"Version: {__version__}")
    console.print("Deterministic Backend Code Generator\n")


if __name__ == "__main__":
    app()
