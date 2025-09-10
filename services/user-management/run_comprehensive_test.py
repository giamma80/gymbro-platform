#!/usr/bin/env python3
"""
Semplice script per eseguire il test completo e mostrare i risultati
"""

import subprocess
import sys
import os

def main():
    # Cambia nella directory corretta
    os.chdir("/Users/giamma/workspace/gymbro-platform/services/user-management")
    
    try:
        # Esegue il test completo con poetry
        result = subprocess.run(
            ["poetry", "run", "python", "comprehensive_test_suite.py"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print("=== STDOUT ===")
        print(result.stdout)
        
        if result.stderr:
            print("\n=== STDERR ===")
            print(result.stderr)
        
        print(f"\n=== EXIT CODE: {result.returncode} ===")
        
    except subprocess.TimeoutExpired:
        print("Test timeout dopo 30 secondi")
    except Exception as e:
        print(f"Errore nell'esecuzione: {e}")

if __name__ == "__main__":
    main()
