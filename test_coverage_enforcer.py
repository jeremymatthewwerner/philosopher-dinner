#!/usr/bin/env python3
"""
Test Coverage Enforcer
Automatically ensures new functionality has comprehensive test coverage
"""

import os
import sys
import ast
import subprocess
import json
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from datetime import datetime

class TestCoverageEnforcer:
    """Enforces comprehensive test coverage for new functionality"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.coverage_db_path = self.repo_path / "test_coverage_tracking.json"
        self.load_coverage_database()
        
        # Patterns for different types of functionality
        self.functionality_patterns = {
            "functions": r"def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(",
            "classes": r"class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[\(:]",
            "methods": r"def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(self",
            "async_functions": r"async\s+def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(",
            "properties": r"@property\s+def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(",
            "cli_commands": r"@click\.command|@app\.command|def\s+(.*_command)\s*\(",
            "api_endpoints": r"@app\.route|@router\.|def\s+(.*_endpoint)\s*\("
        }
        
    def load_coverage_database(self):
        """Load the test coverage tracking database"""
        if self.coverage_db_path.exists():
            try:
                with open(self.coverage_db_path, 'r') as f:
                    self.coverage_db = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.coverage_db = self._create_empty_database()
        else:
            self.coverage_db = self._create_empty_database()
    
    def _create_empty_database(self):
        """Create empty coverage database structure"""
        return {
            "tracked_functions": {},
            "test_mappings": {},
            "coverage_history": [],
            "missing_tests": {},
            "last_scan": None
        }
    
    def save_coverage_database(self):
        """Save the coverage database"""
        with open(self.coverage_db_path, 'w') as f:
            json.dump(self.coverage_db, f, indent=2)
    
    def scan_for_new_functionality(self) -> Dict[str, List[Dict]]:
        """Scan the codebase for new functionality since last check"""
        
        print("🔍 Scanning for new functionality...")
        
        # Get all Python files in the source directory
        source_files = []
        for pattern in ["philosopher_dinner/**/*.py", "tests/**/*.py"]:
            source_files.extend(self.repo_path.glob(pattern))
        
        new_functionality = {
            "functions": [],
            "classes": [],
            "methods": [],
            "async_functions": [],
            "properties": [],
            "cli_commands": [],
            "api_endpoints": []
        }
        
        for file_path in source_files:
            if file_path.name.startswith('__') or file_path.name.startswith('.'):
                continue
                
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Skip if file is mostly imports or empty
                if len(content.strip()) < 50:
                    continue
                
                relative_path = str(file_path.relative_to(self.repo_path))
                
                # Extract functionality using AST for more accurate parsing
                try:
                    tree = ast.parse(content)
                    extracted = self._extract_functionality_ast(tree, relative_path, content)
                    
                    for func_type, functions in extracted.items():
                        new_functionality[func_type].extend(functions)
                        
                except SyntaxError:
                    # Fallback to regex if AST parsing fails
                    extracted = self._extract_functionality_regex(content, relative_path)
                    for func_type, functions in extracted.items():
                        new_functionality[func_type].extend(functions)
                        
            except Exception as e:
                print(f"⚠️  Error processing {file_path}: {e}")
                continue
        
        return new_functionality
    
    def _extract_functionality_ast(self, tree: ast.AST, file_path: str, content: str) -> Dict[str, List[Dict]]:
        """Extract functionality using AST parsing"""
        
        functionality = {
            "functions": [],
            "classes": [],
            "methods": [],
            "async_functions": [],
            "properties": [],
            "cli_commands": [],
            "api_endpoints": []
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_info = {
                    "name": node.name,
                    "file": file_path,
                    "line": node.lineno,
                    "docstring": ast.get_docstring(node),
                    "args": [arg.arg for arg in node.args.args],
                    "decorators": [self._get_decorator_name(d) for d in node.decorators],
                    "is_private": node.name.startswith('_'),
                    "is_test": node.name.startswith('test_') or 'test' in file_path.lower()
                }
                
                # Categorize the function
                if any(dec in ['property'] for dec in func_info["decorators"]):
                    functionality["properties"].append(func_info)
                elif any('command' in dec for dec in func_info["decorators"]):
                    functionality["cli_commands"].append(func_info)
                elif any('route' in dec or 'endpoint' in dec for dec in func_info["decorators"]):
                    functionality["api_endpoints"].append(func_info)
                elif 'self' in func_info["args"]:
                    functionality["methods"].append(func_info)
                else:
                    functionality["functions"].append(func_info)
                    
            elif isinstance(node, ast.AsyncFunctionDef):
                func_info = {
                    "name": node.name,
                    "file": file_path,
                    "line": node.lineno,
                    "docstring": ast.get_docstring(node),
                    "args": [arg.arg for arg in node.args.args],
                    "decorators": [self._get_decorator_name(d) for d in node.decorators],
                    "is_private": node.name.startswith('_'),
                    "is_test": node.name.startswith('test_') or 'test' in file_path.lower(),
                    "is_async": True
                }
                functionality["async_functions"].append(func_info)
                
            elif isinstance(node, ast.ClassDef):
                class_info = {
                    "name": node.name,
                    "file": file_path,
                    "line": node.lineno,
                    "docstring": ast.get_docstring(node),
                    "bases": [self._get_base_name(base) for base in node.bases],
                    "decorators": [self._get_decorator_name(d) for d in node.decorator_list],
                    "is_private": node.name.startswith('_'),
                    "is_test": node.name.startswith('Test') or 'test' in file_path.lower()
                }
                functionality["classes"].append(class_info)
        
        return functionality
    
    def _get_decorator_name(self, decorator):
        """Extract decorator name from AST node"""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return f"{decorator.value.id}.{decorator.attr}"
        else:
            return str(decorator)
    
    def _get_base_name(self, base):
        """Extract base class name from AST node"""
        if isinstance(base, ast.Name):
            return base.id
        elif isinstance(base, ast.Attribute):
            return f"{base.value.id}.{base.attr}"
        else:
            return str(base)
    
    def _extract_functionality_regex(self, content: str, file_path: str) -> Dict[str, List[Dict]]:
        """Fallback: Extract functionality using regex patterns"""
        
        functionality = {
            "functions": [],
            "classes": [],
            "methods": [],
            "async_functions": [],
            "properties": [],
            "cli_commands": [],
            "api_endpoints": []
        }
        
        lines = content.split('\n')
        
        for func_type, pattern in self.functionality_patterns.items():
            matches = re.finditer(pattern, content, re.MULTILINE)
            
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                func_name = match.group(1)
                
                func_info = {
                    "name": func_name,
                    "file": file_path,
                    "line": line_num,
                    "is_private": func_name.startswith('_'),
                    "is_test": func_name.startswith('test_') or 'test' in file_path.lower(),
                    "extracted_via": "regex"
                }
                
                functionality[func_type].append(func_info)
        
        return functionality
    
    def identify_missing_tests(self, functionality: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
        """Identify functionality that lacks proper test coverage"""
        
        print("🧪 Identifying missing test coverage...")
        
        missing_tests = {
            "untested_functions": [],
            "untested_classes": [],
            "untested_methods": [],
            "untested_async_functions": [],
            "untested_properties": [],
            "untested_cli_commands": [],
            "untested_api_endpoints": []
        }
        
        # Get all existing test functions
        existing_tests = set()
        for func_type in functionality:
            for func in functionality[func_type]:
                if func["is_test"]:
                    existing_tests.add(func["name"])
        
        # Check each type of functionality for test coverage
        for func_type, functions in functionality.items():
            if func_type in ["functions", "async_functions"]:
                untested_key = f"untested_{func_type}"
                
                for func in functions:
                    if func["is_test"] or func["is_private"]:
                        continue
                    
                    # Look for corresponding test
                    expected_test_names = [
                        f"test_{func['name']}",
                        f"test_{func['name']}_functionality",
                        f"test_{func['name']}_behavior",
                        f"test_{func['name']}_integration"
                    ]
                    
                    has_test = any(test_name in existing_tests for test_name in expected_test_names)
                    
                    if not has_test:
                        missing_tests[untested_key].append({
                            **func,
                            "expected_tests": expected_test_names,
                            "priority": self._calculate_test_priority(func)
                        })
            
            elif func_type == "classes":
                for cls in functions:
                    if cls["is_test"] or cls["is_private"]:
                        continue
                    
                    # Look for corresponding test class
                    expected_test_names = [
                        f"Test{cls['name']}",
                        f"test_{cls['name'].lower()}",
                        f"test_{cls['name']}_class"
                    ]
                    
                    has_test = any(test_name in existing_tests for test_name in expected_test_names)
                    
                    if not has_test:
                        missing_tests["untested_classes"].append({
                            **cls,
                            "expected_tests": expected_test_names,
                            "priority": self._calculate_test_priority(cls)
                        })
        
        return missing_tests
    
    def _calculate_test_priority(self, func_info: Dict) -> str:
        """Calculate the priority for adding tests to this functionality"""
        
        high_priority_indicators = [
            "command" in func_info["name"].lower(),
            "api" in func_info["name"].lower(),
            "endpoint" in func_info["name"].lower(),
            "process" in func_info["name"].lower(),
            "handle" in func_info["name"].lower(),
            "execute" in func_info["name"].lower(),
            not func_info.get("is_private", False),
            func_info.get("docstring") is not None
        ]
        
        medium_priority_indicators = [
            "helper" in func_info["name"].lower(),
            "util" in func_info["name"].lower(),
            "format" in func_info["name"].lower(),
            "parse" in func_info["name"].lower()
        ]
        
        high_count = sum(high_priority_indicators)
        medium_count = sum(medium_priority_indicators)
        
        if high_count >= 2:
            return "high"
        elif high_count >= 1 or medium_count >= 2:
            return "medium"
        else:
            return "low"
    
    def generate_test_templates(self, missing_tests: Dict) -> Dict[str, str]:
        """Generate test templates for missing functionality"""
        
        print("📝 Generating test templates...")
        
        templates = {}
        
        for category, items in missing_tests.items():
            if not items:
                continue
                
            category_name = category.replace("untested_", "")
            template_content = []
            
            template_content.append(f"#!/usr/bin/env python3")
            template_content.append(f'"""')
            template_content.append(f'Automated test templates for {category_name}')
            template_content.append(f'Generated by Test Coverage Enforcer on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
            template_content.append(f'"""')
            template_content.append("")
            template_content.append("import sys")
            template_content.append("import os")
            template_content.append("import pytest")
            template_content.append("from unittest.mock import patch, MagicMock")
            template_content.append("")
            template_content.append("# Add project to path")
            template_content.append("sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))")
            template_content.append("")
            
            for item in items:
                # Import statement
                module_path = item["file"].replace("/", ".").replace(".py", "")
                template_content.append(f"from {module_path} import {item['name']}")
            
            template_content.append("")
            template_content.append("")
            
            for item in items:
                priority = item.get("priority", "medium")
                
                template_content.append(f"class Test{item['name'].title()}:")
                template_content.append(f'    """Test class for {item["name"]} functionality"""')
                template_content.append("")
                template_content.append(f"    def test_{item['name']}_basic_functionality(self):")
                template_content.append(f'        """Test basic functionality of {item["name"]}"""')
                template_content.append(f"        # TODO: Implement basic functionality test")
                template_content.append(f"        # Priority: {priority}")
                template_content.append(f"        # File: {item['file']}:{item['line']}")
                
                if item.get("docstring"):
                    template_content.append(f'        # Description: {item["docstring"][:100]}...')
                
                template_content.append(f"        pass")
                template_content.append("")
                
                if priority in ["high", "medium"]:
                    template_content.append(f"    def test_{item['name']}_error_handling(self):")
                    template_content.append(f'        """Test error handling for {item["name"]}"""')
                    template_content.append(f"        # TODO: Test error conditions and edge cases")
                    template_content.append(f"        pass")
                    template_content.append("")
                
                if priority == "high":
                    template_content.append(f"    def test_{item['name']}_integration(self):")
                    template_content.append(f'        """Test integration scenarios for {item["name"]}"""')
                    template_content.append(f"        # TODO: Test integration with other components")
                    template_content.append(f"        pass")
                    template_content.append("")
            
            templates[f"test_{category_name}_generated.py"] = "\n".join(template_content)
        
        return templates
    
    def create_test_enforcement_hook(self):
        """Create a pre-commit hook that enforces test coverage"""
        
        hook_content = '''#!/bin/bash
# Pre-commit hook for test coverage enforcement

echo "🧪 Checking test coverage for new functionality..."

# Run the test coverage enforcer
python3 test_coverage_enforcer.py --enforce

# Check if there are missing tests
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ COMMIT BLOCKED: Missing test coverage detected!"
    echo "📝 Please add tests for new functionality before committing."
    echo "💡 Run 'python3 test_coverage_enforcer.py --generate-templates' to get started."
    echo ""
    exit 1
fi

echo "✅ Test coverage requirements satisfied!"
'''
        
        hook_path = self.repo_path / ".git/hooks/pre-commit-test-coverage"
        with open(hook_path, 'w') as f:
            f.write(hook_content)
        
        # Make executable
        hook_path.chmod(0o755)
        
        print(f"✅ Created test coverage enforcement hook: {hook_path}")
    
    def enforce_coverage(self, strict: bool = False) -> bool:
        """Enforce test coverage requirements"""
        
        print("🔒 ENFORCING TEST COVERAGE REQUIREMENTS")
        print("=" * 50)
        
        functionality = self.scan_for_new_functionality()
        missing_tests = self.identify_missing_tests(functionality)
        
        # Count missing tests by priority
        total_missing = 0
        high_priority_missing = 0
        
        for category, items in missing_tests.items():
            total_missing += len(items)
            high_priority_missing += len([item for item in items if item.get("priority") == "high"])
        
        print(f"📊 COVERAGE ANALYSIS:")
        print(f"  📋 Total functionality items: {sum(len(funcs) for funcs in functionality.values())}")
        print(f"  ❌ Missing tests: {total_missing}")
        print(f"  🔴 High priority missing: {high_priority_missing}")
        
        # Enforcement rules
        if strict:
            if total_missing > 0:
                print(f"\n❌ STRICT MODE: No missing tests allowed!")
                self._print_missing_tests_summary(missing_tests)
                return False
        else:
            if high_priority_missing > 0:
                print(f"\n⚠️  HIGH PRIORITY TESTS MISSING!")
                self._print_missing_tests_summary(missing_tests, priority_filter="high")
                return False
            elif total_missing > 10:
                print(f"\n⚠️  TOO MANY MISSING TESTS ({total_missing})!")
                self._print_missing_tests_summary(missing_tests)
                return False
        
        print(f"\n✅ Test coverage requirements satisfied!")
        return True
    
    def _print_missing_tests_summary(self, missing_tests: Dict, priority_filter: str = None):
        """Print summary of missing tests"""
        
        print(f"\n📋 MISSING TESTS SUMMARY:")
        
        for category, items in missing_tests.items():
            if not items:
                continue
            
            if priority_filter:
                items = [item for item in items if item.get("priority") == priority_filter]
                if not items:
                    continue
            
            print(f"\n{category.replace('untested_', '').title()}:")
            for item in items[:5]:  # Show first 5
                priority = item.get("priority", "medium")
                print(f"  🔴 {item['name']} ({priority}) - {item['file']}:{item['line']}")
            
            if len(items) > 5:
                print(f"  ... and {len(items) - 5} more")
    
    def generate_and_save_templates(self):
        """Generate and save test templates to files"""
        
        functionality = self.scan_for_new_functionality()
        missing_tests = self.identify_missing_tests(functionality)
        templates = self.generate_test_templates(missing_tests)
        
        if not templates:
            print("✅ No missing test templates needed!")
            return
        
        templates_dir = self.repo_path / "tests" / "generated"
        templates_dir.mkdir(exist_ok=True)
        
        for filename, content in templates.items():
            file_path = templates_dir / filename
            with open(file_path, 'w') as f:
                f.write(content)
            print(f"📝 Generated test template: {file_path}")
        
        print(f"\n💡 Next steps:")
        print(f"  1. Review generated templates in {templates_dir}")
        print(f"  2. Implement the TODO test cases")
        print(f"  3. Run tests to ensure they work")
        print(f"  4. Add templates to your test runner")


def main():
    """Main function with CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Coverage Enforcer")
    parser.add_argument("--scan", action="store_true", help="Scan for new functionality")
    parser.add_argument("--enforce", action="store_true", help="Enforce test coverage requirements")
    parser.add_argument("--strict", action="store_true", help="Use strict enforcement (no missing tests allowed)")
    parser.add_argument("--generate-templates", action="store_true", help="Generate test templates")
    parser.add_argument("--setup-hooks", action="store_true", help="Set up test coverage enforcement hooks")
    
    args = parser.parse_args()
    
    enforcer = TestCoverageEnforcer()
    
    if args.scan:
        functionality = enforcer.scan_for_new_functionality()
        missing_tests = enforcer.identify_missing_tests(functionality)
        
        print("🔍 FUNCTIONALITY SCAN RESULTS:")
        for category, items in functionality.items():
            if items:
                print(f"  {category}: {len(items)} items")
        
        print("\n🧪 MISSING TEST COVERAGE:")
        for category, items in missing_tests.items():
            if items:
                print(f"  {category}: {len(items)} items")
    
    elif args.enforce:
        success = enforcer.enforce_coverage(strict=args.strict)
        sys.exit(0 if success else 1)
    
    elif args.generate_templates:
        enforcer.generate_and_save_templates()
    
    elif args.setup_hooks:
        enforcer.create_test_enforcement_hook()
    
    else:
        # Default: run full analysis
        print("🧪 COMPREHENSIVE TEST COVERAGE ANALYSIS")
        print("=" * 50)
        
        functionality = enforcer.scan_for_new_functionality()
        missing_tests = enforcer.identify_missing_tests(functionality)
        
        total_functionality = sum(len(items) for items in functionality.values())
        total_missing = sum(len(items) for items in missing_tests.values())
        
        coverage_percent = ((total_functionality - total_missing) / max(1, total_functionality)) * 100
        
        print(f"📊 OVERALL COVERAGE: {coverage_percent:.1f}%")
        print(f"  📋 Total functionality: {total_functionality}")
        print(f"  ✅ Tested: {total_functionality - total_missing}")
        print(f"  ❌ Missing tests: {total_missing}")
        
        if total_missing > 0:
            print(f"\n💡 To generate test templates:")
            print(f"  python3 test_coverage_enforcer.py --generate-templates")


if __name__ == "__main__":
    main()