import numpy as np

COLORS = [
    (43, 131, 186), # Blue
    (171, 221, 164), # Green
    (255, 255, 191), # Yellow
    (253, 174, 97), # Orange
    (215, 25, 28), # Red
]

def color_palette(a: np.ndarray, n=5):
    i_min = np.min(a)
    i_max = np.max(a)
    i_diff = float(i_max - i_min)
    i_step = i_diff / (n - 1)
    steps = []
    for i in range(n):
        steps.append(i_min + i * i_step)
    def get_between(v):
        for i in range(len(steps) - 1):
            if v > steps[i]:
                continue
            return i
        return len(steps) - 1
    def interpolate(v):
        i = get_between(v)
        c1 = COLORS[i]
        c2 = COLORS[i - 1]
        x = max(0.0, min(1.0, (v - steps[i - 1]) / i_step))
        return (
            int(max(0, min(255, c1[0] * x + c2[0] * (1 - x)))), # Red
            int(max(0, min(255, c1[1] * x + c2[1] * (1 - x)))), # Green
            int(max(0, min(255, c1[2] * x + c2[2] * (1 - x)))), # Blue
        )
    return interpolate

def colorize(src: np.ndarray, alpha=.6):
    colors = color_palette(src)
    r = np.empty(src.shape, 'uint8')
    g = np.empty(src.shape, 'uint8')
    b = np.empty(src.shape, 'uint8')
    a = np.empty(src.shape, 'uint8')
    for x in range(src.shape[0]):
        for y in range(src.shape[1]):
            c = colors(src[x, y])
            r[x, y] = c[0]
            g[x, y] = c[1]
            b[x, y] = c[2]
            a[x, y] = int(255 * alpha)
    return r, g, b, a
