import time
import functools
import cProfile
import pstats
import io
import os

def time_function(func):
    """
    Decorator that measures the execution time of a function and prints it.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        run_time = end_time - start_time
        print(f"\n⏱️ {func.__name__} executed in {run_time:.4f} seconds")
        return result
    return wrapper

def profile_function(func):
    """
    Decorator that profiles a function and saves the stats to a file.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()
        result = func(*args, **kwargs)
        profiler.disable()
        
        s = io.StringIO()
        sortby = pstats.SortKey.CUMULATIVE
        ps = pstats.Stats(profiler, stream=s).sort_stats(sortby)
        ps.print_stats()
        
        report_path = f"performance_reports/{func.__name__}_profile.txt"
        os.makedirs(os.path.dirname(report_path), exist_ok=True)

        with open(report_path, "w") as f:
            f.write(s.getvalue())
            
        print(f"\n📊 Performance profile for {func.__name__} saved to {report_path}")
        
        return result
    return wrapper
