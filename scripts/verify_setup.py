"""
Verify PropBot project setup
"""

import os
import sys
from pathlib import Path

def verify_structure():
    """Check all folders exist"""
    
    required_folders = [
        'data/raw',
        'data/processed',
        'scripts',
        'airflow/dags',
        'database',
        'app',
        'tests',
        'evaluation',
        'logs'
    ]
    
    print("=" * 70)
    print("CHECKING PROJECT STRUCTURE")
    print("=" * 70)
    
    all_exist = True
    
    for folder in required_folders:
        exists = Path(folder).exists()
        status = "ok" if exists else "no"
        print(f"{status} {folder}")
        
        if not exists:
            all_exist = False
    
    return all_exist

def verify_dependencies():
    """Check Python packages"""
    
    print("\n" + "=" * 70)
    print("CHECKING PYTHON DEPENDENCIES")
    print("=" * 70)
    
    packages = ['pandas', 'numpy', 'requests', 'tqdm', 'geopy', 'dotenv']
    
    all_installed = True
    
    for package in packages:
        try:
            __import__(package)
            print(f" {package}")
        except ImportError:
            print(f" {package} - NOT INSTALLED")
            all_installed = False
    
    return all_installed

def main():
    """Run all checks"""
    
    folders_ok = verify_structure()
    deps_ok = verify_dependencies()
    
    print("\n" + "=" * 70)
    
    if folders_ok and deps_ok:
        print(" PROJECT SETUP COMPLETE!")
        print("=" * 70)
        print("\n READY FOR DATA COLLECTION!")
        print("\nNext: Create your first data collection script")
        print("Run: python scripts\\collect_crime.py")
    else:
        print(" SETUP INCOMPLETE")
        print("Please fix issues above")
    
    print("=" * 70)

if __name__ == "__main__":
    main()