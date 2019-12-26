import copy
from itertools import chain

sample = '''
#75#8####
###4##63#
##6#5#9##
1##3###4#
#####5#2#
##8######
#####238#
61######2
9########'''.strip()

sample = '''
375#8#214
891427635
246153978
12#3###4#
#####5#2#
##82#####
#####238#
613#####2
982#3####'''.strip()

class Cell(object):
    def __init__(self, x, y, values):
        self.x = x
        self.y = y
        self.values = values

    def isfixed(self):
        return len(self.values) == 1

    def fixed(self):
        return list(self.values)[0]

    def __repr__(self):
        return self.fmtopt()

    def fmtval(self):
        return str(self.fixed()) if self.isfixed() else '-'

    def fmtopt(self):
        return '[%s]' % ''.join(
            str(i) if i in self.values else ' ' for i in range(1, 10)
        )

    def discard(self, value):
        found = value in self.values
        self.values.discard(value)
        return found


class Board(object):
    def __init__(self, depth=0):
        self.depth = depth
        self.cells = [
            Cell(i % 9, i // 9, {1, 2, 3, 4, 5, 6, 7, 8, 9})
            for i in range(81)
        ]

    def clone(self):
        return copy.deepcopy(self)

    def get(self, x, y):
        return self.cells[x + y * 9]

    def set(self, x, y, values):
        i = x + y * 9
        self.cells[i].values = values

    def __repr__(self):
        return self.fmtopt()

    def fmtval(self):
        buf = []
        for y in range(9):
            for x in range(9):
                buf.append(self.get(x, y).fmtval())
            buf.append('\n')
        return ''.join(buf)

    def fmtopt(self):
        buf = []
        for y in range(9):
            for x in range(9):
                buf.append(self.get(x, y).fmtopt())
            buf.append('\n')
        return ''.join(buf)

    def prune(self):
        modified, solved = 0, 0
        for y in range(9):
            for x in range(9):
                c = self.get(x, y)
                if c.isfixed():
                    v = c.fixed()
                    for n in self.neighbours(x, y):
                        if n.discard(v):
                            modified += 1
                            if n.isfixed():
                                solved += 1
                                self.debug('FOUND', n)

        return (modified, solved)

    def debug(self, msg, cell):
        buf = []
        buf.append(msg)
        buf.append('(%d,%d)' % (cell.x, cell.y))
        buf.append('%s%d' % (chr(65 + cell.y), cell.x + 1))
        buf.append('=')
        if cell.isfixed():
            buf.append(str(cell.fixed()))
        else:
            buf.append(cell.fmtopt())
        print(' '.join(buf))

    def pruneall(self):
        while self.prune() > 0:
            pass

    def solve(self):
        solved = 0
        for y in range(9):
            for x in range(9):
                c = self.get(x, y)
                #print('ROW', x, y, [(n.x, n.y) for n in self.row(c.x, c.y)])
                if not c.isfixed():
                    opts = options(self.row(c.x, c.y))
                    opts = c.values.difference(opts)
                    if len(opts) == 1:
                        self.set(x, y, opts)
                        solved += 1
                        self.debug('FOUND-ROW', c)

                #print('COL', x, y, [(n.x, n.y) for n in self.col(c.x, c.y)])
                if not c.isfixed():
                    opts = options(self.col(c.x, c.y))
                    opts = c.values.difference(opts)
                    if len(opts) == 1:
                        self.set(x, y, opts)
                        solved += 1
                        self.debug('FOUND-COL', c)

                #print('BOX', x, y, [(n.x, n.y) for n in self.box(c.x, c.y)])
                if not c.isfixed():
                    opts = options(self.box(c.x, c.y))
                    opts = c.values.difference(opts)
                    if len(opts) == 1:
                        self.set(x, y, opts)
                        solved += 1
                        self.debug('FOUND-BOX', c)
        return solved

    def solve2(self):
        self.pruneall()

        if self.issolved() or not self.isvalid():
            # print('-' * 40)
            # print('RETURN', self.issolved(), self.isvalid())
            # print(self.fmtval())
            print('-', end='', flush=True)
            return self.issolved()

        cs = (c for c in self.cells if not c.isfixed())
        cs = sorted(cs, key=lambda x: len(x.values))
        for c in cs:
            # print(c)
            for v in c.values:
                b = self.clone()
                b.depth += 1
                # print('-' * 40)
                # print('BRANCH-%d' % b.depth, c.x, c.y, c.fmtopt(), v)
                b.set(c.x, c.y, {v})
                # b.pruneall()
                # print(c, c.x, c.y)
                # print(b.fmtval())
                # print(b.fmtopt())
                # exit()

                assert self.get(c.x, c.y).values != b.get(c.x, c.y).values
                # print(b.fmtopt())
                print('+%d(%d)' % (b.depth, len(cs)), end='', flush=False)
                if b.solve():
                    self.cells = b.cells
                    return self.issolved()

    def row(self, x, y):
        return (self.get(i, y) for i in range(9) if i != x)

    def col(self, x, y):
        return (self.get(x, i) for i in range(9) if i != y)

    def box(self, x, y):
        ox = x // 3 * 3
        oy = y // 3 * 3
        return (
            self.get(ox + i % 3, oy + i // 3)
            for i in range(9) if x != (ox + i % 3) or y != (oy + i // 3)
        )

    def neighbours(self, x, y):
        return chain(self.box(x, y), self.row(x, y), self.col(x, y))

    def issolved(self):
        for c in self.cells:
            if not c.isfixed():
                return False
        return True

    def isvalid(self):
        for c in self.cells:
            if len(c.values) == 0:
                return False
        return True


def fixed(cells):
    return {
        v for c in cells for v in c.values if c.isfixed()
    }


def options(cells):
    return {v for c in cells for v in c.values}


def complement(values):
    return {1, 2, 3, 4, 5, 6, 7, 8, 9}.difference(values)


def parse(s):
    b = Board()
    y = 0
    for line in s.split('\n'):
        x = 0
        for ch in line:
            if ch.isdigit():
                b.set(x, y, {int(ch)})
            x += 1
        y += 1
    return b


b = parse(sample)
print(b.fmtopt())

while not b.issolved():
    m, s = b.prune()
    print(b.fmtval())
    b.solve()
    print(b.fmtval())

print(b.fmtval())
