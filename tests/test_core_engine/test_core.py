"""
Tests for CommandParser

Tests intent matching, entity extraction, and language detection.
"""

import pytest
from shivai.core_engine.command_parser import CommandParser, Intent, ParsedCommand


class TestCommandParser:
    """Test suite for CommandParser"""
    
    @pytest.fixture
    def parser(self):
        """Create parser instance"""
        return CommandParser()
    
    def test_exit_intent(self, parser):
        """Test exit command recognition"""
        commands = ["exit", "quit", "bye", "band karo"]
        
        for cmd in commands:
            result = parser.parse(cmd)
            assert result.intent == Intent.EXIT
            assert result.confidence > 0.5
    
    def test_help_intent(self, parser):
        """Test help command recognition"""
        commands = ["help", "commands", "kya kar sakte"]
        
        for cmd in commands:
            result = parser.parse(cmd)
            assert result.intent == Intent.HELP
    
    def test_android_unlock(self, parser):
        """Test Android unlock command"""
        commands = ["phone unlock karo", "unlock phone", "mobile unlock"]
        
        for cmd in commands:
            result = parser.parse(cmd)
            assert result.intent == Intent.ANDROID_UNLOCK
    
    def test_app_builder_intent(self, parser):
        """Test app builder commands"""
        result = parser.parse("build todo app")
        assert result.intent == Intent.APP_BUILD
        assert 'app_type' in result.entities
        assert result.entities['app_type'] == 'todo'
    
    def test_workflow_run(self, parser):
        """Test workflow execution commands"""
        result = parser.parse("run morning workflow")
        assert result.intent == Intent.WORKFLOW_RUN
        assert result.entities.get('workflow_name') == 'morning_routine'
    
    def test_pc_open_app(self, parser):
        """Test PC app opening"""
        result = parser.parse("open notepad")
        assert result.intent == Intent.PC_OPEN_APP
        assert 'app_name' in result.entities
        assert result.entities['app_name'] == 'notepad'
    
    def test_volume_control(self, parser):
        """Test volume control commands"""
        result = parser.parse("volume up")
        assert result.intent == Intent.PC_VOLUME
        assert result.entities['direction'] == 'up'
        
        result = parser.parse("volume down")
        assert result.entities['direction'] == 'down'
    
    def test_language_detection(self, parser):
        """Test language detection"""
        # Hindi
        result = parser.parse("phone unlock karo")
        assert result.language == 'hi'
        
        # English
        result = parser.parse("open calculator")
        assert result.language == 'en'
        
        # Hinglish
        result = parser.parse("notepad kholo")
        assert result.language in ['hi', 'hinglish']
    
    def test_entity_extraction_numbers(self, parser):
        """Test number extraction"""
        result = parser.parse("create 5 folders")
        assert 'numbers' in result.entities
        assert 5 in result.entities['numbers']
    
    def test_unknown_intent(self, parser):
        """Test unknown command handling"""
        result = parser.parse("some random gibberish xyz123")
        assert result.intent == Intent.UNKNOWN
        assert result.confidence < 0.5
    
    def test_confidence_scores(self, parser):
        """Test confidence scoring"""
        # Clear match should have high confidence
        result = parser.parse("exit")
        assert result.confidence > 0.7
        
        # Partial match should have lower confidence
        result = parser.parse("maybe exit later")
        assert result.confidence < result.confidence  # Still matches but less confident
    
    def test_case_insensitivity(self, parser):
        """Test case insensitive matching"""
        result1 = parser.parse("OPEN NOTEPAD")
        result2 = parser.parse("open notepad")
        result3 = parser.parse("OpEn NoTePaD")
        
        assert result1.intent == result2.intent == result3.intent
    
    def test_intent_description(self, parser):
        """Test getting human-readable intent descriptions"""
        desc = parser.get_intent_description(Intent.APP_BUILD)
        assert "Build application" in desc
        
        desc = parser.get_intent_description(Intent.ANDROID_UNLOCK)
        assert "Unlock" in desc and "phone" in desc.lower()
