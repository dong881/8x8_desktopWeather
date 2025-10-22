#!/usr/bin/env python3
"""
Test script to verify environment variable loading from .env file
"""

import os
from dotenv import load_dotenv

def test_env_loading():
    """Test loading environment variables from .env file"""
    print("=" * 60)
    print("🔧 Testing Environment Variable Loading")
    print("=" * 60)
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Test GitHub variables
    github_token = os.getenv('GITHUB_TOKEN')
    github_repo = os.getenv('GITHUB_REPO')
    github_path = os.getenv('GITHUB_PATH')
    github_branch = os.getenv('GITHUB_BRANCH')
    
    print(f"GITHUB_TOKEN: {'✅ Set' if github_token else '❌ Not set'}")
    print(f"GITHUB_REPO: {'✅ Set' if github_repo else '❌ Not set'}")
    print(f"GITHUB_PATH: {'✅ Set' if github_path else '❌ Not set'}")
    print(f"GITHUB_BRANCH: {'✅ Set' if github_branch else '❌ Not set'}")
    
    # Test other variables
    port = os.getenv('PORT')
    flask_secret = os.getenv('FLASK_SECRET_KEY')
    
    print(f"\nPORT: {'✅ Set' if port else '❌ Not set'}")
    print(f"FLASK_SECRET_KEY: {'✅ Set' if flask_secret else '❌ Not set'}")
    
    print("\n" + "=" * 60)
    print("📝 Environment Variables Summary:")
    print("=" * 60)
    
    # Show all environment variables that start with GITHUB
    github_vars = {k: v for k, v in os.environ.items() if k.startswith('GITHUB')}
    if github_vars:
        for key, value in github_vars.items():
            # Don't show the actual token value for security
            if 'TOKEN' in key:
                print(f"{key}: {'*' * 10} (hidden)")
            else:
                print(f"{key}: {value}")
    else:
        print("No GITHUB_* environment variables found")
    
    print("\n" + "=" * 60)
    print("💡 To fix the GitHub token issue:")
    print("1. Edit the .env file and add your GitHub token:")
    print("   GITHUB_TOKEN=your_github_token_here")
    print("2. Add your repository name:")
    print("   GITHUB_REPO=your_username/your_repo_name")
    print("=" * 60)

if __name__ == "__main__":
    test_env_loading()