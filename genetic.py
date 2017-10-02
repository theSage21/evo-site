import os
import random
import json


cross_probability = 0.8
mutate_probability = 0.01


def roulette(wts):
    "return index in proportion to weights"
    m = min(wts)
    W = [i-m for i in wts]
    mark = random.random() * sum(W)
    total = 0
    for i, v in enumerate(W):
        total += v
        if total >= mark:
            return i


def make_token():
    "random token"
    a = '1234567890abcdefghijklmnopqrstuvwxyz'
    return ''.join(random.choice(a) for _ in range(100))


def random_color():
    "make a random color"
    nums = '0123456789ABCDEF'
    return ''.join(random.choice(nums) for _ in range(6))


def mutate(color):
    "mutate a color"
    r, g, b = color[:2], color[2:4], color[4:]
    if random.random() < mutate_probability:
        r = random_color()[:2]
    if random.random() < mutate_probability:
        g = random_color()[:2]
    if random.random() < mutate_probability:
        b = random_color()[:2]
    return r+g+b


def crossover(c1, c2):
    "cross two colors"
    if random.random() < cross_probability:
        i = random.choice([0, 2, 4])
        b1 = c1[:i] + c2[i:i+2] + c1[i+2:]
        b2 = c2[:i] + c1[i:i+2] + c2[i+2:]
        c1, c2 = b1, b2
    return c1, c2


class GA:
    def __init__(self, psize=10, minhits=1):
        """populaiton size, minimum hits per gene before evolving next
        population"""
        self.psize = psize
        self.minhits = minhits
        self.load()

    def crossover(self, c1, c2):
        "crossover two page color reps"
        b1, b2 = [], []
        for i, j in zip(c1, c2):
            a, b = crossover(i, j)
            b1.append(a)
            b2.append(b)
        return b1, b2

    def mutate(self, c):
        "mutate a page color reps"
        return [mutate(i) for i in c]

    def genpop(self, pop=None):
        "make a population. If None then generate a new pop"
        if pop is None:
            self.pop = [[random_color() for i in range(6)]
                        for _ in range(self.psize)]
        else:
            self.pop = pop
        self.hits = [0 for _ in range(self.psize)]
        self.serves = [0 for _ in range(self.psize)]

    def evolve_pop(self):
        "Evolve the population"
        fitness = [h/t for h, t in zip(self.hits, self.serves)]
        newpop = []
        for _ in range(self.psize):
            i = roulette(fitness)
            j = roulette(fitness)
            c1, c2 = self.crossover(self.pop[i], self.pop[j])
            c1, c2 = self.mutate(c1), self.mutate(c2)
            newpop.append(c1)
            newpop.append(c2)
        random.shuffle(newpop)
        self.genpop(newpop)

    def get_data(self):
        "Get a page data to sample the fitness"
        token = make_token()
        self.tokenmap[token] = self.current_index
        a = self.pop[self.current_index]
        data = dict(ident=token,
                    sec1c=a[0],
                    sec2c=a[1],
                    sec3c=a[2],
                    bt1c=a[3],
                    bt2c=a[4],
                    bt3c=a[5])
        self.serves[self.current_index] += 1
        self.current_index = (self.current_index + 1) % self.psize
        if min(self.hits) >= self.minhits:
            self.evolve_pop()
        return data

    def load(self):
        if os.path.exists('state'):
            with open('state', 'r') as fl:
                da = json.load(fl)
        else:
            self.genpop()
            da = {'pop': self.pop,
                  'current_index': 0,
                  'hits': self.hits,
                  'tokenmap': {},
                  'psize': self.psize,
                  'serves': self.serves,
                  'minhits': self.minhits}
        self.pop = da['pop']
        self.current_index = da['current_index']
        self.hits = da['hits']
        self.tokenmap = da['tokenmap']
        self.psize = da['psize']
        self.serves = da['serves']
        self.minhits = da['minhits']

    def save(self):
        with open('state', 'w') as fl:
            json.dump({'pop': self.pop,
                       'current_index': self.current_index,
                       'hits': self.hits,
                       'tokenmap': self.tokenmap,
                       'psize': self.psize,
                       'serves': self.serves,
                       'minhits': self.minhits}, fl)

    def mark_hit(self, ident):
        "mark a hit on a page"
        index = self.tokenmap.get(ident)
        if index is not None:
            self.hits[index] += 1
            self.tokenmap.pop(ident)
