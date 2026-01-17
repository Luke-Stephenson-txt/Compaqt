"""
Event system module.

Provides a publish-subscribe event system for
decoupled component communication.
"""

import asyncio
import inspect
import logging
from typing import (
    Any, Callable, Dict, List, Optional, 
    Set, Coroutine, Union
)
from dataclasses import dataclass, field
from enum import Enum, auto
from weakref import WeakSet
import time


# Configure logger
logger = logging.getLogger(__name__)


class EventPriority(Enum):
    """
    Event handler priority levels.
    
    Higher priority handlers are called first.
    """
    LOW = auto()
    NORMAL = auto()
    HIGH = auto()
    CRITICAL = auto()


@dataclass
class Event:
    """
    Base event class.
    
    All events should inherit from this class
    to ensure consistent structure.
    
    Attributes:
        name: Event name/type
        data: Event payload data
        timestamp: When the event was created
        source: Optional source identifier
        propagate: Whether to continue to next handlers
    """
    name: str
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    source: Optional[str] = None
    propagate: bool = True
    
    def stop_propagation(self) -> None:
        """Stop event from reaching remaining handlers."""
        self.propagate = False


@dataclass
class EventHandler:
    """
    Wrapper for event handler functions.
    
    Stores metadata about the handler including
    priority and whether it's async.
    """
    callback: Callable
    priority: EventPriority
    is_async: bool
    once: bool = False
    
    def __post_init__(self):
        """Determine if callback is async."""
        self.is_async = inspect.iscoroutinefunction(self.callback)


class EventEmitter:
    """
    Event emitter with support for sync and async handlers.
    
    Features:
    - Priority-based handler execution
    - Async handler support
    - One-time handlers
    - Event propagation control
    - Wildcard subscriptions
    """
    
    def __init__(self):
        """Initialize the event emitter."""
        self._handlers: Dict[str, List[EventHandler]] = {}
        self._wildcard_handlers: List[EventHandler] = []
        self._event_history: List[Event] = []
        self._max_history = 100
    
    def on(
        self,
        event_name: str,
        callback: Callable,
        priority: EventPriority = EventPriority.NORMAL
    ) -> Callable:
        """
        Register an event handler.
        
        Args:
            event_name: Name of event to listen for
            callback: Handler function
            priority: Handler priority
            
        Returns:
            The callback function (for decorator use)
        """
        handler = EventHandler(
            callback=callback,
            priority=priority,
            is_async=False  # Will be set in __post_init__
        )
        
        if event_name == "*":
            self._wildcard_handlers.append(handler)
        else:
            if event_name not in self._handlers:
                self._handlers[event_name] = []
            self._handlers[event_name].append(handler)
            
            # Sort by priority (highest first)
            self._handlers[event_name].sort(
                key=lambda h: h.priority.value,
                reverse=True
            )
        
        return callback
    
    def once(
        self,
        event_name: str,
        callback: Callable,
        priority: EventPriority = EventPriority.NORMAL
    ) -> Callable:
        """
        Register a one-time event handler.
        
        The handler will be automatically removed
        after being called once.
        
        Args:
            event_name: Name of event to listen for
            callback: Handler function
            priority: Handler priority
            
        Returns:
            The callback function
        """
        handler = EventHandler(
            callback=callback,
            priority=priority,
            is_async=False,
            once=True
        )
        
        if event_name not in self._handlers:
            self._handlers[event_name] = []
        self._handlers[event_name].append(handler)
        
        return callback
    
    def off(
        self,
        event_name: str,
        callback: Optional[Callable] = None
    ) -> None:
        """
        Remove event handler(s).
        
        Args:
            event_name: Event name
            callback: Specific callback to remove, or None for all
        """
        if event_name == "*":
            if callback is None:
                self._wildcard_handlers.clear()
            else:
                self._wildcard_handlers = [
                    h for h in self._wildcard_handlers
                    if h.callback != callback
                ]
        elif event_name in self._handlers:
            if callback is None:
                del self._handlers[event_name]
            else:
                self._handlers[event_name] = [
                    h for h in self._handlers[event_name]
                    if h.callback != callback
                ]
    
    def emit(
        self,
        event_name: str,
        data: Optional[Dict[str, Any]] = None,
        source: Optional[str] = None
    ) -> Event:
        """
        Emit an event synchronously.
        
        Args:
            event_name: Name of event to emit
            data: Event data payload
            source: Event source identifier
            
        Returns:
            The emitted Event object
        """
        event = Event(
            name=event_name,
            data=data or {},
            source=source
        )
        
        # Record in history
        self._record_event(event)
        
        # Get all applicable handlers
        handlers = self._get_handlers(event_name)
        
        # Execute handlers
        handlers_to_remove = []
        
        for handler in handlers:
            if not event.propagate:
                break
            
            try:
                if handler.is_async:
                    # Run async handler in event loop
                    loop = asyncio.get_event_loop()
                    loop.run_until_complete(handler.callback(event))
                else:
                    handler.callback(event)
                
                if handler.once:
                    handlers_to_remove.append(handler)
                    
            except Exception as e:
                logger.error(f"Error in event handler: {e}")
        
        # Remove one-time handlers
        for handler in handlers_to_remove:
            self._remove_handler(event_name, handler)
        
        return event
    
    async def emit_async(
        self,
        event_name: str,
        data: Optional[Dict[str, Any]] = None,
        source: Optional[str] = None
    ) -> Event:
        """
        Emit an event asynchronously.
        
        Args:
            event_name: Name of event to emit
            data: Event data payload
            source: Event source identifier
            
        Returns:
            The emitted Event object
        """
        event = Event(
            name=event_name,
            data=data or {},
            source=source
        )
        
        self._record_event(event)
        handlers = self._get_handlers(event_name)
        
        for handler in handlers:
            if not event.propagate:
                break
            
            try:
                if handler.is_async:
                    await handler.callback(event)
                else:
                    handler.callback(event)
            except Exception as e:
                logger.error(f"Error in async event handler: {e}")
        
        return event
    
    def _get_handlers(self, event_name: str) -> List[EventHandler]:
        """Get all handlers for an event including wildcards."""
        handlers = list(self._wildcard_handlers)
        
        if event_name in self._handlers:
            handlers.extend(self._handlers[event_name])
        
        # Sort combined list by priority
        handlers.sort(key=lambda h: h.priority.value, reverse=True)
        
        return handlers
    
    def _remove_handler(
        self,
        event_name: str,
        handler: EventHandler
    ) -> None:
        """Remove a specific handler."""
        if event_name in self._handlers:
            try:
                self._handlers[event_name].remove(handler)
            except ValueError:
                pass
    
    def _record_event(self, event: Event) -> None:
        """Record event in history."""
        self._event_history.append(event)
        
        # Trim history if needed
        if len(self._event_history) > self._max_history:
            self._event_history = self._event_history[-self._max_history:]
    
    def get_history(
        self,
        event_name: Optional[str] = None,
        limit: int = 10
    ) -> List[Event]:
        """
        Get recent event history.
        
        Args:
            event_name: Filter by event name
            limit: Maximum events to return
            
        Returns:
            List of recent events
        """
        events = self._event_history
        
        if event_name:
            events = [e for e in events if e.name == event_name]
        
        return events[-limit:]
