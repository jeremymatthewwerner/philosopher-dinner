#!/usr/bin/env python3
"""
LLM Setup Script for Philosopher Dinner
Helps users configure API keys and test LLM integration.
"""
import os
import sys
from pathlib import Path

def main():
    print("🏛️ Philosopher Dinner - LLM Setup")
    print("=" * 50)
    
    # Check if .env file exists
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists():
        if env_example.exists():
            print("📋 Creating .env file from .env.example...")
            env_file.write_text(env_example.read_text())
            print("✅ Created .env file. Please edit it with your API keys.")
        else:
            print("❌ No .env.example file found. Creating basic .env...")
            env_content = """# LLM Configuration
# Choose one of the following LLM providers:

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini

# Anthropic Configuration (Alternative)
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ANTHROPIC_MODEL=claude-3-haiku-20240307

# Default LLM Provider (openai or anthropic)
DEFAULT_LLM_PROVIDER=openai
"""
            env_file.write_text(env_content)
            print("✅ Created basic .env file. Please edit it with your API keys.")
    
    print(f"\n📝 Configuration file: {env_file.absolute()}")
    print("\n🔧 Setup Instructions:")
    print("1. Edit the .env file with your API key:")
    print("   - For OpenAI: Add your OpenAI API key to OPENAI_API_KEY")
    print("   - For Anthropic: Add your Anthropic API key to ANTHROPIC_API_KEY")
    print("2. Choose your preferred provider in DEFAULT_LLM_PROVIDER")
    print("3. Install the required LLM package:")
    print("   - For OpenAI: pip install langchain-openai")
    print("   - For Anthropic: pip install langchain-anthropic")
    print("4. Run the application: python main.py")
    
    # Test if dependencies are available
    print(f"\n🧪 Testing Dependencies:")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ python-dotenv is available")
    except ImportError:
        print("❌ python-dotenv not found. Install with: pip install python-dotenv")
        return
    
    # Test OpenAI
    try:
        import langchain_openai
        if os.getenv("OPENAI_API_KEY") and os.getenv("OPENAI_API_KEY") != "your_openai_api_key_here":
            print("✅ OpenAI dependencies available and API key configured")
        else:
            print("⚠️  OpenAI dependencies available but API key not configured")
    except ImportError:
        print("⚠️  OpenAI dependencies not installed. Install with: pip install langchain-openai")
    
    # Test Anthropic
    try:
        import langchain_anthropic
        if os.getenv("ANTHROPIC_API_KEY") and os.getenv("ANTHROPIC_API_KEY") != "your_anthropic_api_key_here":
            print("✅ Anthropic dependencies available and API key configured")
        else:
            print("⚠️  Anthropic dependencies available but API key not configured")
    except ImportError:
        print("⚠️  Anthropic dependencies not installed. Install with: pip install langchain-anthropic")
    
    # Test actual LLM configuration
    print(f"\n🚀 Testing LLM Configuration:")
    try:
        sys.path.insert(0, ".")
        from philosopher_dinner.config.llm_config import is_llm_available, get_available_providers, get_llm_instance
        
        if is_llm_available():
            providers = get_available_providers()
            print(f"✅ LLM is available! Providers: {', '.join(providers)}")
            
            # Test LLM instance creation
            try:
                llm = get_llm_instance()
                if llm:
                    print(f"✅ Successfully created LLM instance")
                    print("🎉 Your philosophers are ready to use AI!")
                else:
                    print("❌ Failed to create LLM instance")
            except Exception as e:
                print(f"❌ Error creating LLM instance: {e}")
        else:
            print("❌ No LLM providers configured")
            print("   Please set up either OPENAI_API_KEY or ANTHROPIC_API_KEY in .env")
            
    except Exception as e:
        print(f"❌ Error testing LLM configuration: {e}")
    
    print(f"\n" + "=" * 50)
    print("🏛️ Setup complete! Run 'python main.py' to start philosophical discussions.")

if __name__ == "__main__":
    main()