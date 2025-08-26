# Create this as setup.py for package distribution
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ab-testing-framework",
    version="1.0.0",
    author="LoyaNg",
    author_email="loyanganba.ngathem@gmail.com",
    description="A comprehensive Python framework for A/B testing analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/LoyaNg-rgb/ab-testing-framework",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Office/Business :: Financial :: Investment",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.0.0",
            "black>=21.0.0",
            "flake8>=3.9.0",
            "mypy>=0.910",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=0.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ab-test=ab_test_analyzer:main",
        ],
    },
)

# ==================================================
# Additional files to create in your repository:
# ==================================================

### .gitignore
"""
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
.python-version

# pipenv
Pipfile.lock

# PEP 582
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# Data files
*.csv
*.json
*.xlsx
*.parquet

# Output files
results/
plots/
reports/

# IDE
.vscode/
.idea/
*.swp
*.swo

# macOS
.DS_Store
"""

### LICENSE (MIT License)
"""
MIT License

Copyright (c) 2024 

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

### tests/test_analyzer.py
"""
import pytest
import pandas as pd
import numpy as np
import sys
import os

# Add parent directory to path to import the analyzer
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ab_test_analyzer import ABTestAnalyzer
from data.data_generator import generate_sample_ab_test_data

class TestABTestAnalyzer:
    
    @pytest.fixture
    def sample_data(self):
        '''Generate sample data for testing'''
        ab_test_df, countries_df = generate_sample_ab_test_data(n_users=1000, seed=42)
        
        # Save to temporary files
        ab_test_df.to_csv('test_ab.csv', index=False)
        countries_df.to_csv('test_countries.csv', index=False)
        
        yield 'test_ab.csv', 'test_countries.csv'
        
        # Cleanup
        os.remove('test_ab.csv')
        os.remove('test_countries.csv')
    
    def test_initialization(self, sample_data):
        '''Test analyzer initialization'''
        ab_file, countries_file = sample_data
        analyzer = ABTestAnalyzer(ab_file, countries_file)
        
        assert analyzer is not None
        assert len(analyzer.data) > 0
        assert 'con_treat' in analyzer.data.columns
        assert 'converted' in analyzer.data.columns
        assert 'country' in analyzer.data.columns
    
    def test_power_analysis(self, sample_data):
        '''Test power analysis calculation'''
        ab_file, countries_file = sample_data
        analyzer = ABTestAnalyzer(ab_file, countries_file)
        
        power = analyzer.power_analysis()
        
        assert isinstance(power, float)
        assert 0 <= power <= 1
    
    def test_statistical_tests(self, sample_data):
        '''Test statistical analysis'''
        ab_file, countries_file = sample_data
        analyzer = ABTestAnalyzer(ab_file, countries_file)
        
        results = analyzer.statistical_tests()
        
        assert 'overall' in results
        assert 'control_rate' in results['overall']
        assert 'treatment_rate' in results['overall']
        assert 'p_value' in results['overall']
        assert 'significant' in results['overall']
    
    def test_data_validation(self, sample_data):
        '''Test data quality checks'''
        ab_file, countries_file = sample_data
        analyzer = ABTestAnalyzer(ab_file, countries_file)
        
        # Check that data validation ran without errors
        assert hasattr(analyzer, 'data')
        assert len(analyzer.data) > 0
        
        # Check treatment assignment
        treatment_counts = analyzer.data['con_treat'].value_counts()
        assert 'control' in treatment_counts.index
        assert 'treatment' in treatment_counts.index

if __name__ == '__main__':
    pytest.main([__file__])
"""

### examples/basic_usage.py
"""
#!/usr/bin/env python3

'''
Basic usage example of the A/B Testing Framework

This script demonstrates the simplest way to use the framework
for analyzing A/B test results.
'''

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ab_test_analyzer import ABTestAnalyzer
from data.data_generator import generate_sample_ab_test_data, save_sample_data

def main():
    print("A/B Testing Framework - Basic Usage Example")
    print("=" * 50)
    
    # Step 1: Generate sample data (in real usage, you'd have your own CSV files)
    print("\\n1. Generating sample data...")
    ab_test_df, countries_df = generate_sample_ab_test_data(n_users=10000)
    save_sample_data(ab_test_df, countries_df, 'example_ab_test.csv', 'example_countries.csv')
    
    # Step 2: Initialize analyzer
    print("\\n2. Initializing analyzer...")
    analyzer = ABTestAnalyzer('example_ab_test.csv', 'example_countries.csv')
    
    # Step 3: Run complete analysis
    print("\\n3. Running analysis...")
    print("\\nExploratory Analysis:")
    analyzer.exploratory_analysis()
    
    print("\\nPower Analysis:")
    power = analyzer.power_analysis()
    
    print("\\nStatistical Tests:")
    results = analyzer.statistical_tests()
    
    print("\\nResults Visualization:")
    analyzer.create_results_visualization(results)
    
    print("\\nBusiness Recommendations:")
    analyzer.business_recommendations(results)
    
    # Cleanup
    os.remove('example_ab_test.csv')
    os.remove('example_countries.csv')
    
    print("\\n" + "=" * 50)
    print("Analysis complete! Check the generated plots and recommendations above.")

if __name__ == "__main__":
    main()
"""
