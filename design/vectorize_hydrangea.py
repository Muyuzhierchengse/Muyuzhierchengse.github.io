"""Extract four continuous centerline walks from the approved colour path map.

The image model supplies the botanical shape; this utility only performs a
deterministic colour separation, thinning, and path export.  Keeping that split
lets the final website use real SVG strokes without redrawing the approved art.
"""

from __future__ import annotations

from collections import defaultdict, deque
from pathlib import Path
import math
import sys

import numpy as np
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "hydrangea-four-path-map.png"
OUTPUT = ROOT.parent / "static" / "images" / "hydrangea-continuous.svg"
PREVIEW = ROOT / "hydrangea-vector-preview-smooth.png"


def separate_colours(rgb: np.ndarray) -> dict[str, np.ndarray]:
    """Return tolerant masks for the four deliberately saturated guide inks."""
    values = rgb.astype(float)
    red, green, blue = values[:, :, 0], values[:, :, 1], values[:, :, 2]
    return {
        "path-a": (red > 150) & (red > green * 1.35) & (red > blue * 1.20),
        "path-b": (blue > 100) & (blue > red * 1.25) & (blue > green * 1.10),
        "path-c": (green > 90) & (green > red * 1.15) & (green > blue * 1.15),
        "path-d": (red > 140) & (blue > 100) & (green < np.minimum(red, blue) * 0.75),
    }


def largest_component(mask: np.ndarray) -> np.ndarray:
    """Discard isolated antialiasing specks while preserving the main stroke."""
    height, width = mask.shape
    seen = np.zeros_like(mask, dtype=bool)
    best: list[tuple[int, int]] = []
    for row, col in zip(*np.nonzero(mask)):
        if seen[row, col]:
            continue
        queue = deque([(row, col)])
        seen[row, col] = True
        component: list[tuple[int, int]] = []
        while queue:
            current_row, current_col = queue.popleft()
            component.append((current_row, current_col))
            for row_delta in (-1, 0, 1):
                for col_delta in (-1, 0, 1):
                    if row_delta == col_delta == 0:
                        continue
                    next_row = current_row + row_delta
                    next_col = current_col + col_delta
                    if (
                        0 <= next_row < height
                        and 0 <= next_col < width
                        and mask[next_row, next_col]
                        and not seen[next_row, next_col]
                    ):
                        seen[next_row, next_col] = True
                        queue.append((next_row, next_col))
        if len(component) > len(best):
            best = component
    result = np.zeros_like(mask, dtype=bool)
    if best:
        rows, cols = zip(*best)
        result[np.array(rows), np.array(cols)] = True
    return result


def thin(mask: np.ndarray) -> np.ndarray:
    """Vectorised Zhang–Suen thinning, producing a one-pixel centreline."""
    image = mask.astype(np.uint8)
    changed = True
    while changed:
        changed = False
        for first_pass in (True, False):
            padded = np.pad(image, 1)
            p2 = padded[:-2, 1:-1]
            p3 = padded[:-2, 2:]
            p4 = padded[1:-1, 2:]
            p5 = padded[2:, 2:]
            p6 = padded[2:, 1:-1]
            p7 = padded[2:, :-2]
            p8 = padded[1:-1, :-2]
            p9 = padded[:-2, :-2]
            neighbours = p2 + p3 + p4 + p5 + p6 + p7 + p8 + p9
            transitions = np.stack(
                [
                    (p2 == 0) & (p3 == 1),
                    (p3 == 0) & (p4 == 1),
                    (p4 == 0) & (p5 == 1),
                    (p5 == 0) & (p6 == 1),
                    (p6 == 0) & (p7 == 1),
                    (p7 == 0) & (p8 == 1),
                    (p8 == 0) & (p9 == 1),
                    (p9 == 0) & (p2 == 1),
                ],
                axis=0,
            ).sum(axis=0)
            if first_pass:
                condition_a = p2 * p4 * p6 == 0
                condition_b = p4 * p6 * p8 == 0
            else:
                condition_a = p2 * p4 * p8 == 0
                condition_b = p2 * p6 * p8 == 0
            remove = (
                (image == 1)
                & (neighbours >= 2)
                & (neighbours <= 6)
                & (transitions == 1)
                & condition_a
                & condition_b
            )
            if np.any(remove):
                image[remove] = 0
                changed = True
    return image.astype(bool)


def skeleton_graph(skeleton: np.ndarray) -> dict[tuple[int, int], list[tuple[int, int]]]:
    """Build an eight-neighbour graph from the thinned colour centreline."""
    points = set(zip(*np.nonzero(skeleton)))
    graph: dict[tuple[int, int], list[tuple[int, int]]] = defaultdict(list)
    for row, col in points:
        for row_delta in (-1, 0, 1):
            for col_delta in (-1, 0, 1):
                if row_delta == col_delta == 0:
                    continue
                neighbour = (row + row_delta, col + col_delta)
                if neighbour not in points:
                    continue
                graph[(row, col)].append(neighbour)
    return graph


