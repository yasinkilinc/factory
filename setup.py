from setuptools import setup, find_packages

setup(
    name="backend-factory",
    version="1.0.0",
    description="Deterministic Backend Code Generator",
    author="Backend Factory Team",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.5.0",
        "typer>=0.9.0",
        "jinja2>=3.1.2",
        "pyyaml>=6.0.1",
        "jsonschema>=4.20.0",
        "rich>=13.7.0",
    ],
    entry_points={
        "console_scripts": [
            "backend-factory=cli:app",
        ],
    },
    python_requires=">=3.11",
)
