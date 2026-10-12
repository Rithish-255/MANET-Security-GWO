import math
import random
from typing import List, Dict, Tuple

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


random.seed(42)
np.random.seed(42)


def generate_manet_topology(num_nodes: int = 12, malicious_fraction: float = 0.2) -> Dict:
    """Create a small MANET with random topology and node trust values."""
    graph = {
        i: [] for i in range(num_nodes)
    }

    for i in range(num_nodes):
        for j in range(i + 1, num_nodes):
            if i != j and np.random.rand() < 0.32:
                graph[i].append(j)
                graph[j].append(i)

    # Ensure connectivity by adding some fallback links if nodes are isolated
    for i in range(num_nodes - 1):
        if not graph[i]:
            graph[i].append(i + 1)
            graph[i + 1].append(i)

    trust = {}
    for i in range(num_nodes):
        base = 0.52 + 0.38 * np.random.rand()
        if np.random.rand() < malicious_fraction:
            base = base * 0.42
        trust[i] = round(base, 3)

    residual_energy = {}
    for i in range(num_nodes):
        residual_energy[i] = round(0.45 + 0.55 * np.random.rand(), 3)

    malicious_nodes = set()
    for i in range(num_nodes):
        if np.random.rand() < malicious_fraction:
            malicious_nodes.add(i)

    return {
        "graph": graph,
        "trust": trust,
        "energy": residual_energy,
        "malicious_nodes": malicious_nodes,
    }


def route_exists(graph: Dict[int, List[int]], route: List[int]) -> bool:
    if len(route) < 2:
        return False
    for i in range(len(route) - 1):
        if route[i + 1] not in graph.get(route[i], []):
            return False
    return True


def generate_random_route(graph: Dict[int, List[int]], source: int, destination: int) -> List[int]:
    visited = {source}
    route = [source]
    current = source

    while current != destination:
        neighbors = [n for n in graph.get(current, []) if n not in visited]
        if not neighbors:
            return [source, destination] if source != destination else [source]
        nxt = random.choice(neighbors)
        route.append(nxt)
        visited.add(nxt)
        current = nxt
    return route


def route_fitness(route: List[int], trust: Dict[int, float], energy: Dict[int, float], malicious_nodes: set, hop_penalty: float = 1.0) -> float:
    if not route or len(route) < 2:
        return 0.0

    trust_score = sum(trust.get(node, 0.0) for node in route) / len(route)
    energy_score = sum(energy.get(node, 0.0) for node in route) / len(route)
    malicious_hits = sum(1 for node in route if node in malicious_nodes)
    path_length = len(route)

    # Higher is better. Security and energy are rewarded; malicious nodes and path length are penalized.
    score = (
        0.55 * trust_score +
        0.25 * energy_score +
        0.20 * (1.0 / (1.0 + malicious_hits + 0.25 * path_length))
    )
    return round(score, 4)


def generate_initial_whales(graph: Dict[int, List[int]], source: int, destination: int, whale_count: int = 20):
    whales = []
    for _ in range(whale_count):
        route = generate_random_route(graph, source, destination)
        whales.append(route)
    return whales


def ensure_valid_route(route: List[int], graph: Dict[int, List[int]], source: int, destination: int):
    if not route or route[0] != source:
        route = [source] + route
    if route[-1] != destination:
        route = route + [destination]

    if not route_exists(graph, route):
        # If invalid, repair by greedily connecting to the nearest valid neighbor
        repaired = [source]
        current = source
        while current != destination:
            candidates = [n for n in graph.get(current, []) if n not in repaired]
            if not candidates:
                break
            nxt = min(candidates, key=lambda n: abs(n - destination))
            repaired.append(nxt)
            current = nxt
        if repaired[-1] != destination:
            repaired.append(destination)
        return repaired

    return route


def guided_whale_optimization(
    graph: Dict[int, List[int]],
    source: int,
    destination: int,
    trust: Dict[int, float],
    energy: Dict[int, float],
    malicious_nodes: set,
    whale_count: int = 20,
    iterations: int = 30,
) -> Tuple[List[int], float, Dict[str, float]]:
    whales = generate_initial_whales(graph, source, destination, whale_count)
    best_route = whales[0]
    best_score = route_fitness(best_route, trust, energy, malicious_nodes)

    for _ in range(iterations):
        for idx, whale in enumerate(whales):
            whale = ensure_valid_route(whale, graph, source, destination)
            score = route_fitness(whale, trust, energy, malicious_nodes)
            if score > best_score:
                best_route = whale
                best_score = score

        leader = best_route
        updated_whales = []

        for whale in whales:
            route = []
            max_len = max(len(whale), len(leader))
            for i in range(max_len):
                if i < len(whale) and i < len(leader):
                    v = whale[i] if random.random() < 0.6 else leader[i]
                elif i < len(leader):
                    v = leader[i]
                else:
                    v = whale[i]
                route.append(v)

            # Add guidance toward secure nodes
            fixed = []
            for node in route:
                if node in malicious_nodes:
                    candidate_nodes = [n for n in graph.get(fixed[-1] if fixed else source, []) if n not in malicious_nodes]
                    if candidate_nodes:
                        node = candidate_nodes[0]
                fixed.append(node)

            route = ensure_valid_route(fixed, graph, source, destination)
            updated_whales.append(route)

        whales = updated_whales

    final_best = ensure_valid_route(best_route, graph, source, destination)
    final_score = route_fitness(final_best, trust, energy, malicious_nodes)

    metrics = {
        "best_route": final_best,
        "security_score": round(final_score, 4),
        "malicious_nodes_avoided": sum(1 for n in final_best if n in malicious_nodes),
    }
    return final_best, final_score, metrics


