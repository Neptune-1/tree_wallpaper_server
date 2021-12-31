from io import BytesIO
from math import sin, cos, pi
from random import randint, random

from PIL import Image, ImageDraw
from pyramid.view import view_config


@view_config(route_name='get_wallpaper', renderer='json')
def get_wallpaper(request):
    print(request)
    screen_size_x = request.params.get('screen_size_x')
    screen_size_y = request.params.get('screen_size_y')
    inverse = request.params.get('inverse')
    if screen_size_x is None:
        screen_size_x = 1920 * 2
        screen_size_y = 1080 * 2
    else:
        screen_size_x = int(screen_size_x)
        screen_size_y = int(screen_size_y)
    print(inverse, screen_size_x, screen_size_y)
    if inverse is None:
        inverse = False
    image_file = GetFractalTreeWallpaper((screen_size_x, screen_size_y), inverse).get_wallpaper()

    request.response.body = image_file
    request.response.content_type = 'image/png'
    return request.response


class GetFractalTreeWallpaper:

    def __init__(self, screen_size, inverse):  # screen_size - tuple (x, y) , inverse - bool
        self.screen_size = screen_size  # (x, y)

        self.inverse = inverse
        self.screen_size = screen_size[0] * 4, screen_size[1] * 4
        self.im = Image.new('RGB', screen_size, (lambda: (20, 20, 20) if self.inverse else (245, 245, 245))())
        self.draw = ImageDraw.Draw(self.im)  # draw object to draw on image
        self.null_alpha = pi / 2 + (random() - 0.5) / 5  # angle of main branch
        self.base_alpha = pi / randint(5, 10)
        self.null_l = screen_size[1] / randint(6, 8)  # length of main branch
        self.null_point = (screen_size[0] / 2, screen_size[1] / 5 * 4)  # begin point of main branch
        self.full_n = 0  # initial number of branches

        self.wind_influence = random() / 3 + 0.84  # >1 main rotation in left side, <1 ... in right side

        self.start_width = 80 + 20*(random()-0.5)  # width of main branch
        print(self.start_width)

    def draw_branch(self, begin, end, alpha, width1, width2, n,
                    alpha_pre):  # begin - tuple (x, y), end - tuple (x, y), alpha - angle, width - int

        angle = pi / 2 - (self.null_alpha * self.wind_influence ** n + alpha)
        angle_pre = pi / 2 - (self.null_alpha * self.wind_influence ** (n - 1) + alpha_pre)
        if n == 1:
            angle_pre = 0
        p1 = (begin[0] - cos(angle_pre) * (width1 / 2), begin[1] - sin(angle_pre) * (width1 / 2))
        p2 = (begin[0] + cos(angle_pre) * (width1 / 2), begin[1] + sin(angle_pre) * (width1 / 2))
        p3 = (end[0] + cos(angle) * (width2 / 2), end[1] + sin(angle) * (width2 / 2))
        p4 = (end[0] - cos(angle) * (width2 / 2), end[1] - sin(angle) * (width2 / 2))
        self.draw.polygon([p1, p4, p3, p2],
                          fill=self.get_color(n))

    def get_width(self, n):  # n - number of iteration
        return round(self.start_width * 0.8 ** (n * 1.9))

    def get_color(self, n):  # n - number of iteration
        if self.inverse:
            return 220, 220, 220, 255 - n * 2
        else:
            return 0, 0, 0, 100 + n * 10

    # point - tuple (x, y), alpha - angle, n - number of iteration, alpha_pre - angle of previous branch
    def branch(self, point, alpha, n, alpha_pre):
        alpha = alpha % (pi * 2)
        self.full_n += 1
        x, y = point
        length_coef = random() / 10 + 0.7 + 0.1 ** n

        x1 = x + cos(self.null_alpha * self.wind_influence ** n + alpha) * self.null_l * length_coef ** n
        y1 = y - sin(self.null_alpha * self.wind_influence ** n + alpha) * self.null_l * length_coef ** n

        n += 1

        self.draw_branch((x, y), (x1, y1), alpha, self.get_width(n), self.get_width(n + 1), n, alpha_pre)

        if n < 15:
            for i in range(randint(1, 2)):
                r = random()
                if r < 0.5:  # probability of 2 branches
                    self.branch((x1, y1), alpha - i * self.base_alpha * (random() / 5 + 1), n, alpha)
                    self.branch((x1, y1), alpha + i * self.base_alpha * (random() / 5 + 1), n, alpha)
                elif r < 0.51:  # probability of right branch
                    self.branch((x1, y1), alpha + i * self.base_alpha * (random() / 5 + 1), n, alpha)
                elif r < 0.9 + (lambda: 0.11 if n < 7 else 0)():  # probability of left branch
                    self.branch((x1, y1), alpha - i * self.base_alpha * (random() / 5 + 1), n, alpha)

    def get_wallpaper(self):
        while self.full_n < 40000:
            print("start")
            self.branch(self.null_point, 0, 0, 0)
            print(self.full_n)  # print number of branches

        self.im = self.im.resize((self.screen_size[0] // 2, self.screen_size[1] // 2),
                                 resample=Image.ANTIALIAS)  # smooth image
        temp = BytesIO()
        self.im.save(temp, format="png")

        return temp.getvalue()
