"""Hill Climbing and small-instance exhaustive route-order comparison."""
from itertools import permutations


def route_cost(order, entrance, distance_fn):
    """Sum segment costs for a book-position order; infinity if unreachable."""
    if not order:
        return 0
    total = 0
    current = tuple(entrance)
    for destination in order:
        distance = distance_fn(current, tuple(destination))
        if distance is None or distance == float("inf"):
            return float("inf")
        total += distance
        current = tuple(destination)
    return total


def hill_climbing(positions, entrance=(0, 0), distance_fn=None, max_iterations=500):
    """Improve a collection order with swap-neighborhood hill climbing.

    For compatibility with simple earlier versions, if distance_fn is omitted,
    Manhattan distance is used. Pass A* path lengths for obstacle-aware costs.
    Returns a list of positions in the selected visit order.
    """
    positions = [tuple(p) for p in positions]
    if distance_fn is None:
        distance_fn = lambda a, b: abs(a[0] - b[0]) + abs(a[1] - b[1])
    if len(positions) < 2:
        return positions

    current = positions[:]
    current_cost = route_cost(current, entrance, distance_fn)
    for _ in range(max_iterations):
        best_order, best_cost = current, current_cost
        for i in range(len(current) - 1):
            for j in range(i + 1, len(current)):
                candidate = current[:]
                candidate[i], candidate[j] = candidate[j], candidate[i]
                candidate_cost = route_cost(candidate, entrance, distance_fn)
                if candidate_cost < best_cost:
                    best_order, best_cost = candidate, candidate_cost
        if best_cost >= current_cost:
            break
        current, current_cost = best_order, best_cost
    return current


def exhaustive_best_order(positions, entrance=(0, 0), distance_fn=None, max_books=8):
    """Find the optimal order by checking permutations for small selections.

    Returns (best_order, best_cost). For more than max_books, returns (None, None).
    """
    positions = [tuple(p) for p in positions]
    if len(positions) > max_books:
        return None, None
    if distance_fn is None:
        distance_fn = lambda a, b: abs(a[0] - b[0]) + abs(a[1] - b[1])
    best_order, best_cost = None, float("inf")
    for order in permutations(positions):
        cost = route_cost(order, entrance, distance_fn)
        if cost < best_cost:
            best_order, best_cost = list(order), cost
    if best_order is None:
        return None, float("inf")
    return best_order, best_cost