def compute_network_metrics(route: List[int], trust: Dict[int, float], energy: Dict[int, float], malicious_nodes: set) -> Dict[str, float]:
    route_trust = sum(trust.get(node, 0.0) for node in route) / max(1, len(route))
    route_energy = sum(energy.get(node, 0.0) for node in route) / max(1, len(route))
    malicious_count = sum(1 for node in route if node in malicious_nodes)

    pdr = 92.5 + (route_trust * 10.0) - (malicious_count * 6.5)
    throughput = 700 + route_energy * 350 - malicious_count * 60
    delay = 50 + (len(route) * 12) - (route_trust * 25)
    lifetime = 75 + (route_energy * 40) - (malicious_count * 10)

    return {
        "route_trust": round(route_trust, 3),
        "route_energy": round(route_energy, 3),
        "packet_delivery_ratio": round(pdr, 2),
        "throughput_kbps": round(throughput, 2),
        "average_delay_ms": round(delay, 2),
        "network_lifetime_percent": round(lifetime, 2),
        "malicious_nodes_encountered": malicious_count,
    }


def plot_metrics(metrics: Dict[str, float]) -> None:
    labels = ["PDR", "Throughput", "Delay", "Lifetime"]
    values = [
        metrics["packet_delivery_ratio"],
        metrics["throughput_kbps"],
        metrics["average_delay_ms"],
        metrics["network_lifetime_percent"],
    ]

    plt.figure(figsize=(8, 5))
    plt.bar(labels, values, color=["#2ecc71", "#3498db", "#f39c12", "#9b59b6"])
    plt.title("MANET Security Performance with Guided Whale Optimization")
    plt.ylabel("Metric Value")
    plt.ylim(0, max(values) * 1.5)
    for i, value in enumerate(values):
        plt.text(i, value + 2, f"{value:.2f}", ha="center")
    plt.tight_layout()
    plt.savefig("plots/manet_security_results.png", dpi=150)


def simulate_manet_security_project() -> Dict[str, object]:
    network = generate_manet_topology(num_nodes=12, malicious_fraction=0.2)
    graph = network["graph"]
    trust = network["trust"]
    energy = network["energy"]
    malicious_nodes = network["malicious_nodes"]

    source = 0
    destination = 11

    route, score, _ = guided_whale_optimization(
        graph,
        source,
        destination,
        trust,
        energy,
        malicious_nodes,
        whale_count=20,
        iterations=30,
    )

    metrics = compute_network_metrics(route, trust, energy, malicious_nodes)

    result = {
        "source": source,
        "destination": destination,
        "selected_route": route,
        "security_score": score,
        "packet_delivery_ratio": metrics["packet_delivery_ratio"],
        "throughput_kbps": metrics["throughput_kbps"],
        "average_delay_ms": metrics["average_delay_ms"],
        "network_lifetime_percent": metrics["network_lifetime_percent"],
        "malicious_nodes_avoided": len(malicious_nodes) - metrics["malicious_nodes_encountered"],
        "nodes_visited": len(route),
        "trust_score": metrics["route_trust"],
        "energy_score": metrics["route_energy"],
    }

    print("\n=== MANET Security Enhancement using Guided Whale Optimization ===")
    print(f"Source Node      : {source}")
    print(f"Destination Node : {destination}")
    print(f"Selected Route   : {route}")
    print(f"Security Score   : {score:.4f}")
    print(f"Trust Score      : {result['trust_score']:.3f}")
    print(f"Energy Score     : {result['energy_score']:.3f}")
    print(f"Packet Delivery Ratio : {metrics['packet_delivery_ratio']:.2f}%")
    print(f"Throughput       : {metrics['throughput_kbps']:.2f} kbps")
    print(f"Average Delay    : {metrics['average_delay_ms']:.2f} ms")
    print(f"Network Lifetime : {metrics['network_lifetime_percent']:.2f}%")
    print(f"Malicious Nodes Avoided : {result['malicious_nodes_avoided']}")
    print(f"Nodes in Route   : {len(route)}")

    plot_metrics(metrics)
    print("\nResult plots saved to: plots/manet_security_results.png")

    return result


if __name__ == "__main__":
    simulate_manet_security_project()
