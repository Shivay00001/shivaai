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

from shivai.core_engine import ShivAIAgent, Config
from shivai.utils.logger import setup_logging


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
    
    # Setup logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    setup_logging(log_level, args.log_file)
    
    logger = logging.getLogger(__name__)
    logger.info("Starting ShivAI...")
    
    # Print banner
    print_banner()
    
    try:
        # Load configuration
        config = Config(args.config) if args.config else Config()
        
        if args.text:
            print("📝 Running in text-only mode (voice disabled)")
            # Disable voice plugins
            config.speech.engine = "disabled"
            config.tts.engine = "disabled"
        
        # Create and run agent
        agent = ShivAIAgent(config)
        
        if args.text:
            # Text-only interactive loop
            print("\nType 'help' for commands, 'exit' to quit\n")
            while True:
                try:
                    command = input("You: ").strip()
                    if command:
                        if not agent.process_command(command):
                            break
                except KeyboardInterrupt:
                    print("\n")
                    break
        else:
            # Voice interactive mode
            agent.run()
    
    except KeyboardInterrupt:
        print("\n\n🔷 ShivAI Shutdown Initiated")
        logger.info("Keyboard interrupt received")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1
    
    print("💾 Saving session data...")
    print("✅ Session saved. Goodbye!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
