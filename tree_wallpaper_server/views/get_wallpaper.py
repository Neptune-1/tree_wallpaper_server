from io import BytesIO
from math import sin, cos, pi
from random import randint, random

from PIL import Image, ImageDraw
from pyramid.view import view_config


@view_config(route_name='get_wallpaper', renderer='json')
def get_wallpaper(request):
    screen_size_x = request.params.get('screen_size_x')
    screen_size_y = request.params.get('screen_size_y')
    inverse = request.params.get('inverse')
    if screen_size_x is None:
        screen_size_x = 1920
        screen_size_y = 1080
    if inverse is None:
        inverse = False
    image_file = GetFractalTreeWallpaper((screen_size_x, screen_size_y), inverse).get_wallpaper()

    request.response.body = image_file
    request.response.content_type = 'image/png'
    return request.response


class GetFractalTreeWallpaper:

    def __init__(self, screen_size, inverse):
        self.inverse = inverse
        self.screen_size = screen_size[0] * 4, screen_size[1] * 4

        self.im = Image.new('RGB', self.screen_size, (lambda: (20, 20, 20) if self.inverse else (245, 245, 245))())
        self.draw = ImageDraw.Draw(self.im)
        self.null_alpha = pi / 2 + (random() - 0.5) / 5
        self.base_alpha = pi / randint(5, 10)
        self.null_l = self.screen_size[1] / randint(6, 8)
        self.null_point = (self.screen_size[0] / 2, self.screen_size[1] / 5 * 4)
        self.full_n = 0

        self.wind_influence = random() / 5 + 0.9  # >1 main rotation in left side, <1 ... in right side
        for i in range(5):
            self.draw.line((0, self.screen_size[1] / 5 * 3.5 + (random() - 0.5) * 7, self.screen_size[0],
                            self.screen_size[1] / 5 * 3.5 - (random() - 0.5) * 7), width=1,
                           fill=(lambda: (220, 220, 220) if self.inverse else (50, 50, 50))())

    def branch(self, point, alpha, n):
        self.full_n += 1
        x, y = point
        length_coef = random() / 10 + 0.7 + 0.1 ** n

        x1 = x + cos(self.null_alpha * self.wind_influence ** n + alpha) * self.null_l * length_coef ** n
        y1 = y - sin(self.null_alpha * self.wind_influence ** n + alpha) * self.null_l * length_coef ** n

        n += 1

        self.draw.line((x, y, x1, y1), width=round(self.screen_size[0] * 0.01 * 0.8 ** (n * 1.5)),
                       fill=(lambda: (220, 220, 220) if self.inverse else (n * 3, n * 3, n * 3))())

        if n < 15:
            for i in range(randint(1, 2)):
                r = random()
                if r < 0.5:
                    self.branch((x1, y1), alpha - i * self.base_alpha * (random() / 5 + 1), n)
                    self.branch((x1, y1), alpha + i * self.base_alpha * (random() / 5 + 1), n)
                elif r < 0.51:
                    self.branch((x1, y1), alpha + i * self.base_alpha * (random() / 5 + 1), n)
                elif r < 0.9:
                    self.branch((x1, y1), alpha - i * self.base_alpha * (random() / 5 + 1), n)

    def get_wallpaper(self):
        while self.full_n < 50000:
            print("start")
            self.branch(self.null_point, 0, 0)
            print(self.full_n)

        self.im = self.im.resize((self.screen_size[0] // 2, self.screen_size[1] // 2), resample=Image.ANTIALIAS)

        temp = BytesIO()
        self.im.save(temp, format="png")

        return temp.getvalue()
