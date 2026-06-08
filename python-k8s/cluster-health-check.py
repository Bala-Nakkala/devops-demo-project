from kubernetes import client, config
from datetime import datetime
import sys

def load_cluster():
    try:
        config.load_kube_config()
        print("✅ Connected using kubeconfig")
    except:
        try:
            config.load_incluster_config()
            print("✅ Connected using in-cluster config")
        except Exception as e:
            print("❌ Cluster connection failed:", e)
            sys.exit(1)


def check_nodes():
    v1 = client.CoreV1Api()
    nodes = v1.list_node()

    print("\n🔹 NODE HEALTH")

    not_ready_nodes = 0

    for node in nodes.items:
        status = "Unknown"

        for condition in node.status.conditions:
            if condition.type == "Ready":
                status = condition.status

        if status != "True":
            not_ready_nodes += 1
            print(f"❌ {node.metadata.name} | NotReady")
        else:
            print(f"✅ {node.metadata.name} | Ready")

    return not_ready_nodes


def check_pods():
    v1 = client.CoreV1Api()
    pods = v1.list_pod_for_all_namespaces()

    print("\n🔹 POD HEALTH")

    running = 0
    pending = 0
    failed = 0
    crashloop = 0

    for pod in pods.items:
        phase = pod.status.phase

        if phase == "Running":
            running += 1
        elif phase == "Pending":
            pending += 1
        else:
            failed += 1

        # Detect CrashLoopBackOff / high restarts
        if pod.status.container_statuses:
            for c in pod.status.container_statuses:
                if c.restart_count >= 3:
                    crashloop += 1
                    print(f"⚠️ Crash/Restart issue: {pod.metadata.namespace}/{pod.metadata.name}")

    print(f"Running Pods : {running}")
    print(f"Pending Pods : {pending}")
    print(f"Failed Pods  : {failed}")
    print(f"Problem Pods : {crashloop}")

    return pending + failed + crashloop


def main():
    print("===================================")
    print("  KUBERNETES CLUSTER HEALTH CHECK  ")
    print("===================================")
    print("Time:", datetime.now())
    print("===================================\n")

    load_cluster()

    node_issues = check_nodes()
    pod_issues = check_pods()

    print("\n===================================")

    if node_issues == 0 and pod_issues == 0:
        print("🟢 CLUSTER STATUS: HEALTHY")
        sys.exit(0)
    else:
        print("🔴 CLUSTER STATUS: UNHEALTHY")
        print(f"Issues -> Nodes: {node_issues}, Pods: {pod_issues}")
        sys.exit(2)


if __name__ == "__main__":
    main()
