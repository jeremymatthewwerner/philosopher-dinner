#!/usr/bin/env python3
"""
Test that all required dependencies are properly installed.
This should be the FIRST test that runs to catch missing packages.
"""
import sys
import os
import importlib
import subprocess

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_required_dependencies():
    """Test that all critical dependencies can be imported"""
    
    print("\n🔍 TESTING REQUIRED DEPENDENCIES")
    print("=" * 60)
    
    required_packages = [
        # Core framework
        ("langchain", "langchain"),
        ("langchain_core", "langchain-core"),
        ("langgraph", "langgraph"),
        
        # LLM providers
        ("langchain_openai", "langchain-openai"),
        ("langchain_anthropic", "langchain-anthropic"),
        
        # Essential libraries
        ("rich", "rich"),
        ("dotenv", "python-dotenv"),
        ("pydantic", "pydantic"),
    ]
    
    missing_packages = []
    
    for import_name, package_name in required_packages:
        try:
            importlib.import_module(import_name)
            print(f"  ✅ {import_name}")
        except ImportError as e:
            print(f"  ❌ {import_name} - MISSING! (install with: pip install {package_name})")
            missing_packages.append(package_name)
    
    if missing_packages:
        print("\n❌ MISSING DEPENDENCIES DETECTED!")
        print(f"Install missing packages with:")
        print(f"  pip install {' '.join(missing_packages)}")
        print("\nOr install all requirements:")
        print("  pip install -r requirements.txt")
        return False
    
    print("\n✅ All required dependencies are installed!")
    return True


def test_llm_provider_configuration():
    """Test that at least one LLM provider is properly configured"""
    
    print("\n🔧 TESTING LLM PROVIDER CONFIGURATION")
    print("=" * 60)
    
    import os
    from philosopher_dinner.config.llm_config import get_llm_instance, is_llm_available
    
    # Check environment variables
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    print(f"  OpenAI API Key: {'✅ Set' if openai_key else '❌ Not set'}")
    print(f"  Anthropic API Key: {'✅ Set' if anthropic_key else '❌ Not set'}")
    
    if not openai_key and not anthropic_key:
        print("\n⚠️  WARNING: No LLM API keys configured!")
        print("  The system will fall back to non-AI responses.")
        print("  To enable AI responses, set one of:")
        print("    - OPENAI_API_KEY")
        print("    - ANTHROPIC_API_KEY")
        return False
    
    # Test actual LLM initialization
    try:
        llm = get_llm_instance()
        if llm is None:
            print("\n❌ LLM initialization failed!")
            return False
        print(f"\n✅ LLM successfully initialized!")
        return True
    except Exception as e:
        print(f"\n❌ LLM initialization error: {e}")
        return False


def test_virtual_environment():
    """Test that we're running in the correct virtual environment"""
    
    print("\n🐍 TESTING VIRTUAL ENVIRONMENT")
    print("=" * 60)
    
    # Check if we're in a virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    
    print(f"  Python executable: {sys.executable}")
    print(f"  In virtual environment: {'✅ Yes' if in_venv else '⚠️  No'}")
    
    if not in_venv:
        print("\n⚠️  WARNING: Not running in a virtual environment!")
        print("  Recommended: activate the virtual environment with:")
        print("    source venv/bin/activate")
    
    return True  # Warning only, not a failure


def main():
    """Run all dependency tests"""
    
    print("🏥 PHILOSOPHER DINNER - DEPENDENCY HEALTH CHECK")
    print("=" * 70)
    
    all_passed = True
    
    # Test 1: Required dependencies
    if not test_required_dependencies():
        all_passed = False
    
    # Test 2: Virtual environment
    test_virtual_environment()
    
    # Test 3: LLM configuration (only if dependencies passed)
    if all_passed:
        if not test_llm_provider_configuration():
            # LLM config failure is a warning, not a hard failure
            print("\n⚠️  System will work but without AI responses")
    
    print("\n" + "=" * 70)
    
    if all_passed:
        print("✅ DEPENDENCY CHECK PASSED!")
        print("   All required packages are installed.")
        return 0
    else:
        print("❌ DEPENDENCY CHECK FAILED!")
        print("   Please install missing dependencies before running the application.")
        return 1


if __name__ == "__main__":
    sys.exit(main())