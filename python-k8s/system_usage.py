# system_usage.py
import psutil

def system_health():
    print("🔹 CPU Usage:", psutil.cpu_percent(), "%")
    print("🔹 RAM Usage:", psutil.virtual_memory().percent, "%")
    print("🔹 Disk Usage:", psutil.disk_usage('/').percent, "%")

if __name__ == "__main__":
    system_health()
