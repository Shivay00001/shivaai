"""
Task Queue for ShivAI

Manages asynchronous task execution with priority, retries, and scheduling.
Supports concurrent task execution with thread pool.
"""

import time
import threading
from queue import PriorityQueue, Empty
from typing import Callable, Any, Optional, Dict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import IntEnum
import uuid
import logging

logger = logging.getLogger(__name__)


class TaskPriority(IntEnum):
    """Task priority levels (lower number = higher priority)"""
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    BACKGROUND = 4


@dataclass(order=True)
class Task:
    """
    Task to be executed by the queue
    
    Tasks are ordered by priority and creation time.
    """
    priority: TaskPriority = field(compare=True)
    created_at: float = field(default_factory=time.time, compare=True)
    
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()), compare=False)
    func: Callable = field(compare=False)
    args: tuple = field(default_factory=tuple, compare=False)
    kwargs: dict = field(default_factory=dict, compare=False)
    
    max_retries: int = field(default=0, compare=False)
    retry_count: int = field(default=0, compare=False)
    retry_delay: float = field(default=1.0, compare=False)
    
    timeout: Optional[float] = field(default=None, compare=False)
    
    callback: Optional[Callable] = field(default=None, compare=False)
    error_callback: Optional[Callable] = field(default=None, compare=False)


@dataclass
class TaskResult:
    """Task execution result"""
    task_id: str
    success: bool
    result: Any = None
    error: Optional[Exception] = None
    execution_time: float = 0.0
    retry_count: int = 0


