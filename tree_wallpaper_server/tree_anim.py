from math import sin, cos, pi
from random import randint, random

import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
from tqdm import tqdm


class Tree:
    def __init__(self, screen_size=(1920, 1080),
                 inverse=False):  # screen_size - tuple (x, y) , inverse - bool
        self.inverse = inverse
        self.screen_size = screen_size[0], screen_size[1]  # (x, y)
        self.im = Image.new('RGB', self.screen_size, (lambda: (20, 20, 20) if self.inverse else (245, 245, 245))())
        self.draw = ImageDraw.Draw(self.im)  # draw object to draw on image
        self.null_alpha = pi / 2 + (random() - 0.5) / 5  # angle of main branch
        self.base_alpha = pi / randint(5, 10)
        self.max_null_l = self.screen_size[1] / randint(4, 7)
        self.year_of_branches = 30

        self.lifetime = self.year_of_branches * 13
        self.null_l = [0 for _ in range(self.lifetime // self.year_of_branches + 1)]

        self.null_point = (self.screen_size[0] / 2, self.screen_size[1] / 5 * 4)  # begin point of main branch
        self.full_n = 0  # initial number of branches
        self.wind_influence = random() / 2 + 0.75  # >1 main rotation in left side, <1 ... in right side
        self.start_width = (8 + 3 * (random() - 0.5))  # width of main branch

        self.all_branches = []

        self.year = 1

    def draw_branch(self, branch):  # begin - tuple (x, y), end - tuple (x, y), alpha - angle, width - int

        angle = pi / 2 - (self.null_alpha * self.wind_influence ** branch.n + branch.alpha)
        angle_pre = pi / 2 - (self.null_alpha * self.wind_influence ** (branch.n - 1) + branch.alpha_pre)
        if branch.n == 0:
            angle_pre = 0

        start_width = self.start_width * branch.start_width
        end_width = self.start_width * branch.end_width
        p1 = (branch.start_point[0] - cos(angle_pre) * (start_width / 2),
              branch.start_point[1] - sin(angle_pre) * (start_width / 2))
        p2 = (branch.start_point[0] + cos(angle_pre) * (start_width / 2),
              branch.start_point[1] + sin(angle_pre) * (start_width / 2))
        p3 = (branch.end_point[0] + cos(angle) * (end_width / 2), branch.end_point[1] + sin(angle) * (end_width / 2))
        p4 = (branch.end_point[0] - cos(angle) * (end_width / 2), branch.end_point[1] - sin(angle) * (end_width / 2))
        self.draw.polygon([p1, p4, p3, p2],
                          fill=self.get_color(branch.n))

    def get_width(self, n):  # n - number of iteration
        return 0.8 ** (n * 1.9) / (1 + (0.1 * self.year // self.year_of_branches))

    def get_color(self, n):  # n - number of iteration
        if self.inverse:
            return 220, 220, 220, 255 - n * 2
        else:
            return 0, 0, 0, 100 + n * 10

    # point - tuple (x, y), alpha - angle, n - number of iteration, alpha_pre - angle of previous branch
    def branch(self, point, alpha, n, alpha_pre, id_pre):
        id = len(self.all_branches[n])
        alpha = alpha % (pi * 2)
        self.full_n += 1
        x, y = point
        length_const = random() / 10 + 0.7 + 0.2 ** n
        angle = self.null_alpha * self.wind_influence ** n + alpha
        x1 = x + cos(angle) * self.null_l[n] * length_const ** n
        y1 = y - sin(angle) * self.null_l[n] * length_const ** n
        branch = Branch(id=id,
                        id_pre=id_pre,
                        length_const=length_const,
                        start_width=self.get_width(n),
                        end_width=self.get_width(n + 1),
                        alpha=alpha,
                        alpha_pre=alpha_pre,
                        start_point=point,
                        end_point=(x1, y1),
                        n=n)
        self.all_branches[n].append(branch)

    def choose_new_branch(self, start_point, alpha, n, id):
        for i in range((lambda: randint(1, 2) if n > 5 else randint(1, 2))()):
            angle_offset = i
            if randint(0, 1) == 0:
                angle_offset = -i
            r = random()
            if r < 0.5:  # probability of 2 branches
                self.branch(start_point, alpha - angle_offset * self.base_alpha * (random() / 5 + 1), n, alpha, id)
                self.branch(start_point, alpha + angle_offset * self.base_alpha * (random() / 5 + 1), n, alpha, id)
            elif r < 0.51:  # probability of right branch
                self.branch(start_point, alpha + angle_offset * self.base_alpha * (random() / 5 + 1), n, alpha, id)
            elif r < 0.9 + (lambda: 0.11 if n < 7 else 0)():  # probability of left branch
                self.branch(start_point, alpha - angle_offset * self.base_alpha * (random() / 5 + 1), n, alpha, id)

    def grow_tree(self):
        for i in range(self.year // self.year_of_branches):
            self.null_l[i] = (self.max_null_l / self.lifetime * (self.year - i * self.year_of_branches * 1.5)) + i * 2
        self.start_width += 80 / self.lifetime * (0.1 * self.year // self.year_of_branches)

        all_branches = self.all_branches.copy()
        all_branches.append([])

        if len(all_branches[0]) != 0:
            self.recalculate_tree_for_growing()
            if self.year % self.year_of_branches == 0:
                self.all_branches.append([])
                for branch in all_branches[-2]:
                    self.choose_new_branch(branch.end_point, branch.alpha, branch.n + 1, branch.id)
        else:
            self.all_branches.append([])
            self.branch(self.null_point, 0, 0, 0, None)
        self.year += 1

        return self.all_branches

    def recalculate_tree_for_growing(self):
        for level_n, level in enumerate(self.all_branches):
            for branch in level:
                if level_n != 0:
                    branch.start_point = self.all_branches[level_n - 1][branch.id_pre].end_point

                angle = self.null_alpha * self.wind_influence ** branch.n + branch.alpha
                x, y = branch.start_point
                x1 = x + cos(angle) * self.null_l[branch.n] * branch.length_const ** branch.n
                y1 = y - sin(angle) * self.null_l[branch.n] * branch.length_const ** branch.n
                branch.end_point = (x1, y1)

    def draw_tree(self, branches, show=False):
        self.im = Image.new('RGB', self.screen_size, (lambda: (20, 20, 20) if self.inverse else (245, 245, 245))())
        self.draw = ImageDraw.Draw(self.im)  # draw object to draw on image
        for level in branches:
            for branch in level:
                self.draw_branch(branch)

        if show:
            plt.figure(dpi=200)
            plt.gca().set_aspect('equal', adjustable='box')
            plt.imshow(self.im)
        else:
            return self.im

    def growing2gif(self):
        ims = []
        for _ in tqdm(range(self.lifetime)):
            ims.append(self.draw_tree(self.grow_tree()))

        self.draw_tree(self.grow_tree(), show=True)
        ims[0].save('growing.gif', save_all=True, append_images=ims[1:], duration=self.lifetime // 5)
        print("GIF is gifted")

    def wind2gif(self):
        for _ in tqdm(range(self.lifetime)):
            self.grow_tree()

        ims = []
        for i in tqdm(range(self.lifetime)):
            self.recalculate_tree_for_wind((sin(i*0.1)*sin(i*0.2)*sin(i*0.3)*sin(i*0.4)*0.1)*0.2+2)
            ims.append(self.draw_tree(self.all_branches))

        ims[0].save('wind.gif', save_all=True, append_images=ims[1:], duration=self.lifetime//2)
        print("GIF is gifted")

    def recalculate_tree_for_wind(self, angle_wind_const):
        for level_n, level in enumerate(self.all_branches):
            for branch in level:
                if level_n != 0:
                    branch.start_point = self.all_branches[level_n - 1][branch.id_pre].end_point

                angle = self.null_alpha * self.wind_influence ** branch.n + branch.alpha * angle_wind_const
                x, y = branch.start_point
                x1 = x + cos(angle) * self.null_l[branch.n] * branch.length_const ** branch.n
                y1 = y - sin(angle) * self.null_l[branch.n] * branch.length_const ** branch.n
                branch.end_point = (x1, y1)


class Branch:
    def __init__(self, id, id_pre, length_const, start_width, end_width, alpha, alpha_pre, start_point, end_point, n):
        self.id = id
        self.id_pre = id_pre
        self.length_const = length_const
        self.start_width = start_width
        self.end_width = end_width
        self.alpha = alpha
        self.alpha_pre = alpha_pre
        self.start_point = start_point
        self.end_point = end_point
        self.n = n


#tree = Tree()
#tree.wind2gif()
