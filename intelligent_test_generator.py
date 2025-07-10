#!/usr/bin/env python3
"""
Intelligent Test Generator
Automatically generates comprehensive tests based on function analysis
"""

import os
import sys
import ast
import inspect
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

class IntelligentTestGenerator:
    """Generates intelligent, comprehensive tests for new functionality"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.test_patterns = {
            "happy_path": "Test normal, expected usage",
            "edge_cases": "Test boundary conditions and edge cases", 
            "error_handling": "Test error conditions and exception handling",
            "integration": "Test interaction with other components",
            "performance": "Test performance characteristics",
            "security": "Test security aspects and input validation"
        }
        
    def analyze_function(self, func_info: Dict) -> Dict[str, Any]:
        """Analyze a function to understand what tests it needs"""
        
        analysis = {
            "name": func_info["name"],
            "file": func_info["file"],
            "complexity": "medium",
            "test_categories": [],
            "mock_requirements": [],
            "test_data_needs": [],
            "security_considerations": [],
            "performance_considerations": []
        }
        
        # Analyze function signature
        args = func_info.get("args", [])
        docstring = func_info.get("docstring", "")
        
        # Determine complexity
        if len(args) > 5 or "async" in func_info.get("name", ""):
            analysis["complexity"] = "high"
        elif len(args) <= 2 and not docstring:
            analysis["complexity"] = "low"
        
        # Determine test categories needed
        if not func_info.get("is_private", False):
            analysis["test_categories"].append("happy_path")
        
        # Check for error handling needs
        if "raise" in docstring.lower() or "error" in docstring.lower() or "exception" in docstring.lower():
            analysis["test_categories"].append("error_handling")
        
        # Check for integration needs
        if "self" in args or len(args) > 3:
            analysis["test_categories"].append("integration")
        
        # Check for performance considerations
        if any(keyword in func_info["name"].lower() for keyword in ["process", "parse", "search", "compute", "calculate"]):
            analysis["test_categories"].append("performance")
            analysis["performance_considerations"].append("execution_time")
        
        # Check for security considerations
        if any(keyword in func_info["name"].lower() for keyword in ["auth", "login", "password", "token", "validate", "sanitize"]):
            analysis["test_categories"].append("security")
            analysis["security_considerations"].extend(["input_validation", "injection_prevention"])
        
        # Determine mock requirements
        if "file" in args or "path" in args:
            analysis["mock_requirements"].append("file_system")
        if "request" in args or "response" in args:
            analysis["mock_requirements"].append("http_requests")
        if "db" in args or "database" in args:
            analysis["mock_requirements"].append("database")
        
        # Determine test data needs
        for arg in args:
            if "email" in arg.lower():
                analysis["test_data_needs"].append("email_addresses")
            elif "url" in arg.lower():
                analysis["test_data_needs"].append("urls")
            elif "name" in arg.lower():
                analysis["test_data_needs"].append("names")
            elif "id" in arg.lower():
                analysis["test_data_needs"].append("identifiers")
        
        return analysis
    
    def generate_test_class(self, func_info: Dict, analysis: Dict) -> str:
        """Generate a comprehensive test class for a function"""
        
        class_name = f"Test{func_info['name'].title().replace('_', '')}"
        lines = []
        
        # Class header
        lines.append(f"class {class_name}:")
        lines.append(f'    """Comprehensive tests for {func_info["name"]} functionality"""')
        lines.append("")
        
        # Setup method if needed
        if analysis["mock_requirements"] or analysis["complexity"] == "high":
            lines.extend(self._generate_setup_method(func_info, analysis))
        
        # Generate tests for each category
        for category in analysis["test_categories"]:
            test_methods = self._generate_test_methods(func_info, analysis, category)
            lines.extend(test_methods)
        
        # Add edge cases if not already covered
        if "edge_cases" not in analysis["test_categories"]:
            lines.extend(self._generate_edge_case_tests(func_info, analysis))
        
        return "\n".join(lines)
    
    def _generate_setup_method(self, func_info: Dict, analysis: Dict) -> List[str]:
        """Generate setup method for test class"""
        
        lines = []
        lines.append("    def setup_method(self):")
        lines.append('        """Set up test fixtures before each test method"""')
        
        # Mock setup
        if "file_system" in analysis["mock_requirements"]:
            lines.append("        self.mock_file_system = MagicMock()")
        if "http_requests" in analysis["mock_requirements"]:
            lines.append("        self.mock_requests = MagicMock()")
        if "database" in analysis["mock_requirements"]:
            lines.append("        self.mock_db = MagicMock()")
        
        # Test data setup
        lines.append("        self.test_data = {")
        for data_type in analysis["test_data_needs"]:
            if data_type == "email_addresses":
                lines.append('            "valid_email": "test@example.com",')
                lines.append('            "invalid_email": "invalid-email",')
            elif data_type == "urls":
                lines.append('            "valid_url": "https://example.com",')
                lines.append('            "invalid_url": "not-a-url",')
            elif data_type == "names":
                lines.append('            "valid_name": "John Doe",')
                lines.append('            "empty_name": "",')
        lines.append("        }")
        lines.append("")
        
        return lines
    
    def _generate_test_methods(self, func_info: Dict, analysis: Dict, category: str) -> List[str]:
        """Generate test methods for a specific category"""
        
        lines = []
        method_name = f"test_{func_info['name']}_{category}"
        
        lines.append(f"    def {method_name}(self):")
        lines.append(f'        """{self.test_patterns[category]}"""')
        
        if category == "happy_path":
            lines.extend(self._generate_happy_path_test(func_info, analysis))
        elif category == "error_handling":
            lines.extend(self._generate_error_handling_test(func_info, analysis))
        elif category == "integration":
            lines.extend(self._generate_integration_test(func_info, analysis))
        elif category == "performance":
            lines.extend(self._generate_performance_test(func_info, analysis))
        elif category == "security":
            lines.extend(self._generate_security_test(func_info, analysis))
        else:
            lines.append("        # TODO: Implement specific test logic")
            lines.append("        pass")
        
        lines.append("")
        return lines
    
    def _generate_happy_path_test(self, func_info: Dict, analysis: Dict) -> List[str]:
        """Generate happy path test implementation"""
        
        lines = []
        lines.append("        # Test normal, successful execution")
        
        # Import the function
        module_path = func_info["file"].replace("/", ".").replace(".py", "")
        lines.append(f"        from {module_path} import {func_info['name']}")
        lines.append("")
        
        # Generate test call
        args = func_info.get("args", [])
        if args:
            # Create sample arguments
            test_args = []
            for arg in args:
                if arg == "self":
                    continue
                elif "email" in arg.lower():
                    test_args.append('self.test_data["valid_email"]')
                elif "name" in arg.lower():
                    test_args.append('self.test_data["valid_name"]')
                elif "url" in arg.lower():
                    test_args.append('self.test_data["valid_url"]')
                else:
                    test_args.append(f'"test_{arg}"')
            
            lines.append(f"        result = {func_info['name']}({', '.join(test_args)})")
        else:
            lines.append(f"        result = {func_info['name']}()")
        
        lines.append("        ")
        lines.append("        # Verify expected behavior")
        lines.append("        assert result is not None, 'Function should return a result'")
        lines.append("        # TODO: Add specific assertions based on expected behavior")
        
        return lines
    
    def _generate_error_handling_test(self, func_info: Dict, analysis: Dict) -> List[str]:
        """Generate error handling test implementation"""
        
        lines = []
        lines.append("        # Test error conditions and exception handling")
        
        module_path = func_info["file"].replace("/", ".").replace(".py", "")
        lines.append(f"        from {module_path} import {func_info['name']}")
        lines.append("")
        
        # Test with invalid inputs
        lines.append("        # Test with invalid inputs")
        lines.append("        with pytest.raises(Exception):")
        
        args = func_info.get("args", [])
        if args and args != ["self"]:
            lines.append(f"            {func_info['name']}(None)  # Invalid input")
        else:
            lines.append(f"            # TODO: Identify specific error conditions for {func_info['name']}")
        
        lines.append("")
        lines.append("        # Test edge cases that might cause errors")
        lines.append("        # TODO: Add specific error condition tests")
        
        return lines
    
    def _generate_integration_test(self, func_info: Dict, analysis: Dict) -> List[str]:
        """Generate integration test implementation"""
        
        lines = []
        lines.append("        # Test integration with other components")
        
        if "file_system" in analysis["mock_requirements"]:
            lines.append("        with patch('builtins.open', self.mock_file_system):")
            lines.append(f"            # Test file operations")
            lines.append(f"            # TODO: Test file interaction scenarios")
        
        if "http_requests" in analysis["mock_requirements"]:
            lines.append("        with patch('requests.get', self.mock_requests):")
            lines.append(f"            # Test HTTP request scenarios")
            lines.append(f"            # TODO: Test request/response handling")
        
        if not analysis["mock_requirements"]:
            lines.append("        # TODO: Test interaction with other system components")
            lines.append("        pass")
        
        return lines
    
    def _generate_performance_test(self, func_info: Dict, analysis: Dict) -> List[str]:
        """Generate performance test implementation"""
        
        lines = []
        lines.append("        # Test performance characteristics")
        lines.append("        import time")
        lines.append("")
        lines.append("        start_time = time.time()")
        lines.append(f"        # TODO: Call {func_info['name']} with performance test data")
        lines.append("        end_time = time.time()")
        lines.append("")
        lines.append("        execution_time = end_time - start_time")
        lines.append("        assert execution_time < 1.0, 'Function should complete within 1 second'")
        lines.append("        # TODO: Adjust time limits based on expected performance")
        
        return lines
    
    def _generate_security_test(self, func_info: Dict, analysis: Dict) -> List[str]:
        """Generate security test implementation"""
        
        lines = []
        lines.append("        # Test security aspects and input validation")
        
        if "input_validation" in analysis["security_considerations"]:
            lines.append("        # Test input validation")
            lines.append("        malicious_inputs = [")
            lines.append('            "<script>alert(\'xss\')</script>",')
            lines.append('            "'; DROP TABLE users; --",')
            lines.append('            "../../../etc/passwd",')
            lines.append('            "\\x00\\x01\\x02"')
            lines.append("        ]")
            lines.append("")
            lines.append("        for malicious_input in malicious_inputs:")
            lines.append("            # TODO: Verify malicious input is properly handled")
            lines.append("            pass")
        
        if "injection_prevention" in analysis["security_considerations"]:
            lines.append("        # Test injection prevention")
            lines.append("        # TODO: Test SQL injection, command injection prevention")
        
        return lines
    
    def _generate_edge_case_tests(self, func_info: Dict, analysis: Dict) -> List[str]:
        """Generate edge case tests"""
        
        lines = []
        lines.append(f"    def test_{func_info['name']}_edge_cases(self):")
        lines.append('        """Test boundary conditions and edge cases"""')
        
        args = func_info.get("args", [])
        if args and args != ["self"]:
            lines.append("        # Test with boundary values")
            lines.append("        test_cases = [")
            lines.append('            "",  # Empty string')
            lines.append('            None,  # None value')
            lines.append('            [],  # Empty list')
            lines.append('            {},  # Empty dict')
            lines.append("        ]")
            lines.append("")
            lines.append("        for test_case in test_cases:")
            lines.append("            try:")
            lines.append(f"                result = {func_info['name']}(test_case)")
            lines.append("                # TODO: Verify behavior with edge case inputs")
            lines.append("            except Exception as e:")
            lines.append("                # TODO: Verify expected exceptions")
            lines.append("                pass")
        else:
            lines.append("        # TODO: Identify relevant edge cases")
            lines.append("        pass")
        
        lines.append("")
        return lines
    
    def generate_comprehensive_test_file(self, functions: List[Dict]) -> str:
        """Generate a complete test file for multiple functions"""
        
        lines = []
        
        # File header
        lines.append("#!/usr/bin/env python3")
        lines.append('"""')
        lines.append('Comprehensive automated tests')
        lines.append(f'Generated by Intelligent Test Generator on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        lines.append('"""')
        lines.append("")
        
        # Imports
        lines.append("import sys")
        lines.append("import os")
        lines.append("import pytest")
        lines.append("import time")
        lines.append("from unittest.mock import patch, MagicMock, Mock")
        lines.append("from pathlib import Path")
        lines.append("")
        lines.append("# Add project to path")
        lines.append("sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))")
        lines.append("")
        
        # Generate test classes for each function
        for func_info in functions:
            analysis = self.analyze_function(func_info)
            test_class = self.generate_test_class(func_info, analysis)
            lines.append(test_class)
            lines.append("")
        
        # Test runner
        lines.append("")
        lines.append("def run_comprehensive_tests():")
        lines.append('    """Run all comprehensive tests"""')
        lines.append("    ")
        lines.append("    print('🧪 RUNNING COMPREHENSIVE AUTOMATED TESTS')")
        lines.append("    print('=' * 50)")
        lines.append("    ")
        lines.append("    # Run pytest with verbose output")
        lines.append("    import subprocess")
        lines.append("    result = subprocess.run([")
        lines.append("        'python', '-m', 'pytest', __file__, '-v'")
        lines.append("    ], capture_output=True, text=True)")
        lines.append("    ")
        lines.append("    print(result.stdout)")
        lines.append("    if result.stderr:")
        lines.append("        print('STDERR:', result.stderr)")
        lines.append("    ")
        lines.append("    return result.returncode == 0")
        lines.append("")
        lines.append("")
        lines.append("if __name__ == '__main__':")
        lines.append("    run_comprehensive_tests()")
        
        return "\n".join(lines)
    
    def create_test_automation_workflow(self):
        """Create GitHub Actions workflow for automated test generation"""
        
        workflow_content = '''name: 🤖 Automated Test Generation

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  generate-tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: 3.11
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Scan for missing test coverage
      id: coverage-check
      run: |
        python test_coverage_enforcer.py --enforce
        echo "coverage_ok=$?" >> $GITHUB_OUTPUT
      continue-on-error: true
    
    - name: Generate missing tests
      if: steps.coverage-check.outputs.coverage_ok != '0'
      run: |
        python test_coverage_enforcer.py --generate-templates
        python intelligent_test_generator.py --auto-generate
    
    - name: Commit generated tests
      if: steps.coverage-check.outputs.coverage_ok != '0'
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "Automated Test Generator"
        git add tests/generated/
        if ! git diff --cached --quiet; then
          git commit -m "🤖 Auto-generate missing test coverage

Generated comprehensive tests for new functionality.
Please review and implement the TODO items.

🤖 Generated with [Claude Code](https://claude.ai/code)"
          git push
        fi
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Create PR comment with test summary
      if: github.event_name == 'pull_request' && steps.coverage-check.outputs.coverage_ok != '0'
      uses: actions/github-script@v6
      with:
        script: |
          github.rest.issues.createComment({
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: `## 🤖 Automated Test Generation

⚠️ **Missing test coverage detected!**

I've automatically generated test templates for new functionality. 

📝 **Next steps:**
1. Review generated tests in \`tests/generated/\`
2. Implement the TODO test cases
3. Run tests to ensure they work
4. Include tests in your regular test suite

💡 **Generated tests include:**
- Happy path testing
- Error handling
- Edge cases
- Integration scenarios
- Performance considerations
- Security validation

*Generated by Automated Test Generation workflow*`
          })
'''
        
        workflow_path = self.repo_path / ".github/workflows/auto-test-generation.yml"
        workflow_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(workflow_path, 'w') as f:
            f.write(workflow_content)
        
        print(f"✅ Created automated test generation workflow: {workflow_path}")


def main():
    """Main function with CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Intelligent Test Generator")
    parser.add_argument("--analyze", type=str, help="Analyze specific function")
    parser.add_argument("--generate", type=str, help="Generate tests for specific file")
    parser.add_argument("--auto-generate", action="store_true", help="Auto-generate tests for missing coverage")
    parser.add_argument("--setup-workflow", action="store_true", help="Set up automated test generation workflow")
    
    args = parser.parse_args()
    
    generator = IntelligentTestGenerator()
    
    if args.setup_workflow:
        generator.create_test_automation_workflow()
    
    elif args.auto_generate:
        print("🤖 AUTO-GENERATING COMPREHENSIVE TESTS")
        print("=" * 50)
        
        from test_coverage_enforcer import TestCoverageEnforcer
        enforcer = TestCoverageEnforcer()
        
        functionality = enforcer.scan_for_new_functionality()
        missing_tests = enforcer.identify_missing_tests(functionality)
        
        # Generate comprehensive tests for missing coverage
        for category, items in missing_tests.items():
            if items:
                test_file_content = generator.generate_comprehensive_test_file(items)
                
                output_path = Path("tests/generated") / f"comprehensive_{category}.py"
                output_path.parent.mkdir(exist_ok=True)
                
                with open(output_path, 'w') as f:
                    f.write(test_file_content)
                
                print(f"✅ Generated comprehensive tests: {output_path}")
    
    else:
        print("🧪 INTELLIGENT TEST GENERATOR")
        print("Use --help for available options")


if __name__ == "__main__":
    main()