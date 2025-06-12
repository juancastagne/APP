from setuptools import setup, find_packages

setup(
    name="stream_views",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "nicegui",
        "google-api-python-client",
        "python-dotenv",
    ],
) 