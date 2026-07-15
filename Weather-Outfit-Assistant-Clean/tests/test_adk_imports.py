#!/usr/bin/env python
"""
Test ADK Package and Agent Class Imports

Verifies that Google ADK is properly installed and all required
classes can be imported for the Weather Outfit ADK system.
"""

def test_adk_core_imports():
    """Test core ADK imports"""
    print("Testing Core ADK Imports")
    print("-" * 60)
    
    try:
        from google.adk import Agent, Runner
        print("✅ Agent class imported from google.adk")
        print("✅ Runner class imported from google.adk")
    except ImportError as e:
        print(f"❌ Failed to import core ADK classes: {e}")
        return False
    
    return True


def test_adk_app_imports():
    """Test ADK App imports"""
    print("\nTesting ADK App Imports")
    print("-" * 60)
    
    try:
        from google.adk.apps import App
        print("✅ App class imported from google.adk.apps")
    except ImportError as e:
        print(f"❌ Failed to import App class: {e}")
        return False
    
    return True


def test_adk_agents_module():
    """Test ADK agents module"""
    print("\nTesting ADK Agents Module")
    print("-" * 60)
    
    try:
        from google.adk.agents import Agent
        print("✅ Agent class imported from google.adk.agents")
    except ImportError as e:
        print(f"❌ Failed to import from google.adk.agents: {e}")
        return False
    
    return True


def test_adk_tools_module():
    """Test ADK tools module (optional)"""
    print("\nTesting ADK Tools Module")
    print("-" * 60)
    
    try:
        import google.adk.tools
        print("✅ google.adk.tools module exists")
        print("ℹ️  Note: Tool class not required for function-based tools")
    except ImportError as e:
        print(f"ℹ️  google.adk.tools module check: {e}")
    
    return True  # Optional - not required for function tools


def test_agent_creation():
    """Test creating a simple agent"""
    print("\nTesting Agent Creation")
    print("-" * 60)
    
    try:
        from google.adk.agents import Agent
        
        test_agent = Agent(
            name="test_agent",
            model="gemini-2.0-flash-exp",
            instruction="Test agent",
            description="A test agent",
            tools=[]
        )
        print(f"✅ Created test agent: {test_agent.name}")
        print(f"✅ Agent model: {test_agent.model}")
    except Exception as e:
        print(f"❌ Failed to create agent: {e}")
        return False
    
    return True


def test_app_creation():
    """Test creating an ADK app"""
    print("\nTesting App Creation")
    print("-" * 60)
    
    try:
        from google.adk.apps import App
        from google.adk.agents import Agent
        
        test_agent = Agent(
            name="test_root_agent",
            model="gemini-2.0-flash-exp",
            instruction="Test root agent",
            description="A test root agent",
            tools=[]
        )
        
        test_app = App(
            name="test_app",
            root_agent=test_agent
        )
        print(f"✅ Created test app: {test_app.name}")
        print(f"✅ App root agent: {test_app.root_agent.name}")
    except Exception as e:
        print(f"❌ Failed to create app: {e}")
        return False
    
    return True


def main():
    """Run all ADK import tests"""
    print("=" * 60)
    print("ADK PACKAGE AND AGENT CLASS IMPORT TESTS")
    print("=" * 60)
    print()
    
    tests = [
        test_adk_core_imports,
        test_adk_app_imports,
        test_adk_agents_module,
        test_adk_tools_module,
        test_agent_creation,
        test_app_creation,
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
    
    print("\n" + "=" * 60)
    if all(results):
        print("✅ ALL ADK IMPORT TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED")
        exit(1)
    print("=" * 60)
    print()
    print("Google ADK is properly installed and configured.")
    print("All required classes can be imported successfully.")
    print()


if __name__ == "__main__":
    main()
