"""
Layer Painter Logging System

Comprehensive logging infrastructure for Layer Painter with:
- Debug logging for all operations
- Error aggregation and reporting
- Performance metrics tracking
- Log file persistence
- Configurable log levels

Usage:
    from layer_painter.logging import get_logger
    
    logger = get_logger("module_name")
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    
    # Get metrics
    metrics = get_metrics()
    report_metrics()
"""

import logging
import time
import functools
import traceback
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from collections import defaultdict
from datetime import datetime


# ============================================================================
# Core Logging Setup
# ============================================================================

# Global logger instance
_logger = None
_metrics = None
_error_log = None

def configure_logging(log_level: int = logging.INFO, log_file: Optional[str] = None) -> None:
    """
    Configure global logging system.
    
    Args:
        log_level (int): Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file (str): Path to log file (optional)
    """
    global _logger, _metrics, _error_log
    
    # Create logger
    _logger = logging.getLogger("LayerPainter")
    _logger.setLevel(log_level)
    _logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    
    # Formatter
    formatter = logging.Formatter(
        "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)
    _logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        try:
            log_path = Path(log_file).parent
            log_path.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file, mode='a')
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            _logger.addHandler(file_handler)
            _logger.info(f"Logging to file: {log_file}")
        except Exception as e:
            _logger.warning(f"Failed to setup file logging: {e}")
    
    # Initialize metrics
    _metrics = MetricsCollector()
    _error_log = ErrorLog()


def get_logger(name: str) -> logging.Logger:
    """
    Get or create logger for module.
    
    Args:
        name (str): Module name
    
    Returns:
        Logger instance
    
    Example:
        logger = get_logger("layers")
        logger.debug("Creating layer...")
    """
    global _logger
    if _logger is None:
        configure_logging()
    
    return logging.getLogger(f"LayerPainter.{name}")


# ============================================================================
# Performance Metrics
# ============================================================================

@dataclass
class OperationMetric:
    """Single operation performance metric."""
    name: str
    duration: float  # seconds
    timestamp: float
    success: bool
    error: Optional[str] = None
    

class MetricsCollector:
    """Collect and aggregate performance metrics."""
    
    def __init__(self):
        self.operations: List[OperationMetric] = []
        self.counters: Dict[str, int] = defaultdict(int)
        self.timings: Dict[str, List[float]] = defaultdict(list)
    
    def record_operation(self, name: str, duration: float, success: bool = True, error: Optional[str] = None):
        """
        Record operation metric.
        
        Args:
            name (str): Operation name
            duration (float): Duration in seconds
            success (bool): Whether operation succeeded
            error (str): Error message if failed
        """
        metric = OperationMetric(
            name=name,
            duration=duration,
            timestamp=time.time(),
            success=success,
            error=error
        )
        self.operations.append(metric)
        self.timings[name].append(duration)
        self.counters[f"{name}_total"] += 1
        if not success:
            self.counters[f"{name}_errors"] += 1
    
    def increment_counter(self, name: str, value: int = 1):
        """Increment named counter."""
        self.counters[name] += value
    
    def get_stats(self, operation_name: str) -> Dict[str, float]:
        """
        Get statistics for operation.
        
        Args:
            operation_name (str): Operation name
        
        Returns:
            Dict with 'count', 'total_time', 'avg_time', 'min_time', 'max_time'
        """
        timings = self.timings.get(operation_name, [])
        if not timings:
            return {}
        
        return {
            "count": len(timings),
            "total_time": sum(timings),
            "avg_time": sum(timings) / len(timings),
            "min_time": min(timings),
            "max_time": max(timings),
        }
    
    def get_all_stats(self) -> Dict[str, Dict[str, float]]:
        """Get statistics for all operations."""
        return {op_name: self.get_stats(op_name) for op_name in self.timings.keys()}
    
    def get_counters(self) -> Dict[str, int]:
        """Get all counters."""
        return dict(self.counters)
    
    def reset(self):
        """Clear all metrics."""
        self.operations.clear()
        self.counters.clear()
        self.timings.clear()


def get_metrics() -> MetricsCollector:
    """Get global metrics collector."""
    global _metrics
    if _metrics is None:
        configure_logging()
    return _metrics


def record_metric(name: str, duration: float, success: bool = True, error: Optional[str] = None):
    """Record performance metric."""
    get_metrics().record_operation(name, duration, success, error)


