#!/usr/bin/env python3
"""
Script principal pour exécuter tous les tests avec résultats clairs
"""

import sys
import os
import subprocess
import time
from pathlib import Path

def print_header(title):
    """Affiche un en-tête formaté"""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")

def print_result(success, test_name, details=""):
    """Affiche le résultat d'un test"""
    status = "✅ SUCCESS" if success else "❌ FAIL"
    print(f"{status}: {test_name}")
    if details:
        print(f"    {details}")

def run_python_test(test_file):
    """Exécute un test Python directement"""
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Test timeout after 30 seconds"
    except Exception as e:
        return False, "", str(e)

def run_pytest_command(test_path, markers=None):
    """Exécute pytest avec des marqueurs spécifiques"""
    cmd = [sys.executable, "-m", "pytest", test_path, "-v"]
    
    if markers:
        cmd.extend(["-m", markers])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Pytest timeout after 60 seconds"
    except Exception as e:
        return False, "", str(e)

def check_imports():
    """Vérifie que tous les modules peuvent être importés"""
    print_header("VÉRIFICATION DES IMPORTS")
    
    modules_to_test = [
        ("core.configuration_builder", "ConfigurationBuilder"),
        ("core.session_manager", "SessionManager"),
        ("core.dependency_container", "DependencyContainer"),
        ("core.agent_factory", "AgentFactory"),
    ]
    
    all_imports_ok = True
    
    for module_name, class_name in modules_to_test:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            print_result(True, f"Import {module_name}.{class_name}")
        except Exception as e:
            print_result(False, f"Import {module_name}.{class_name}", str(e))
            all_imports_ok = False
    
    return all_imports_ok

def run_unit_tests():
    """Exécute les tests unitaires"""
    print_header("TESTS UNITAIRES")
    
    unit_tests = [
        "tests/unit/test_configuration_builder.py",
        "tests/unit/test_session_manager.py", 
        "tests/unit/test_dependency_container.py",
    ]
    
    all_unit_ok = True
    
    for test_file in unit_tests:
        if os.path.exists(test_file):
            success, stdout, stderr = run_python_test(test_file)
            print_result(success, f"Test {test_file}")
            if not success and stderr:
                print(f"    Erreur: {stderr}")
            all_unit_ok = success and all_unit_ok
        else:
            print_result(False, f"Test {test_file}", "Fichier non trouvé")
            all_unit_ok = False
    
    return all_unit_ok

def run_error_handling_tests():
    """Exécute les tests de gestion d'erreur"""
    print_header("TESTS DE GESTION D'ERREUR")
    
    error_tests = [
        "tests/error_handling/test_configuration_errors.py",
        "tests/error_handling/test_connection_errors.py",
    ]
    
    all_error_ok = True
    
    for test_file in error_tests:
        if os.path.exists(test_file):
            success, stdout, stderr = run_python_test(test_file)
            print_result(success, f"Test {test_file}")
            if not success and stderr:
                print(f"    Erreur: {stderr}")
            all_error_ok = success and all_error_ok
        else:
            print_result(False, f"Test {test_file}", "Fichier non trouvé")
            all_error_ok = False
    
    return all_error_ok

def run_integration_tests():
    """Exécute les tests d'intégration avec pytest"""
    print_header("TESTS D'INTÉGRATION")
    
    try:
        success, stdout, stderr = run_pytest_command("tests/integration/", "integration")
        print_result(success, "Tests d'intégration pytest")
        if stdout:
            print("    Output pytest:")
            for line in stdout.split('\n')[-10:]:  # Dernières 10 lignes
                if line.strip():
                    print(f"    {line}")
        return success
    except Exception as e:
        print_result(False, "Tests d'intégration pytest", str(e))
        return False

def run_all_tests():
    """Exécute tous les tests"""
    print_header("EXÉCUTION COMPLÈTE DES TESTS")
    
    start_time = time.time()
    
    # 1. Vérification des imports
    imports_ok = check_imports()
    
    # 2. Tests unitaires
    unit_ok = run_unit_tests()
    
    # 3. Tests de gestion d'erreur
    error_ok = run_error_handling_tests()
    
    # 4. Tests d'intégration
    integration_ok = run_integration_tests()
    
    # Résumé final
    end_time = time.time()
    duration = end_time - start_time
    
    print_header("RÉSUMÉ FINAL")
    
    print(f"📊 Résultats:")
    print(f"   Imports: {'✅ OK' if imports_ok else '❌ ÉCHEC'}")
    print(f"   Tests unitaires: {'✅ OK' if unit_ok else '❌ ÉCHEC'}")
    print(f"   Gestion d'erreur: {'✅ OK' if error_ok else '❌ ÉCHEC'}")
    print(f"   Tests d'intégration: {'✅ OK' if integration_ok else '❌ ÉCHEC'}")
    print(f"   Durée totale: {duration:.2f}s")
    
    all_ok = imports_ok and unit_ok and error_ok and integration_ok
    
    if all_ok:
        print(f"\n🎉 TOUS LES TESTS RÉUSSIS !")
        return 0
    else:
        print(f"\n⚠️  CERTAINS TESTS ONT ÉCHOUÉ")
        print(f"   Consultez les logs ci-dessus pour les détails")
        return 1

def main():
    """Fonction principale"""
    print("🚀 SCRIPT DE TEST - SYSTÈME AGENT VOCAL")
    print(f"   Répertoire de travail: {os.getcwd()}")
    print(f"   Python: {sys.executable}")
    
    # Vérifier que nous sommes dans le bon répertoire
    if not os.path.exists("core"):
        print("❌ ERREUR: Ce script doit être exécuté depuis le répertoire worker/")
        print("   Usage: cd worker && python run_tests.py")
        return 1
    
    return run_all_tests()

if __name__ == "__main__":
    sys.exit(main())
