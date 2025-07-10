"""
LLM Configuration and Factory
Handles initialization of different LLM providers for the philosopher agents.
"""
import os
from typing import Optional, Union

# Try to load environment variables, but don't fail if dotenv is not available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available, environment variables will be read from system
    pass

def get_llm_instance(provider: Optional[str] = None, model: Optional[str] = None):
    """
    Get an LLM instance based on provider and model.
    
    Args:
        provider: 'openai' or 'anthropic' (defaults to DEFAULT_LLM_PROVIDER env var)
        model: Specific model name (defaults to provider's default model)
    
    Returns:
        LLM instance ready for use with LangChain/LangGraph
    """
    provider = provider or os.getenv("DEFAULT_LLM_PROVIDER", "openai")
    
    try:
        if provider.lower() == "openai":
            return _get_openai_llm(model)
        elif provider.lower() == "anthropic":
            return _get_anthropic_llm(model)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
    except ImportError as e:
        print(f"Error importing {provider} dependencies: {e}")
        print(f"Please install: pip install langchain-{provider}")
        return None
    except Exception as e:
        print(f"Error initializing {provider} LLM: {e}")
        return None

def _get_openai_llm(model: Optional[str] = None):
    """Initialize OpenAI LLM"""
    from langchain_openai import ChatOpenAI
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    
    model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    return ChatOpenAI(
        model=model,
        api_key=api_key,
        temperature=0.7,  # Some creativity for philosophical discussions
        max_tokens=500,   # Reasonable response length
    )

def _get_anthropic_llm(model: Optional[str] = None):
    """Initialize Anthropic LLM"""
    from langchain_anthropic import ChatAnthropic
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")
    
    model = model or os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307")
    
    return ChatAnthropic(
        model=model,
        api_key=api_key,
        temperature=0.7,
        max_tokens=500,
    )

def is_llm_available() -> bool:
    """Check if LLM configuration is available"""
    provider = os.getenv("DEFAULT_LLM_PROVIDER", "openai")
    
    if provider == "openai":
        return bool(os.getenv("OPENAI_API_KEY"))
    elif provider == "anthropic":
        return bool(os.getenv("ANTHROPIC_API_KEY"))
    
    return False

def get_available_providers() -> list:
    """Get list of available LLM providers based on API keys"""
    providers = []
    
    if os.getenv("OPENAI_API_KEY"):
        providers.append("openai")
    if os.getenv("ANTHROPIC_API_KEY"):
        providers.append("anthropic")
    
    return providers