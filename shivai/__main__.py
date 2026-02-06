"""
ShivAI CLI Entry Point

Provides command-line interface for running ShivAI agent.

Usage:
    python -m shivai                    # Start interactive agent
    python -m shivai --text             # Text-only mode (no voice)
    python -m shivai --config path.yaml # Custom config
    python -m shivai --help             # Show help
"""

import sys
import argparse
import logging
from pathlib import Path


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="ShivAI - India's First Offline AGI Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m shivai                      # Start interactive mode
  python -m shivai --text               # Text-only mode
  python -m shivai --debug              # Enable debug logging
  python -m shivai --config my.yaml    # Use custom config
  
For more information, visit: https://github.com/shivai/shivai
        """
    )
    
    parser.add_argument(
        '--config',
        type=str,
        help='Path to configuration file (default: config.yaml)'
    )
    
    parser.add_argument(
        '--text',
        action='store_true',
        help='Text-only mode (disable voice input/output)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    parser.add_argument(
        '--log-file',
        type=str,
        default='data/logs/shivai.log',
        help='Log file path'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='ShivAI v1.0.0'
    )
    
    return parser.parse_args()


def print_banner():
    """Print startup banner"""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║         🔷 ShivAI - Autonomous General Intelligence          ║
║                India's First Offline AGI Assistant            ║
╚═══════════════════════════════════════════════════════════════╝

✨ Features:
   • 500+ Tasks (PC + Phone Automation)
   • Offline Speech Recognition (Hindi + English)
   • App Builder (Auto Code Generation)
   • Multi-Step Workflows
   • Pattern Learning & Context Memory
   • Android Control via ADB

🎯 No LLM Dependency | 🔒 100% Privacy | 🇮🇳 Made in India

═══════════════════════════════════════════════════════════════
"""
    print(banner)


def main():
    """Main entry point"""
    args = parse_args()
    
    # Print banner
    print_banner()
    
    print("\n⚠️  Note: Full ShivAI implementation requires additional plugins.")
    print("📝 Running in minimal mode. Type 'help' for available commands.\n")
    
    try:
        # Basic text-only interactive loop
        print("Type 'help' for commands, 'exit' to quit\n")
        while True:
            try:
                command = input("You: ").strip()
                if not command:
                    continue
                    
                if command.lower() in ['exit', 'quit', 'bye']:
                    print("\n✅ Goodbye!")
                    break
                elif command.lower() == 'help':
                    print("""
Available commands:
  help     - Show this help message
  version  - Show version information
  status   - Show system status
  exit     - Exit ShivAI

Note: Full feature set requires plugin implementation.
See README.md for setup instructions.
""")
                elif command.lower() == 'version':
                    print("ShivAI v1.0.0")
                elif command.lower() == 'status':
                    print("Status: Ready (minimal mode)")
                else:
                    print(f"Command not yet implemented: {command}")
                    print("Hint: Run 'help' to see available commands")
                    
            except KeyboardInterrupt:
                print("\n")
                break
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
