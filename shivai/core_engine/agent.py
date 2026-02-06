"""
ShivAI Agent - Main Orchestration Engine

Coordinates all components: plugins, speech, TTS, workflows, context.
Main command processing loop and task execution.

Based on prototype's ShivAI_AGI class.
Reference: voice_assistant.py:ShivAI_AGI
"""

import time
import uuid
import logging
from datetime import datetime
from typing import Any, Dict, Optional, Callable

from .config import Config
from .plugin_loader import PluginLoader, BasePlugin
from .command_parser import CommandParser, ParsedCommand, Intent
from .context_manager import ContextManager, TaskRecord
from .task_queue import TaskQueue, TaskPriority

logger = logging.getLogger(__name__)


class ShivAIAgent:
    """
    Main ShivAI Agent
    
    Orchestrates all subsystems and provides the main command processing loop.
    
    Architecture:
    - PluginLoader: Dynamic plugin management
    - CommandParser: Offline NLU for intent extraction
    - ContextManager: Session state and learning
    - TaskQueue: Asynchronous task execution
    
    Offline-first: All core functionality works without internet.
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize ShivAI Agent
        
        Args:
            config: Configuration object (creates default if None)
        """
        logger.info("🔷 Initializing ShivAI Agent...")
        
        # Configuration
        self.config = config or Config()
        
        # Core components
        self.plugin_loader = PluginLoader(self.config.plugin.plugin_dirs)
        self.command_parser = CommandParser()
        self.context_manager = ContextManager(self.config.database.path)
        self.task_queue = TaskQueue(max_workers=self.config.workflow.max_concurrent)
        
        # State
        self.is_active = True
        self.total_tasks = 0
        self.expert_tasks = 0
        
        # Plugin references (lazy loaded)
        self._speech_plugin = None
        self._tts_plugin = None
        self._adb_plugin = None
        self._app_builder_plugin = None
        self._workflow_plugin = None
        
        # Initialize
        self._initialize()
        
        logger.info("✅ ShivAI Agent initialized successfully!")
    
    def _initialize(self) -> None:
        """Initialize agent subsystems"""
        # Discover and load plugins
        self.plugin_loader.discover_plugins()
        
        if self.config.plugin.auto_load:
            loaded = self.plugin_loader.load_all(enabled_only=True)
            logger.info(f"Auto-loaded {loaded} plugins")
        
        # Start task queue
        self.task_queue.start()
        
        # Load context from previous sessions
        stats = self.context_manager.get_task_stats()
        if stats['total_tasks'] > 0:
            logger.info(f"Loaded context: {stats['total_tasks']} previous tasks")
    
    def _get_speech_plugin(self) -> Optional[BasePlugin]:
        """Lazy load speech recognition plugin"""
        if not self._speech_plugin:
            plugins = self.plugin_loader.get_plugins_by_capability("speech_recognition")
            self._speech_plugin = plugins[0] if plugins else None
        return self._speech_plugin
    
    def _get_tts_plugin(self) -> Optional[BasePlugin]:
        """Lazy load TTS plugin"""
        if not self._tts_plugin:
            plugins = self.plugin_loader.get_plugins_by_capability("text_to_speech")
            self._tts_plugin = plugins[0] if plugins else None
        return self._tts_plugin
    
    def _get_adb_plugin(self) -> Optional[BasePlugin]:
        """Lazy load ADB plugin"""
        if not self._adb_plugin:
            plugins = self.plugin_loader.get_plugins_by_capability("android_control")
            self._adb_plugin = plugins[0] if plugins else None
        return self._adb_plugin
    
    def _get_app_builder_plugin(self) -> Optional[BasePlugin]:
        """Lazy load app builder plugin"""
        if not self._app_builder_plugin:
            plugins = self.plugin_loader.get_plugins_by_capability("app_builder")
            self._app_builder_plugin = plugins[0] if plugins else None
        return self._app_builder_plugin
    
    def _get_workflow_plugin(self) -> Optional[BasePlugin]:
        """Lazy load workflow plugin"""
        if not self._workflow_plugin:
            plugins = self.plugin_loader.get_plugins_by_capability("workflow_engine")
            self._workflow_plugin = plugins[0] if plugins else None
        return self._workflow_plugin
    
    def speak(self, text: str, fast: bool = False) -> None:
        """
        Speak text using TTS plugin
        
        Args:
            text: Text to speak
            fast: Use fast mode (higher speech rate)
        """
        tts_plugin = self._get_tts_plugin()
        
        if tts_plugin:
            try:
                context = {'fast': fast}
                tts_plugin.handle_command(f"speak: {text}", context)
            except Exception as e:
                logger.error(f"TTS error: {e}")
        
        # Always print to console
        print(f"🤖 ShivAI: {text}")
    
    def listen(self, timeout: int = 5) -> str:
        """
        Listen for voice command using speech plugin
        
        Args:
            timeout: Listening timeout in seconds
            
        Returns:
            Recognized text (lowercase)
        """
        speech_plugin = self._get_speech_plugin()
        
        if not speech_plugin:
            logger.error("No speech recognition plugin available")
            return ""
        
        print("🎤 Suniye...")
        
        try:
            context = {'timeout': timeout}
            result = speech_plugin.handle_command("listen", context)
            
            if result:
                command = result.lower()
                print(f"👤 Aap: {command}")
                return command
        
        except Exception as e:
            logger.error(f"Speech recognition error: {e}")
        
        return ""
    
    def process_command(self, command: str) -> bool:
        """
        Process command and route to appropriate handler
        
        Args:
            command: Command text (from voice or text input)
            
        Returns:
            True to continue, False to exit
        """
        if not command:
            return True
        
        # Parse command
        parsed = self.command_parser.parse(command)
        
        logger.info(f"Intent: {parsed.intent.name} (confidence: {parsed.confidence:.2f})")
        logger.debug(f"Entities: {parsed.entities}")
        
        # Create task record
        task_id = str(uuid.uuid4())
        task_record = TaskRecord(
            task_id=task_id,
            command=command,
            intent=parsed.intent.name,
            timestamp=datetime.now(),
            status='processing'
        )
        
        self.context_manager.add_task(task_record)
        self.total_tasks += 1
        
        start_time = time.time()
        
        try:
            # Route based on intent
            result = self._route_command(parsed)
            
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            # Update task status
            self.context_manager.update_task_status(
                task_id,
                'completed',
                result=str(result),
                execution_time_ms=execution_time_ms
            )
            
            # Check if exit command
            if parsed.intent == Intent.EXIT:
                return False
        
        except Exception as e:
            logger.error(f"Command execution error: {e}")
            
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            self.context_manager.update_task_status(
                task_id,
                'failed',
                error=str(e),
                execution_time_ms=execution_time_ms
            )
            
            self.speak(f"Error: {str(e)[:100]}")
        
        return True
    
    def _route_command(self, parsed: ParsedCommand) -> Any:
        """
        Route parsed command to appropriate handler
        
        Args:
            parsed: ParsedCommand object
            
        Returns:
            Command execution result
        """
        intent = parsed.intent
        entities = parsed.entities
        
        # Exit
        if intent == Intent.EXIT:
            self._handle_exit()
            return "Exiting"
        
        # Help
        elif intent == Intent.HELP:
            return self._handle_help()
        
        # Status
        elif intent == Intent.STATUS:
            return self._handle_status()
        
        # Android control
        elif intent.name.startswith('ANDROID_'):
            return self._handle_android_command(parsed)
        
        # App builder
        elif intent.name.startswith('APP_'):
            return self._handle_app_builder_command(parsed)
        
        # Workflow
        elif intent.name.startswith('WORKFLOW_'):
            return self._handle_workflow_command(parsed)
        
        # Learning
        elif intent.name.startswith('PATTERN_'):
            return self._handle_pattern_command(parsed)
        
        # PC automation
        elif intent.name.startswith('PC_'):
            return self._handle_pc_command(parsed)
        
        # Expert tasks
        elif intent.name.startswith('EXPERT_'):
            self.expert_tasks += 1
            return self._handle_expert_command(parsed)
        
        # Unknown
        else:
            self.speak("Command samajh nahi aaya. Help boliye.")
            return None
    
    def _handle_exit(self) -> None:
        """Handle exit command"""
        stats = self.context_manager.get_task_stats()
        self.speak(
            f"Total {self.total_tasks} tasks complete. "
            f"{self.expert_tasks} expert tasks. Dhanyavaad!"
        )
    
    def _handle_help(self) -> str:
        """Handle help command"""
        help_text = """
        🔷 ShivAI - Autonomous General Intelligence (AGI)
        
        Categories:
        📱 Android Control: "phone unlock", "phone screenshot", "phone battery"
        🗏️ App Builder: "build todo app", "create calculator"
        🔄 Workflows: "run morning workflow", "backup workflow"
        💻 PC Automation: "open notepad", "screenshot", "organize files"
        🎯 Expert Tasks: "create project structure", "analyze performance"
        
        Say "help" anytime for this menu.
        """
        self.speak("Complete help screen par hai")
        print(help_text)
        return help_text
    
    def _handle_status(self) -> Dict[str, Any]:
        """Handle status command"""
        stats = self.context_manager.get_task_stats()
        
        self.speak(
            f"Total tasks: {self.total_tasks}, "
            f"Expert tasks: {self.expert_tasks}, "
            f"Success rate: {stats['success_rate']:.0%}"
        )
        
        return stats
    
    def _handle_android_command(self, parsed: ParsedCommand) -> Any:
        """Handle Android/ADB commands"""
        adb_plugin = self._get_adb_plugin()
        
        if not adb_plugin:
            self.speak("ADB plugin not available. Please enable in settings.")
            return None
        
        context = {
            'intent': parsed.intent.name,
            'entities': parsed.entities
        }
        
        return adb_plugin.handle_command(parsed.raw_text, context)
    
    def _handle_app_builder_command(self, parsed: ParsedCommand) -> Any:
        """Handle app builder commands"""
        app_builder_plugin = self._get_app_builder_plugin()
        
        if not app_builder_plugin:
            self.speak("App builder plugin not available.")
            return None
        
        context = {
            'intent': parsed.intent.name,
            'entities': parsed.entities
        }
        
        result = app_builder_plugin.handle_command(parsed.raw_text, context)
        
        if result:
            self.expert_tasks += 1
        
        return result
    
    def _handle_workflow_command(self, parsed: ParsedCommand) -> Any:
        """Handle workflow commands"""
        workflow_plugin = self._get_workflow_plugin()
        
        if not workflow_plugin:
            self.speak("Workflow plugin not available.")
            return None
        
        context = {
            'intent': parsed.intent.name,
            'entities': parsed.entities
        }
        
        return workflow_plugin.handle_command(parsed.raw_text, context)
    
    def _handle_pattern_command(self, parsed: ParsedCommand) -> Any:
        """Handle pattern learning commands"""
        # Pattern learning is handled by context manager
        if parsed.intent == Intent.PATTERN_LEARN:
            pattern_name = parsed.entities.get('pattern_name', 'custom_pattern')
            self.speak(f"Learning pattern: {pattern_name}. Next commands will be recorded.")
            self.context_manager.set_context('learning_pattern', pattern_name)
            return pattern_name
        
        elif parsed.intent == Intent.PATTERN_EXECUTE:
            pattern_name = parsed.entities.get('pattern_name')
            if not pattern_name:
                self.speak("Pattern name not found.")
                return None
            
            # Load pattern from context
            patterns = self.context_manager.get_context('learned_patterns', {})
            commands = patterns.get(pattern_name)
            
            if commands:
                self.speak(f"Executing pattern: {pattern_name}")
                for cmd in commands:
                    self.process_command(cmd)
                    time.sleep(0.5)
                return f"Executed {len(commands)} commands"
            else:
                self.speak("Pattern not found.")
                return None
    
    def _handle_pc_command(self, parsed: ParsedCommand) -> Any:
        """Handle PC automation commands"""
        # PC automation through automation plugin
        plugins = self.plugin_loader.get_plugins_by_capability("pc_automation")
        
        if not plugins:
            self.speak("PC automation plugin not available.")
            return None
        
        context = {
            'intent': parsed.intent.name,
            'entities': parsed.entities
        }
        
        return plugins[0].handle_command(parsed.raw_text, context)
    
    def _handle_expert_command(self, parsed: ParsedCommand) -> Any:
        """Handle expert-level automation tasks"""
        # Expert tasks through dedicated plugin
        plugins = self.plugin_loader.get_plugins_by_capability("expert_automation")
        
        if not plugins:
            self.speak("Expert automation plugin not available.")
            return None
        
        context = {
            'intent': parsed.intent.name,
            'entities': parsed.entities
        }
        
        return plugins[0].handle_command(parsed.raw_text, context)
    
    def run(self) -> None:
        """
        Main agent execution loop
        
        Continuously listens for commands and processes them.
        """
        print("\n" + "="*65)
        print("🔷 ShivAI - Autonomous General Intelligence (AGI)")
        print("="*65)
        print("✨ India's First Offline Expert Assistant")
        print("🎯 500+ Tasks | 📱 Phone Control | 🗏️ App Builder")
        print("🧠 No LLM Dependency | 💪 Expert-Level Automation")
        print("="*65 + "\n")
        
        self.speak("Namaste! ShivAI AGI system activated. Help boliye commands dekhne ke liye.")
        
        while self.is_active:
            try:
                # Listen for command
                command = self.listen()
                
                # Process command
                if not self.process_command(command):
                    break
            
            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received")
                break
            
            except Exception as e:
                logger.error(f"Unexpected error in main loop: {e}")
                self.speak("System error. Restarting...")
                time.sleep(1)
        
        # Cleanup
        self.shutdown()
    
    def shutdown(self) -> None:
        """Graceful shutdown"""
        logger.info("🔷 ShivAI Agent shutdown initiated")
        
        # Save context
        self.context_manager.close_session()
        
        # Stop task queue
        self.task_queue.stop()
        
        # Unload plugins
        self.plugin_loader.unload_all()
        
        print("\n💾 Saving session data...")
        print("✅ Session saved. Goodbye!")
        
        logger.info("✅ ShivAI Agent shutdown complete")
    
    def execute_text_command(self, command: str) -> Any:
        """
        Execute text command (no voice)
        
        Useful for API/UI integration.
        
        Args:
            command: Text command
            
        Returns:
            Command execution result
        """
        self.process_command(command)
