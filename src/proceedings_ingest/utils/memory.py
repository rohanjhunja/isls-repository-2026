import os
import sys
import gc
import logging

logger = logging.getLogger(__name__)


def get_rss_memory_gb() -> float:
    """Return the RSS memory usage of the current process in Gigabytes."""
    try:
        import psutil
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / (1024 ** 3)
    except ImportError:
        import resource
        rusage = resource.getrusage(resource.RUSAGE_SELF)
        # On macOS, ru_maxrss is reported in bytes.
        if sys.platform == "darwin":
            return rusage.ru_maxrss / (1024 ** 3)
        # On Linux, ru_maxrss is reported in KB.
        return rusage.ru_maxrss / (1024 ** 2)


def check_memory(max_memory_gb: float = 8.0) -> float:
    """Check process memory usage and raise MemoryError if max_memory_gb limit is exceeded.

    Returns the current memory usage in GB.
    """
    current_gb = get_rss_memory_gb()
    if current_gb > max_memory_gb:
        force_garbage_collection()
        current_gb = get_rss_memory_gb()
        if current_gb > max_memory_gb:
            raise MemoryError(
                f"Memory ceiling exceeded: Process RSS memory is {current_gb:.2f} GB "
                f"(limit is {max_memory_gb:.2f} GB)."
            )
    return current_gb


def force_garbage_collection() -> float:
    """Trigger explicit Python garbage collection and return memory usage after cleanup."""
    gc.collect()
    return get_rss_memory_gb()
