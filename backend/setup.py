"""
Setup script for Orbital Traffic Analyzer Backend
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="orbital-traffic-analyzer",
    version="1.0.0",
    author="Orbital Traffic Analyzer Contributors",
    description="Backend API for real-time satellite tracking and orbital congestion analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/orbital-traffic-analyzer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Astronomy",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.11",
    install_requires=[
        "fastapi>=0.104.1",
        "uvicorn>=0.24.0",
        "sqlalchemy>=2.0.23",
        "psycopg2-binary>=2.9.9",
        "redis>=5.0.1",
        "skyfield>=1.46",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
        "apscheduler>=3.10.4",
        "pydantic>=2.5.0",
        "numpy>=1.26.2",
    ],
)

