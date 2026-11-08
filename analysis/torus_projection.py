"""Projected shape of a luminous torus (Hopfion (Ring) Lightning Hypothesis v0.8, Appendix A).

Standard library only. Run: python3 analysis/torus_projection.py   (takes a few seconds)

Model: optically thin torus with uniform emissivity, major radius R, minor radius a, symmetry axis tilted
by inclination i from the line of sight (i = 0 face-on, 90 deg edge-on). Part 1 is the analytic silhouette;
part 2 integrates emission along the line of sight on a voxel grid, adds a Gaussian "glow" of width
sigma = f (R + a), and measures the 50 %-of-peak contour.
"""
import math


def silhouette_table():
    print("Part 1: silhouette axis ratio q(i) = (R cos i + a) / (R + a); random orientations: P(cos i >= c) = 1 - c")
    for r_over_a in (0.5, 0.75, 1.0, 1.5, 2.0, 3.0):
        a, r = 1.0, r_over_a
        c = max(0.0, (0.85 * (r + a) - a) / r)
        hole = "yes" if r > a else "no"
        print(f"R/a = {r_over_a:4}: edge-on q = {a / (r + a):.2f}; fraction of view directions with q >= 0.85 = {1 - c:.2f}; face-on central hole: {hole}")


def emission_image(r_over_a, inc_deg, n=71):
    a, r = 1.0, r_over_a
    half = (r + a) * 1.6
    xs = [-half + 2 * half * k / (n - 1) for k in range(n)]
    ci, si = math.cos(math.radians(inc_deg)), math.sin(math.radians(inc_deg))
    img = [[0.0] * n for _ in range(n)]
    for ix, x in enumerate(xs):
        for iy, y in enumerate(xs):
            count = 0
            for s in xs:
                zb = y * si + s * ci
                yb = y * ci - s * si
                if (math.hypot(x, yb) - r) ** 2 + zb**2 <= a * a:
                    count += 1
            img[ix][iy] = count
    return xs, img


def gaussian_blur(img, sigma_px):
    if sigma_px <= 0:
        return img
    n = len(img)
    rad = int(3 * sigma_px) + 1
    kern = [math.exp(-0.5 * (j / sigma_px) ** 2) for j in range(-rad, rad + 1)]
    total = sum(kern)
    kern = [k / total for k in kern]

    def clamp(i):
        return min(max(i, 0), n - 1)

    tmp = [[sum(img[clamp(i + j)][y] * kern[j + rad] for j in range(-rad, rad + 1)) for y in range(n)] for i in range(n)]
    return [[sum(tmp[x][clamp(i + j)] * kern[j + rad] for j in range(-rad, rad + 1)) for i in range(n)] for x in range(n)]


def contour_stats(img, level=0.5):
    n = len(img)
    peak = max(max(row) for row in img)
    on = [(i, j) for i in range(n) for j in range(n) if img[i][j] >= level * peak]
    wi = max(i for i, _ in on) - min(i for i, _ in on)
    wj = max(j for _, j in on) - min(j for _, j in on)
    c = n // 2
    return min(wi, wj) / max(wi, wj), img[c][c] / peak


def emission_table():
    print("\nPart 2: line-of-sight emission, 50 % contour, glow sigma = f (R + a)")
    for r_over_a in (0.5, 1.0, 2.0):
        for f in (0.0, 0.2, 0.4):
            cells = []
            for inc in (0, 45, 90):
                xs, img = emission_image(r_over_a, inc)
                blurred = gaussian_blur(img, f * (r_over_a + 1.0) / (xs[1] - xs[0]))
                q, centre = contour_stats(blurred)
                cells.append(f"i = {inc:2d}: q = {q:.2f}, centre/peak = {centre:.2f}")
            print(f"R/a = {r_over_a}, f = {f}: " + " | ".join(cells))


if __name__ == "__main__":
    silhouette_table()
    emission_table()
