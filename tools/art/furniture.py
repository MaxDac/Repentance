"""Furniture drawn in the room's one-point perspective, so beds and cabinets stand on the floor at the same
scale as the characters (a man is about 75-85 px tall, i.e. roughly 42-47 px per metre at the back wall).

World units are back-wall pixels: x runs along the wall, y is height above the floor and z is the distance from
the back wall towards the camera."""
from PIL import ImageDraw
from .common import mul


class Room3D:
    def __init__(self, floor, vx, vy, d0=900.0):
        self.floor, self.vx, self.vy, self.d0 = floor, vx, vy, d0

    def s(self, z):
        return self.d0 / (self.d0 - z)

    def P(self, x, y, z):
        s = self.s(z)
        return (self.vx + (x - self.vx) * s, self.vy + (self.floor - self.vy) * s - y * s)

    def quad(self, img, pts, fill, outline=None):
        d = ImageDraw.Draw(img)
        d.polygon([self.P(*p) for p in pts], fill=fill, outline=outline)

    def line(self, img, a, b, fill, width=1):
        ImageDraw.Draw(img).line([self.P(*a), self.P(*b)], fill=fill, width=width)

    def box(self, img, x0, x1, y0, y1, z0, z1, col, top=None, side=None, outline=None, front=True):
        """Solid box: draws the visible side, the top and the front face."""
        top = top or mul(col, 1.14)
        side = side or mul(col, 0.72)
        if x0 > self.vx:
            self.quad(img, [(x0, y0, z0), (x0, y0, z1), (x0, y1, z1), (x0, y1, z0)], side, outline)
        if x1 < self.vx:
            self.quad(img, [(x1, y0, z0), (x1, y0, z1), (x1, y1, z1), (x1, y1, z0)], side, outline)
        self.quad(img, [(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)], top, outline)
        if front:
            self.quad(img, [(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], col, outline)

    def front_y(self, z):
        """Screen row (painting coordinates) of the floor at depth z."""
        return self.P(self.vx, 0, z)[1]