def report_metrics() -> str:
    """
    Generate metrics report.
    
    Returns:
        Formatted metrics report string
    """
    metrics = get_metrics()
    stats = metrics.get_all_stats()
    counters = metrics.get_counters()
    
    lines = [
        "=" * 60,
        "Layer Painter Performance Metrics",
        "=" * 60,
        ""
    ]
    
    if stats:
        lines.append("Operation Timings:")
        lines.append("-" * 60)
        for op_name, stat in sorted(stats.items()):
            lines.append(
                f"  {op_name:30} | "
                f"Count: {stat.get('count', 0):4} | "
                f"Avg: {stat.get('avg_time', 0):.3f}s | "
                f"Total: {stat.get('total_time', 0):.3f}s"
            )
        lines.append("")
    
    if counters:
        lines.append("Counters:")
        lines.append("-" * 60)
        for counter_name, value in sorted(counters.items()):
            lines.append(f"  {counter_name:40} : {value:6}")
        lines.append("")
    
    lines.append("=" * 60)
    
    return "\n".join(lines)


# ============================================================================
# Error Logging & Aggregation
# ============================================================================

@dataclass
class ErrorRecord:
    """Single error record."""
    message: str
    exception_type: str
    traceback: str
    timestamp: float
    context: Dict[str, Any] = field(default_factory=dict)


class ErrorLog:
    """Aggregate and track errors."""
    
    def __init__(self, max_errors: int = 100):
        self.errors: List[ErrorRecord] = []
        self.max_errors = max_errors
        self.error_counts: Dict[str, int] = defaultdict(int)
    
    def record_error(self, exc: Exception, context: Optional[Dict[str, Any]] = None):
        """
        Record error for aggregation.
        
        Args:
            exc (Exception): Exception that occurred
            context (dict): Additional context information
        """
        error_record = ErrorRecord(
            message=str(exc),
            exception_type=type(exc).__name__,
            traceback=traceback.format_exc(),
            timestamp=time.time(),
            context=context or {}
        )
        
        self.errors.append(error_record)
        self.error_counts[type(exc).__name__] += 1
        
        # Keep only recent errors
        if len(self.errors) > self.max_errors:
            self.errors = self.errors[-self.max_errors:]
    
    def get_recent_errors(self, count: int = 10) -> List[ErrorRecord]:
        """Get most recent errors."""
        return self.errors[-count:]
    
    def get_error_summary(self) -> Dict[str, int]:
        """Get count of each error type."""
        return dict(self.error_counts)
    
    def clear(self):
        """Clear error log."""
        self.errors.clear()
        self.error_counts.clear()
    
    def generate_report(self) -> str:
        """Generate error report."""
        lines = [
            "=" * 60,
            "Layer Painter Error Report",
            "=" * 60,
            ""
        ]
        
        if self.error_counts:
            lines.append("Error Summary:")
            lines.append("-" * 60)
            for error_type, count in sorted(self.error_counts.items(), key=lambda x: x[1], reverse=True):
                lines.append(f"  {error_type:40} : {count:6} occurrences")
            lines.append("")
        
        if self.errors:
            lines.append(f"Recent Errors (last {len(self.errors)}):")
            lines.append("-" * 60)
            for i, error in enumerate(self.get_recent_errors(5), 1):
                lines.append(f"\n  [{i}] {error.exception_type}: {error.message}")
                if error.context:
                    lines.append(f"      Context: {error.context}")
            lines.append("")
        
        lines.append("=" * 60)
        return "\n".join(lines)


def get_error_log() -> ErrorLog:
    """Get global error log."""
    global _error_log
    if _error_log is None:
        configure_logging()
    return _error_log


# ============================================================================
# Decorators for Automatic Logging
# ============================================================================

def log_operation(operation_name: str = None, log_args: bool = False) -> Callable:
    """
    Decorator to log function execution.
    
    Args:
        operation_name (str): Name for logs (defaults to function name)
        log_args (bool): Whether to log function arguments
    
    Example:
        @log_operation("paint_channel")
        def paint_channel(layer, channel):
            ...
    """
    def decorator(func: Callable) -> Callable:
        op_name = operation_name or func.__name__
        logger = get_logger(func.__module__)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            # Log start
            if log_args:
                logger.debug(f"Starting {op_name} with args={args}, kwargs={kwargs}")
            else:
                logger.debug(f"Starting {op_name}")
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(f"Completed {op_name} in {duration:.3f}s")
                record_metric(op_name, duration, success=True)
                return result
            
            except Exception as exc:
                duration = time.time() - start_time
                logger.error(f"Failed {op_name} after {duration:.3f}s: {exc}")
                get_error_log().record_error(exc, {"operation": op_name})
                record_metric(op_name, duration, success=False, error=str(exc))
                raise
        
        return wrapper
    return decorator


