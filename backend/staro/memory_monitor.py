import psutil
import time
import requests
import threading


def monitor_memory_while_testing():
    """Monitoriše memory usage dok se testovi izvode"""
    process = psutil.Process()
    memory_samples = []

    def sample_memory():
        while True:
            memory_mb = process.memory_info().rss / 1024 / 1024
            memory_samples.append({
                'timestamp': time.time(),
                'memory_mb': round(memory_mb, 2)
            })
            time.sleep(1) # Sample            svake           sekunde

    # Pokreni monitoring u pozadini
    monitor_thread = threading.Thread(target=sample_memory, daemon=True)
    monitor_thread.start()

    print("🖥️  Memory monitoring pokrenut...")
    return memory_samples

# Pokreni ovaj script u drugom terminalu dok se performance test izvodi