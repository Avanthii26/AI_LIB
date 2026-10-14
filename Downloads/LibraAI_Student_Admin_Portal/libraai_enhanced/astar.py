"""A* pathfinding for a four-directional library grid."""
from heapq import heappush, heappop


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(start, goal, grid_size=10, obstacles=None):
    """Return a list of (row, col) cells from start to goal, or None.

    Movement is four-directional and each move costs one. The start and goal
    must be inside the grid and must not be blocked.
    """
    obstacles = set(obstacles or ())
    start, goal = tuple(start), tuple(goal)
    def valid(p):
        return 0 <= p[0] < grid_size and 0 <= p[1] < grid_size and p not in obstacles

    if not valid(start) or not valid(goal):
        return None
    if start == goal:
        return [start]

    frontier = []
    heappush(frontier, (manhattan(start, goal), 0, start))
    came_from = {start: None}
    g_score = {start: 0}
    closed = set()

    while frontier:
        _, cost, current = heappop(frontier)
        if current in closed:
            continue
        if current == goal:
            path = []
            node = current
            while node is not None:
                path.append(node)
                node = came_from[node]
            return list(reversed(path))
        closed.add(current)
        r, c = current
        for nxt in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
            if not valid(nxt) or nxt in closed:
                continue
            tentative = g_score[current] + 1
            if tentative < g_score.get(nxt, float("inf")):
                came_from[nxt] = current
                g_score[nxt] = tentative
                heappush(frontier, (tentative + manhattan(nxt, goal), tentative, nxt))
    return None


def path_length(path):
    """Number of movement steps in a path, or None if no path exists."""
    return None if not path else max(0, len(path) - 1)