def log_performance(threshold_ms: float = 100) -> Callable:
    """
    Decorator to log slow operations.
    
    Args:
        threshold_ms (float): Warn if operation takes longer than this (milliseconds)
    
    Example:
        @log_performance(threshold_ms=500)
        def expensive_operation():
            ...
    """
    def decorator(func: Callable) -> Callable:
        logger = get_logger(func.__module__)
        threshold_s = threshold_ms / 1000.0
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                return func(*args, **kwargs)
            finally:
                duration = time.time() - start_time
                if duration > threshold_s:
                    logger.warning(
                        f"{func.__name__} took {duration*1000:.1f}ms "
                        f"(threshold: {threshold_ms}ms)"
                    )
        
        return wrapper
    return decorator


def log_cache_operation(cache_name: str) -> Callable:
    """
    Decorator to log cache operations.
    
    Args:
        cache_name (str): Name of cache
    
    Example:
        @log_cache_operation("channel_mix_nodes")
        def get_channel_mix_node(layer, channel_uid):
            ...
    """
    def decorator(func: Callable) -> Callable:
        logger = get_logger(func.__module__)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            found = result is not None
            logger.debug(f"{cache_name} lookup: {'HIT' if found else 'MISS'}")
            return result
        
        return wrapper
    return decorator


# ============================================================================
# Context Managers for Logging Blocks
# ============================================================================

class LogContext:
    """Context manager for logging operations."""
    
    def __init__(self, operation_name: str, logger: Optional[logging.Logger] = None):
        """
        Create log context.
        
        Args:
            operation_name (str): Name of operation
            logger (Logger): Logger to use (optional)
        
        Example:
            with LogContext("bake_textures") as ctx:
                # do work
                ctx.log("Step 1 complete")
        """
        self.operation_name = operation_name
        self.logger = logger or get_logger("context")
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        self.logger.info(f"Starting: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        if exc_type is None:
            self.logger.info(f"Completed: {self.operation_name} ({duration:.3f}s)")
            record_metric(self.operation_name, duration, success=True)
        else:
            self.logger.error(f"Failed: {self.operation_name} ({duration:.3f}s): {exc_val}")
            get_error_log().record_error(exc_val, {"operation": self.operation_name})
            record_metric(self.operation_name, duration, success=False, error=str(exc_val))
        return False
    
    def log(self, message: str, level: int = logging.INFO):
        """Log message within context."""
        self.logger.log(level, f"[{self.operation_name}] {message}")


# ============================================================================
# Convenience Functions
# ============================================================================

def log_state_change(old_value: Any, new_value: Any, property_name: str) -> None:
    """Log state change."""
    logger = get_logger("state")
    logger.debug(f"State change: {property_name} = {old_value} → {new_value}")


def log_cache_clear(cache_name: str, item_count: int = None) -> None:
    """Log cache clearing."""
    logger = get_logger("cache")
    if item_count is not None:
        logger.debug(f"Cleared {cache_name} cache ({item_count} items)")
    else:
        logger.debug(f"Cleared {cache_name} cache")


def log_node_operation(operation: str, node_name: str, success: bool = True) -> None:
    """Log node tree operation."""
    logger = get_logger("nodes")
    status = "OK" if success else "FAILED"
    logger.debug(f"Node operation [{status}]: {operation} on '{node_name}'")


def log_ui_event(event_name: str, context: Dict[str, Any] = None) -> None:
    """Log UI event."""
    logger = get_logger("ui")
    msg = f"UI event: {event_name}"
    if context:
        msg += f" (context: {context})"
    logger.debug(msg)


# ============================================================================
# Summary Report Generation
# ============================================================================

def generate_debug_report() -> str:
    """
    Generate comprehensive debug report.
    
    Returns:
        Formatted debug report string
    """
    report_parts = [
        "=" * 70,
        f"Layer Painter Debug Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 70,
        "",
    ]
    
    # Metrics
    report_parts.append(report_metrics())
    
    # Errors
    report_parts.append("")
    report_parts.append(get_error_log().generate_report())
    
    # Summary
    metrics = get_metrics()
    total_operations = len(metrics.operations)
    failed_operations = sum(1 for op in metrics.operations if not op.success)
    
    report_parts.append("")
    report_parts.append("Summary:")
    report_parts.append(f"  Total operations: {total_operations}")
    report_parts.append(f"  Failed operations: {failed_operations}")
    report_parts.append(f"  Success rate: {(1 - failed_operations/total_operations)*100:.1f}%" if total_operations > 0 else "  N/A")
    
    return "\n".join(report_parts)


def save_debug_report(filepath: str) -> None:
    """
    Save debug report to file.
    
    Args:
        filepath (str): Where to save report
    """
    report = generate_debug_report()
    
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w') as f:
        f.write(report)
    
    logger = get_logger("logging")
    logger.info(f"Debug report saved to: {filepath}")


# Initialize on import
configure_logging()
