#!/usr/bin/env python3
"""
Build script for creating desktop application EXE files
Usage: python build_all.py
"""

import os
import subprocess
import sys
from pathlib import Path

from build_config import applications, common_options


def build_application(app_name, config):
    """Build a single application EXE"""
    print(f"\n{'='*60}")
    print(f"Building {config['name']}.exe...")
    print(f"{'='*60}")
    
    # PyInstaller command
    cmd = [
        'pyinstaller',
        '--name', config['name'],
        '--icon', config['icon'],
        '--onefile',
        '--windowed',
        '--add-data', 'resources:resources',
        '--hidden-import', 'PyQt5',
        '--hidden-import', 'requests',
        '--hidden-import', 'PIL',
        '--hidden-import', 'reportlab',
        '--hidden-import', 'dotenv',
        config['main_file']
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        print(f"✅ {config['name']}.exe built successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to build {config['name']}.exe")
        print(f"Error: {e}")
        return False


def build_all():
    """Build all applications"""
    print("\n" + "="*60)
    print("MSDC Hospital Desktop Applications Builder")
    print("="*60)
    
    # Check if PyInstaller is installed
    try:
        subprocess.run(['pyinstaller', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ PyInstaller not found. Install with: pip install pyinstaller")
        sys.exit(1)
    
    # Build each application
    results = {}
    for app_key, app_config in applications.items():
        results[app_key] = build_application(app_key, app_config)
    
    # Summary
    print("\n" + "="*60)
    print("BUILD SUMMARY")
    print("="*60)
    
    successful = sum(1 for v in results.values() if v)
    total = len(results)
    
    for app_key, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{applications[app_key]['name']:20} {status}")
    
    print(f"\nBuilt: {successful}/{total}")
    
    if successful == total:
        print("\n🎉 All applications built successfully!")
        print("\nExecutables are located in:")
        print(f"  dist/Admin.exe")
        print(f"  dist/Admission.exe")
        print(f"  dist/Reception.exe")
        print(f"  dist/Pharmacy.exe")
        print(f"  dist/Lab.exe")
        print(f"  dist/Clinic.exe")
        print(f"  dist/MedicalInventory.exe")
        print(f"  dist/Statistics.exe")
        print(f"\nDistribute these to each department workstation.")
    else:
        print(f"\n⚠️  {total - successful} application(s) failed to build.")
        sys.exit(1)


if __name__ == '__main__':
    build_all()
