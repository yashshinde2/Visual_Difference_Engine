"""
Performance Logging Module
Tracks execution times and resource usage for all pipeline stages.
"""

import time
from typing import Dict
from datetime import datetime


class PerformanceTracker:
    """Tracks performance metrics across analysis pipeline."""
    
    def __init__(self):
        self.start_time = time.time()
        self.stages: Dict[str, Dict] = {}
        self.current_stage = None
        self.current_stage_start = None
    
    def start_stage(self, stage_name: str):
        """Start timing a pipeline stage."""
        self.current_stage = stage_name
        self.current_stage_start = time.time()
        if stage_name not in self.stages:
            self.stages[stage_name] = {
                "count": 0,
                "total_time_ms": 0.0,
                "min_time_ms": float('inf'),
                "max_time_ms": 0.0,
            }
    
    def end_stage(self):
        """End timing current stage."""
        if self.current_stage and self.current_stage_start:
            elapsed_ms = (time.time() - self.current_stage_start) * 1000
            stage_data = self.stages[self.current_stage]
            stage_data["count"] += 1
            stage_data["total_time_ms"] += elapsed_ms
            stage_data["min_time_ms"] = min(stage_data["min_time_ms"], elapsed_ms)
            stage_data["max_time_ms"] = max(stage_data["max_time_ms"], elapsed_ms)
    
    def get_total_time_ms(self) -> float:
        """Get total pipeline execution time."""
        return (time.time() - self.start_time) * 1000
    
    def get_stage_time_ms(self, stage_name: str) -> float:
        """Get specific stage time."""
        if stage_name in self.stages:
            return self.stages[stage_name]["total_time_ms"]
        return 0.0
    
    def get_average_stage_time_ms(self, stage_name: str) -> float:
        """Get average time for stage."""
        if stage_name in self.stages:
            data = self.stages[stage_name]
            return data["total_time_ms"] / max(data["count"], 1)
        return 0.0
    
    def get_report(self) -> Dict:
        """Get comprehensive performance report."""
        total_time = self.get_total_time_ms()
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_time_ms": round(total_time, 2),
            "total_time_sec": round(total_time / 1000, 2),
            "stages": {}
        }
        
        for stage_name, data in self.stages.items():
            avg_time = data["total_time_ms"] / max(data["count"], 1)
            report["stages"][stage_name] = {
                "total_time_ms": round(data["total_time_ms"], 2),
                "average_time_ms": round(avg_time, 2),
                "min_time_ms": round(data["min_time_ms"], 2),
                "max_time_ms": round(data["max_time_ms"], 2),
                "call_count": data["count"],
                "percent_of_total": round((data["total_time_ms"] / total_time) * 100, 1) if total_time > 0 else 0,
            }
        
        return report
    
    def print_report(self):
        """Print formatted performance report."""
        report = self.get_report()
        
        print("\n" + "="*60)
        print("PERFORMANCE ANALYSIS REPORT")
        print("="*60)
        print(f"Timestamp: {report['timestamp']}")
        print(f"Total Time: {report['total_time_sec']}s")
        print("-"*60)
        
        for stage_name, times in report["stages"].items():
            print(f"\n{stage_name}:")
            print(f"  Total:    {times['total_time_ms']:>8.2f} ms ({times['percent_of_total']:>5.1f}%)")
            print(f"  Average:  {times['average_time_ms']:>8.2f} ms")
            print(f"  Min/Max:  {times['min_time_ms']:>8.2f} / {times['max_time_ms']:>8.2f} ms")
            print(f"  Calls:    {times['call_count']:>8}")
        
        print("\n" + "="*60)
    
    def to_dict(self) -> Dict:
        """Convert report to dictionary for API response."""
        return self.get_report()
