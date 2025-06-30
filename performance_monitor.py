
"""
Performance Monitoring Module
===========================

Tracks performance improvements and provides real-time metrics.
"""

import time
import logging
import threading
from typing import Dict, List
from collections import defaultdict, deque


class PerformanceMonitor:
    """Monitor and track performance metrics."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics = defaultdict(list)
        self.start_times = {}
        self.lock = threading.Lock()
    
    def start_timer(self, operation: str) -> None:
        """Start timing an operation."""
        with self.lock:
            self.start_times[operation] = time.time()
    
    def end_timer(self, operation: str) -> float:
        """End timing and record duration."""
        with self.lock:
            if operation in self.start_times:
                duration = time.time() - self.start_times[operation]
                self.metrics[operation].append(duration)
                del self.start_times[operation]
                return duration
        return 0.0
    
    def get_average_time(self, operation: str) -> float:
        """Get average time for an operation."""
        with self.lock:
            times = self.metrics[operation]
            return sum(times) / len(times) if times else 0.0
    
    def get_performance_report(self) -> str:
        """Generate performance report."""
        report = "\n" + "="*60 + "\n"
        report += "PERFORMANCE REPORT\n"
        report += "="*60 + "\n"
        
        with self.lock:
            for operation, times in self.metrics.items():
                if times:
                    avg_time = sum(times) / len(times)
                    total_time = sum(times)
                    count = len(times)
                    
                    report += f"{operation}:\n"
                    report += f"  Average: {avg_time:.2f}s\n"
                    report += f"  Total: {total_time:.2f}s\n" 
                    report += f"  Count: {count}\n"
                    if count > 0:
                        report += f"  Rate: {count/total_time:.1f} ops/sec\n"
                    report += "\n"
        
        return report


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


def monitor_performance(operation_name: str):
    """Decorator to monitor function performance."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            performance_monitor.start_timer(operation_name)
            try:
                result = func(*args, **kwargs)
                duration = performance_monitor.end_timer(operation_name)
                logging.getLogger(__name__).debug(f"⚡ {operation_name}: {duration:.2f}s")
                return result
            except Exception as e:
                performance_monitor.end_timer(operation_name)
                raise
        return wrapper
    return decorator
