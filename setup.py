# Environment setup script for Neogiator Bot
# Run this script to set up your environment

import os
import sys

def create_env_file():
    """Create .env file with OpenAI API key prompt"""
    env_path = ".env"
    
    if os.path.exists(env_path):
        print("✅ .env file already exists")
        return
    
    print("🔑 Setting up OpenAI API Key...")
    print("You'll need an OpenAI API key to use the bot.")
    print("Get one at: https://platform.openai.com/api-keys")
    
    api_key = input("Enter your OpenAI API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided. You can set it later in the .env file.")
        return
    
    with open(env_path, "w") as f:
        f.write(f"OPENAI_API_KEY={api_key}\n")
    
    print("✅ .env file created successfully!")

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        "openai",
        "python-dotenv", 
        "requests",
        "flask",
        "flask-cors",
        "pydantic",
        "jinja2",
        "schedule",
        "colorama",
        "rich"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        os.system(f"pip install {' '.join(missing_packages)}")
    else:
        print("\n✅ All dependencies are installed!")

def main():
    """Main setup function"""
    print("🤖 Neogiator Bot Setup")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version.split()[0]}")
    
    # Check dependencies
    print("\n📦 Checking dependencies...")
    check_dependencies()
    
    # Create .env file
    print("\n🔧 Setting up environment...")
    create_env_file()
    
    print("\n🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Run 'python demo.py' to see the bot in action")
    print("2. Run 'python app.py' to start the web interface")
    print("3. Open http://localhost:5000 in your browser")

if __name__ == "__main__":
    main()
