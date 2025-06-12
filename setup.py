from setuptools import setup, find_packages

setup(
    name="stream_views",
    version="0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "nicegui>=1.4.0",
        "google-api-python-client>=2.0.0",
        "python-dotenv>=1.0.0",
        "pandas>=1.3.0",
        "numpy>=1.21.0",
        "pydantic>=2.0.0",
        "SQLAlchemy>=2.0.0",
        "python-dateutil>=2.8.0",
        "psutil>=5.9.0"
    ],
    python_requires=">=3.8",
) 