def continuous_walk(graph: dict[tuple[int, int], list[tuple[int, int]]]) -> list[tuple[int, int]]:
    """Return one continuous edge-covering walk, retracing only where necessary."""
    if not graph:
        return []
    endpoints = [point for point, neighbours in graph.items() if len(neighbours) == 1]
    start = min(endpoints or graph.keys(), key=lambda point: (point[1], point[0]))
    used_edges: set[tuple[tuple[int, int], tuple[int, int]]] = set()
    walk: list[tuple[int, int]] = []

    sys.setrecursionlimit(max(100_000, len(graph) * 4))

    def visit(point: tuple[int, int]) -> None:
        walk.append(point)
        for neighbour in graph[point]:
            edge = tuple(sorted((point, neighbour)))
            if edge in used_edges:
                continue
            used_edges.add(edge)
            visit(neighbour)
            walk.append(point)

    visit(start)
    return walk


def reduce_walk(points: list[tuple[int, int]], spacing: float = 5.0) -> list[tuple[int, int]]:
    """Thin dense pixel coordinates while retaining turns and path continuity."""
    if len(points) < 3:
        return points
    reduced = [points[0]]
    accumulated = 0.0
    previous = points[0]
    for point in points[1:-1]:
        accumulated += ((point[0] - previous[0]) ** 2 + (point[1] - previous[1]) ** 2) ** 0.5
        if accumulated >= spacing:
            reduced.append(point)
            accumulated = 0.0
        previous = point
    reduced.append(points[-1])
    return reduced


def point_line_distance(
    point: tuple[float, float],
    start: tuple[float, float],
    end: tuple[float, float],
) -> float:
    """Return the perpendicular distance used by Ramer–Douglas–Peucker."""
    dx, dy = end[0] - start[0], end[1] - start[1]
    if dx == dy == 0:
        return math.hypot(point[0] - start[0], point[1] - start[1])
    position = ((point[0] - start[0]) * dx + (point[1] - start[1]) * dy) / (dx * dx + dy * dy)
    projection = (start[0] + position * dx, start[1] + position * dy)
    return math.hypot(point[0] - projection[0], point[1] - projection[1])


def simplify(points: list[tuple[float, float]], tolerance: float = 2.4) -> list[tuple[float, float]]:
    """Remove pixel-scale wobble while retaining petals, tips, and junctions."""
    if len(points) <= 2:
        return points
    maximum_distance = 0.0
    split_index = 0
    for index, point in enumerate(points[1:-1], start=1):
        distance = point_line_distance(point, points[0], points[-1])
        if distance > maximum_distance:
            maximum_distance = distance
            split_index = index
    if maximum_distance <= tolerance:
        return [points[0], points[-1]]
    left = simplify(points[: split_index + 1], tolerance)
    right = simplify(points[split_index:], tolerance)
    return left[:-1] + right


def is_corner(
    previous: tuple[float, float],
    point: tuple[float, float],
    following: tuple[float, float],
) -> bool:
    """Preserve deliberate petal tips and reversals instead of rounding them."""
    incoming = (point[0] - previous[0], point[1] - previous[1])
    outgoing = (following[0] - point[0], following[1] - point[1])
    incoming_length = math.hypot(*incoming)
    outgoing_length = math.hypot(*outgoing)
    if incoming_length < 1e-6 or outgoing_length < 1e-6:
        return True
    cosine = max(
        -1.0,
        min(1.0, (incoming[0] * outgoing[0] + incoming[1] * outgoing[1]) / (incoming_length * outgoing_length)),
    )
    return math.degrees(math.acos(cosine)) > 52.0


def clamp_handle(
    origin: tuple[float, float],
    handle: tuple[float, float],
    maximum: float,
) -> tuple[float, float]:
    dx, dy = handle[0] - origin[0], handle[1] - origin[1]
    length = math.hypot(dx, dy)
    if length <= maximum or length < 1e-6:
        return handle
    scale = maximum / length
    return origin[0] + dx * scale, origin[1] + dy * scale


