"""Smoke tests for ShivAI core engine.

Runnable with pytest, or directly:  python3 tests/test_smoke.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shivai.core_engine import Config, PluginLoader, BasePlugin, TaskQueue
from shivai.core_engine.task_queue import Task, TaskPriority


def test_config_loads():
    c = Config()
    assert c is not None


def test_task_dataclass_field_order():
    # Regression test: 'func' must be constructible alongside defaulted fields
    t = Task(priority=TaskPriority.NORMAL, func=lambda: 1)
    assert t.func() == 1
    assert t.priority == TaskPriority.NORMAL
    assert t.task_id


def test_task_queue_executes():
    q = TaskQueue(max_workers=1)
    q.start()
    try:
        tid = q.submit(lambda x: x * 2, 21, priority=TaskPriority.HIGH)
        res = q.get_result(tid, timeout=10)
        assert res is not None and res.success and res.result == 42
    finally:
        q.stop()


def test_plugin_loader_instantiates():
    loader = PluginLoader()
    assert loader is not None


if __name__ == "__main__":
    test_config_loads()
    test_task_dataclass_field_order()
    test_task_queue_executes()
    test_plugin_loader_instantiates()
    print("smoke test: 4 passed")
