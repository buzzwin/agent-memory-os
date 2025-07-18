#!/usr/bin/env python3
"""
Comprehensive Test Runner for Agent Memory OS

This script runs all test suites and generates detailed reports for PyPI readiness.
"""

import os
import sys
import subprocess
import time
import json
from datetime import datetime
from pathlib import Path


class TestRunner:
    """Comprehensive test runner for Agent Memory OS"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.test_results = {}
        self.start_time = time.time()
        
    def run_command(self, command, description):
        """Run a command and capture results"""
        print(f"\n🔧 {description}")
        print("-" * 50)
        
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            success = result.returncode == 0
            print(f"Status: {'✅ PASSED' if success else '❌ FAILED'}")
            
            if result.stdout:
                print("Output:")
                print(result.stdout)
            
            if result.stderr:
                print("Errors:")
                print(result.stderr)
            
            return {
                'success': success,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            return {
                'success': False,
                'returncode': -1,
                'stdout': '',
                'stderr': str(e)
            }
    
    def run_unit_tests(self):
        """Run unit tests"""
        return self.run_command(
            [sys.executable, "-m", "pytest", "tests/test_memory.py", "-v"],
            "Running Unit Tests"
        )
    
    def run_regression_tests(self):
        """Run regression tests"""
        return self.run_command(
            [sys.executable, "-m", "pytest", "tests/test_regression.py", "-v"],
            "Running Regression Tests"
        )
    
    def run_integration_tests(self):
        """Run integration tests"""
        return self.run_command(
            [sys.executable, "-m", "pytest", "tests/test_integrations.py", "-v"],
            "Running Integration Tests"
        )
    
    def run_all_tests(self):
        """Run all tests"""
        return self.run_command(
            [sys.executable, "-m", "pytest", "tests/", "-v"],
            "Running All Tests"
        )
    
    def check_imports(self):
        """Check that all modules can be imported"""
        print("\n📦 Checking Module Imports")
        print("-" * 50)
        
        import_checks = {
            'Core SDK': [
                'agent_memory_sdk',
                'agent_memory_sdk.memory',
                'agent_memory_sdk.models',
                'agent_memory_sdk.store.base_store',
                'agent_memory_sdk.store.sqlite_store',
                'agent_memory_sdk.store.store_factory',
                'agent_memory_sdk.utils.embedding_utils',
                'agent_memory_sdk.utils.time_utils'
            ],
            'LangChain Integration': [
                'agent_memory_sdk.integrations.langchain.memory_chain',
                'agent_memory_sdk.integrations.langchain.memory_tool',
                'agent_memory_sdk.integrations.langchain.memory_callback',
                'agent_memory_sdk.integrations.langchain.memory_agent'
            ],
            'LangGraph Integration': [
                'agent_memory_sdk.integrations.langgraph.memory_graph',
                'agent_memory_sdk.integrations.langgraph.memory_state',
                'agent_memory_sdk.integrations.langgraph.memory_node',
                'agent_memory_sdk.integrations.langgraph.memory_tool_node'
            ],
            'REST API': [
                'agent_memory_sdk.api.server',
                'agent_memory_sdk.api.client',
                'agent_memory_sdk.api.models'
            ],
            'Storage Backends': [
                'agent_memory_sdk.store.pinecone_store',
                'agent_memory_sdk.store.postgresql_store'
            ]
        }
        
        results = {}
        all_success = True
        
        for category, modules in import_checks.items():
            print(f"\n{category}:")
            category_success = True
            
            for module in modules:
                try:
                    __import__(module)
                    print(f"  ✅ {module}")
                except ImportError as e:
                    print(f"  ❌ {module}: {e}")
                    category_success = False
                    all_success = False
            
            results[category] = category_success
        
        return {
            'success': all_success,
            'results': results
        }
    
    def check_dependencies(self):
        """Check that all dependencies are available"""
        print("\n📋 Checking Dependencies")
        print("-" * 50)
        
        dependencies = {
            'Core': ['pydantic', 'sqlite3'],
            'Optional': ['pinecone', 'psycopg2-binary', 'fastapi', 'uvicorn'],
            'Testing': ['pytest', 'pytest-asyncio'],
            'LangChain': ['langchain', 'langchain-community', 'langchain-core'],
            'LangGraph': ['langgraph']
        }
        
        results = {}
        all_available = True
        
        for category, deps in dependencies.items():
            print(f"\n{category}:")
            category_available = True
            
            for dep in deps:
                try:
                    __import__(dep.replace('-', '_'))
                    print(f"  ✅ {dep}")
                except ImportError:
                    print(f"  ❌ {dep} (not installed)")
                    category_available = False
                    if category != 'Optional':
                        all_available = False
            
            results[category] = category_available
        
        return {
            'success': all_available,
            'results': results
        }
    
    def check_file_structure(self):
        """Check that all required files exist"""
        print("\n📁 Checking File Structure")
        print("-" * 50)
        
        required_files = [
            'setup.py',
            'requirements.txt',
            'README.md',
            'LICENSE',
            'agent_memory_sdk/__init__.py',
            'agent_memory_sdk/memory.py',
            'agent_memory_sdk/models.py',
            'agent_memory_sdk/store/__init__.py',
            'agent_memory_sdk/store/base_store.py',
            'agent_memory_sdk/store/sqlite_store.py',
            'agent_memory_sdk/store/store_factory.py',
            'tests/__init__.py',
            'tests/test_memory.py',
            'tests/test_regression.py',
            'tests/test_integrations.py'
        ]
        
        results = {}
        all_exist = True
        
        for file_path in required_files:
            full_path = self.project_root / file_path
            exists = full_path.exists()
            results[file_path] = exists
            
            status = "✅" if exists else "❌"
            print(f"{status} {file_path}")
            
            if not exists:
                all_exist = False
        
        return {
            'success': all_exist,
            'results': results
        }
    
    def run_demo_tests(self):
        """Run demo scripts to ensure they work"""
        print("\n🎯 Running Demo Tests")
        print("-" * 50)
        
        demos = [
            ('Core Memory Demo', 'examples/crewai_memory_demo.py'),
            ('LangChain Demo', 'examples/langchain_memory_demo.py'),
            ('LangGraph Demo', 'examples/langgraph_memory_demo.py'),
            ('API Demo', 'examples/api_demo.py')
        ]
        
        results = {}
        all_success = True
        
        for name, script in demos:
            script_path = self.project_root / script
            if script_path.exists():
                result = self.run_command(
                    [sys.executable, str(script_path)],
                    f"Running {name}"
                )
                results[name] = result
                if not result['success']:
                    all_success = False
            else:
                print(f"⚠️  {name}: Script not found ({script})")
                results[name] = {'success': False, 'error': 'Script not found'}
                all_success = False
        
        return {
            'success': all_success,
            'results': results
        }
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 80)
        print("📊 AGENT MEMORY OS - COMPREHENSIVE TEST REPORT")
        print("=" * 80)
        
        end_time = time.time()
        duration = end_time - self.start_time
        
        # Summary
        print(f"\n⏱️  Test Duration: {duration:.2f} seconds")
        print(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Test Results Summary
        print("\n📈 Test Results Summary:")
        print("-" * 40)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result.get('success', False))
        
        print(f"Total Test Categories: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%" if total_tests > 0 else "N/A")
        
        # Detailed Results
        print("\n📋 Detailed Results:")
        print("-" * 40)
        
        for test_name, result in self.test_results.items():
            status = "✅ PASSED" if result.get('success', False) else "❌ FAILED"
            print(f"{test_name}: {status}")
            
            if not result.get('success', False) and result.get('stderr'):
                print(f"  Error: {result['stderr'][:100]}...")
        
        # PyPI Readiness Assessment
        print("\n🚀 PyPI Readiness Assessment:")
        print("-" * 40)
        
        critical_tests = [
            'File Structure Check',
            'Module Imports Check',
            'Unit Tests',
            'Regression Tests'
        ]
        
        critical_passed = all(
            self.test_results.get(test, {}).get('success', False)
            for test in critical_tests
        )
        
        if critical_passed:
            print("✅ READY FOR PyPI DISTRIBUTION")
            print("   All critical tests passed")
        else:
            print("❌ NOT READY FOR PyPI DISTRIBUTION")
            print("   Some critical tests failed")
            
            failed_critical = [
                test for test in critical_tests
                if not self.test_results.get(test, {}).get('success', False)
            ]
            print(f"   Failed critical tests: {', '.join(failed_critical)}")
        
        # Recommendations
        print("\n💡 Recommendations:")
        print("-" * 40)
        
        if not critical_passed:
            print("🔧 Fix critical test failures before PyPI distribution")
        
        optional_tests = [
            'Integration Tests',
            'Dependencies Check',
            'Demo Tests'
        ]
        
        optional_failures = [
            test for test in optional_tests
            if not self.test_results.get(test, {}).get('success', False)
        ]
        
        if optional_failures:
            print("⚠️  Consider fixing optional test failures for better user experience")
            for test in optional_failures:
                print(f"   - {test}")
        
        if critical_passed and not optional_failures:
            print("🎉 Package is in excellent condition for PyPI distribution!")
        
        return critical_passed
    
    def run_all_checks(self):
        """Run all checks and tests"""
        print("🧪 AGENT MEMORY OS - COMPREHENSIVE TEST SUITE")
        print("=" * 60)
        print(f"Project Root: {self.project_root}")
        print(f"Python Version: {sys.version}")
        
        # Run all checks
        self.test_results['File Structure Check'] = self.check_file_structure()
        self.test_results['Module Imports Check'] = self.check_imports()
        self.test_results['Dependencies Check'] = self.check_dependencies()
        self.test_results['Unit Tests'] = self.run_unit_tests()
        self.test_results['Regression Tests'] = self.run_regression_tests()
        self.test_results['Integration Tests'] = self.run_integration_tests()
        self.test_results['Demo Tests'] = self.run_demo_tests()
        
        # Generate final report
        pypi_ready = self.generate_report()
        
        return pypi_ready


def main():
    """Main entry point"""
    runner = TestRunner()
    
    try:
        pypi_ready = runner.run_all_checks()
        
        if pypi_ready:
            print("\n🎉 SUCCESS: Package is ready for PyPI distribution!")
            sys.exit(0)
        else:
            print("\n❌ FAILURE: Package is not ready for PyPI distribution.")
            print("Please fix the issues above before proceeding.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Test run interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 