def bezier_controls(
    points: list[tuple[float, float]],
    index: int,
) -> tuple[tuple[float, float], tuple[float, float]]:
    """Convert a simplified polyline segment into restrained cubic handles."""
    start = points[index]
    end = points[index + 1]
    previous = points[index - 1] if index else start
    following = points[index + 2] if index + 2 < len(points) else end
    segment_length = math.hypot(end[0] - start[0], end[1] - start[1])

    if index and is_corner(previous, start, end):
        first = (start[0] + (end[0] - start[0]) * 0.10, start[1] + (end[1] - start[1]) * 0.10)
    else:
        first = (start[0] + (end[0] - previous[0]) * 0.12, start[1] + (end[1] - previous[1]) * 0.12)

    if index + 2 < len(points) and is_corner(start, end, following):
        second = (end[0] - (end[0] - start[0]) * 0.10, end[1] - (end[1] - start[1]) * 0.10)
    else:
        second = (end[0] - (following[0] - start[0]) * 0.12, end[1] - (following[1] - start[1]) * 0.12)

    limit = max(0.25, segment_length * 0.34)
    return clamp_handle(start, first, limit), clamp_handle(end, second, limit)


def smooth_path(points: list[tuple[int, int]], scale: float) -> tuple[str, list[tuple[float, float]]]:
    if not points:
        return "", []
    coordinates = [(col * scale, row * scale) for row, col in points]
    deduplicated = [coordinates[0]]
    for point in coordinates[1:]:
        if math.hypot(point[0] - deduplicated[-1][0], point[1] - deduplicated[-1][1]) > 0.15:
            deduplicated.append(point)
    fitted = simplify(deduplicated)
    commands = [f"M{fitted[0][0]:.1f},{fitted[0][1]:.1f}"]
    for index, end in enumerate(fitted[1:]):
        first, second = bezier_controls(fitted, index)
        commands.append(
            f"C{first[0]:.1f},{first[1]:.1f} {second[0]:.1f},{second[1]:.1f} {end[0]:.1f},{end[1]:.1f}"
        )
    return " ".join(commands), fitted


def write_preview(paths: list[tuple[str, list[tuple[float, float]]]]) -> None:
    """Save a lightweight geometry proof for visual inspection before deploy."""
    canvas_size = 1400
    preview = Image.new("RGB", (canvas_size, canvas_size), "#fcfbf9")
    drawing = ImageDraw.Draw(preview)
    scale = canvas_size / 1000.0

    def cubic_point(
        start: tuple[float, float],
        first: tuple[float, float],
        second: tuple[float, float],
        end: tuple[float, float],
        position: float,
    ) -> tuple[float, float]:
        inverse = 1.0 - position
        return (
            inverse**3 * start[0]
            + 3 * inverse**2 * position * first[0]
            + 3 * inverse * position**2 * second[0]
            + position**3 * end[0],
            inverse**3 * start[1]
            + 3 * inverse**2 * position * first[1]
            + 3 * inverse * position**2 * second[1]
            + position**3 * end[1],
        )

    for _, fitted in paths:
        sampled = [fitted[0]]
        for index, end in enumerate(fitted[1:]):
            first, second = bezier_controls(fitted, index)
            start = fitted[index]
            sampled.extend(cubic_point(start, first, second, end, step / 14.0) for step in range(1, 15))
        scaled = [(round(x * scale), round(y * scale)) for x, y in sampled]
        drawing.line(scaled, fill="#625d58", width=3, joint="curve")
    preview.save(PREVIEW)


def main() -> None:
    source = np.array(Image.open(SOURCE).convert("RGB"))
    scale = 1000.0 / max(source.shape[:2])
    paths: list[tuple[str, str]] = []
    preview_paths: list[tuple[str, list[tuple[float, float]]]] = []
    for name, colour_mask in separate_colours(source).items():
        component = largest_component(colour_mask)
        skeleton = thin(component)
        graph = skeleton_graph(skeleton)
        walk = reduce_walk(continuous_walk(graph))
        data, fitted = smooth_path(walk, scale)
        paths.append((name, data))
        preview_paths.append((name, fitted))
        approximate_length = sum(
            math.hypot(end[0] - start[0], end[1] - start[1])
            for start, end in zip(fitted, fitted[1:])
        )
        print(
            f"{name}: mask={component.sum()} skeleton={skeleton.sum()} "
            f"sampled={len(walk)} fitted={len(fitted)} approx_length={approximate_length:.0f}"
        )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    path_markup = "\n".join(
        f'    <path id="hydrangea-{name}" class="hydrangea-line" pathLength="1" d="{data}" />'
        for name, data in paths
    )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000" role="img" aria-label="Minimal continuous-line hydrangea">
  <!-- Four smoothed cubic centreline paths derived from the approved botanical concept. -->
  <g fill="none" stroke="currentColor" stroke-width="1.65" stroke-linecap="round" stroke-linejoin="round" shape-rendering="geometricPrecision">
{path_markup}
  </g>
</svg>
'''
    OUTPUT.write_text(svg, encoding="utf-8")
    write_preview(preview_paths)
    print(f"wrote {OUTPUT}")
    print(f"wrote {PREVIEW}")


if __name__ == "__main__":
    main()