class TaskQueue:
    """
    Thread-safe task queue with priority, retries, and concurrency control.
    
    Features:
    - Priority-based execution
    - Automatic retries with exponential backoff
    - Concurrent execution with thread pool
    - Task timeout support
    - Callback on completion/error
    - Task cancellation
    """
    
    def __init__(self, max_workers: int = 3):
        self.max_workers = max_workers
        
        self.queue: PriorityQueue = PriorityQueue()
        self.workers: list[threading.Thread] = []
        self.running = False
        
        self.pending_tasks: Dict[str, Task] = {}
        self.completed_tasks: Dict[str, TaskResult] = {}
        
        self.lock = threading.Lock()
        
        logger.info(f"TaskQueue initialized with {max_workers} workers")
    
    def start(self) -> None:
        """Start worker threads"""
        if self.running:
            logger.warning("TaskQueue already running")
            return
        
        self.running = True
        
        for i in range(self.max_workers):
            worker = threading.Thread(
                target=self._worker,
                name=f"TaskWorker-{i}",
                daemon=True
            )
            worker.start()
            self.workers.append(worker)
        
        logger.info(f"Started {self.max_workers} worker threads")
    
    def stop(self, timeout: float = 5.0) -> None:
        """Stop all workers gracefully"""
        if not self.running:
            return
        
        logger.info("Stopping TaskQueue...")
        self.running = False
        
        # Wait for workers to finish
        for worker in self.workers:
            worker.join(timeout=timeout)
        
        self.workers.clear()
        logger.info("TaskQueue stopped")
    
    def submit(
        self,
        func: Callable,
        *args,
        priority: TaskPriority = TaskPriority.NORMAL,
        max_retries: int = 0,
        retry_delay: float = 1.0,
        timeout: Optional[float] = None,
        callback: Optional[Callable] = None,
        error_callback: Optional[Callable] = None,
        **kwargs
    ) -> str:
        """
        Submit task to queue
        
        Args:
            func: Function to execute
            *args: Positional arguments
            priority: Task priority
            max_retries: Maximum retry attempts
            retry_delay: Delay between retries (seconds)
            timeout: Task timeout (seconds)
            callback: Called on success with result
            error_callback: Called on error with exception
            **kwargs: Keyword arguments
            
        Returns:
            task_id: Unique task identifier
        """
        task = Task(
            priority=priority,
            func=func,
            args=args,
            kwargs=kwargs,
            max_retries=max_retries,
            retry_delay=retry_delay,
            timeout=timeout,
            callback=callback,
            error_callback=error_callback
        )
        
        with self.lock:
            self.pending_tasks[task.task_id] = task
        
        self.queue.put(task)
        logger.debug(f"Submitted task {task.task_id} with priority {priority.name}")
        
        return task.task_id
    
    def _worker(self) -> None:
        """Worker thread that executes tasks from queue"""
        while self.running:
            try:
                # Get task with timeout to allow checking running flag
                task = self.queue.get(timeout=0.5)
            except Empty:
                continue
            
            try:
                result = self._execute_task(task)
                
                # Store result
                with self.lock:
                    self.completed_tasks[task.task_id] = result
                    if task.task_id in self.pending_tasks:
                        del self.pending_tasks[task.task_id]
                
                # Call callback
                if result.success and task.callback:
                    try:
                        task.callback(result.result)
                    except Exception as e:
                        logger.error(f"Callback error for task {task.task_id}: {e}")
                
                elif not result.success and task.error_callback:
                    try:
                        task.error_callback(result.error)
                    except Exception as e:
                        logger.error(f"Error callback error for task {task.task_id}: {e}")
                
            except Exception as e:
                logger.error(f"Unexpected error in worker: {e}")
            
            finally:
                self.queue.task_done()
    
    def _execute_task(self, task: Task) -> TaskResult:
        """
        Execute task with timeout and retry logic
        
        Returns:
            TaskResult with execution details
        """
        start_time = time.time()
        
        try:
            # Execute with timeout if specified
            if task.timeout:
                result = self._execute_with_timeout(task)
            else:
                result = task.func(*task.args, **task.kwargs)
            
            execution_time = time.time() - start_time
            
            logger.debug(f"Task {task.task_id} completed in {execution_time:.2f}s")
            
            return TaskResult(
                task_id=task.task_id,
                success=True,
                result=result,
                execution_time=execution_time,
                retry_count=task.retry_count
            )
        
        except Exception as e:
            execution_time = time.time() - start_time
            
            logger.error(f"Task {task.task_id} failed: {e}")
            
            # Retry logic
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                
                # Exponential backoff
                delay = task.retry_delay * (2 ** (task.retry_count - 1))
                
                logger.info(f"Retrying task {task.task_id} ({task.retry_count}/{task.max_retries}) in {delay:.1f}s")
                
                time.sleep(delay)
                
                # Re-queue task
                self.queue.put(task)
                
                # Return temporary result
                return TaskResult(
                    task_id=task.task_id,
                    success=False,
                    error=e,
                    execution_time=execution_time,
                    retry_count=task.retry_count
                )
            
            else:
                return TaskResult(
                    task_id=task.task_id,
                    success=False,
                    error=e,
                    execution_time=execution_time,
                    retry_count=task.retry_count
                )
    
    def _execute_with_timeout(self, task: Task) -> Any:
        """Execute task with timeout"""
        result_container = []
        exception_container = []
        
        def target():
            try:
                result = task.func(*task.args, **task.kwargs)
                result_container.append(result)
            except Exception as e:
                exception_container.append(e)
        
        thread = threading.Thread(target=target, daemon=True)
        thread.start()
        thread.join(timeout=task.timeout)
        
        if thread.is_alive():
            raise TimeoutError(f"Task exceeded timeout of {task.timeout}s")
        
        if exception_container:
            raise exception_container[0]
        
        return result_container[0] if result_container else None
    
    def get_result(self, task_id: str, timeout: Optional[float] = None) -> Optional[TaskResult]:
        """
        Get task result (blocking if timeout specified)
        
        Args:
            task_id: Task identifier
            timeout: Maximum time to wait (seconds)
            
        Returns:
            TaskResult if available, None otherwise
        """
        start_time = time.time()
        
        while True:
            with self.lock:
                if task_id in self.completed_tasks:
                    return self.completed_tasks[task_id]
            
            if timeout is not None and (time.time() - start_time) >= timeout:
                return None
            
            time.sleep(0.1)
    
    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel pending task
        
        Note: Cannot cancel already executing tasks
        
        Returns:
            True if cancelled, False if not found or already executing
        """
        with self.lock:
            if task_id in self.pending_tasks:
                del self.pending_tasks[task_id]
                logger.info(f"Cancelled task {task_id}")
                return True
        
        return False
    
    def get_queue_size(self) -> int:
        """Get number of tasks in queue"""
        return self.queue.qsize()
    
    def get_pending_count(self) -> int:
        """Get number of pending tasks"""
        with self.lock:
            return len(self.pending_tasks)
    
    def get_completed_count(self) -> int:
        """Get number of completed tasks"""
        with self.lock:
            return len(self.completed_tasks)
    
    def clear_completed(self) -> None:
        """Clear completed task history"""
        with self.lock:
            self.completed_tasks.clear()
        logger.info("Cleared completed task history")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        with self.lock:
            pending = len(self.pending_tasks)
            completed = len(self.completed_tasks)
            
            success = sum(1 for r in self.completed_tasks.values() if r.success)
            failed = completed - success
        
        return {
            'queue_size': self.get_queue_size(),
            'pending': pending,
            'completed': completed,
            'success': success,
            'failed': failed,
            'success_rate': success / completed if completed > 0 else 0,
            'workers': len(self.workers),
            'running': self.running
        }
