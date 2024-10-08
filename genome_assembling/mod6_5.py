# python3
import sys
from collections import deque, defaultdict
class KmerIdMgmt:
    def __init__(self):
        self.id = 0
        self.ids_map = {}
        self.kmers = {}
    def insert(self, kmer):
        if kmer not in self.ids_map:
            self.ids_map[kmer] = self.id
            self.kmers[self.id] = kmer
            self.id += 1
        return self.ids_map[kmer]
class DeBruijnGraph(object):
    def __init__(self, k, reads):
        self.k = k
        self.threshold = self.k + 1
        self.kmer_ids = KmerIdMgmt()
        self.coverage = defaultdict(lambda: 0)
        self.graph = defaultdict(lambda: [set(), 0])
        self.outgoing_num = lambda k: len(self.graph[k][0])
        self.incoming_num = lambda k: self.graph[k][1]
        self.make_deBruijn_graph(self.break_reads_into_kmers(reads))
    def break_reads_into_kmers(self, reads):
        break_read = lambda read: [read[j:j + self.k] for j in range(len(read) - self.k + 1)]
        return [kmer for read in reads for kmer in break_read(read)]
    def make_deBruijn_graph(self, kmers):
        def add_edge(graph, coverage, left, right):
            coverage[(left, right)] += 1
            if right not in graph[left][0]:
                graph[left][0].add(right)
                graph[right][1] += 1
        for kmer in kmers:
            left = self.kmer_ids.insert(kmer[:-1])
            right = self.kmer_ids.insert(kmer[1:])
            if left != right:
                add_edge(self.graph, self.coverage, left, right)
    def remove_leaves(self):
        removable = [k for k, v in self.graph.items() if len(v[0]) == 0]
        for k in removable:
            del self.graph[k]
class TipRemoval(DeBruijnGraph):
    def __init__(self, k, reads):
        DeBruijnGraph.__init__(self, k, reads)
    def remove_tips(self):
        for k, v in self.graph.items():
            if self.outgoing_num(k) == 1 and self.incoming_num(k) == 0:
                find_and_remove = self.find_and_remove_incoming
            elif self.outgoing_num(k) > 1:
                find_and_remove = self.find_and_remove_outgoing
            else:
                continue
            condition = True
            while condition:
                condition = False
                for edge in v[0]:
                    if find_and_remove(edge, 0):
                        v[0].remove(edge)
                        condition = True
                        break
    def find_and_remove_outgoing(self, current, depth):
        if self.outgoing_num(current) > 1 or self.incoming_num(current) > 1:
            return False
        if depth == self.threshold:
            return False
        if self.outgoing_num(current) == 0:
            return True
        if self.find_and_remove_outgoing(next(iter(self.graph[current][0])), depth + 1):
            to = next(iter(self.graph[current][0]))
            self.graph[current][0].pop()
            self.graph[to][1] -= 1
            return True
        return False
    def find_and_remove_incoming(self, current, depth):
        if self.outgoing_num(current) == 0 or self.incoming_num(current) > 1:
            return True
        if depth == self.threshold:
            return False
        if self.find_and_remove_incoming(next(iter(self.graph[current][0])), depth + 1):
            to = next(iter(self.graph[current][0]))
            self.graph[current][0].pop()
            self.graph[to][1] -= 1
            return True
        return False
class BubbleRemoval(TipRemoval):
    def __init__(self, k, reads):
        TipRemoval.__init__(self, k, reads)
        self.paths = {}
    def remove_bubbles(self):
        for k, v in self.graph.items():
            if self.outgoing_num(k) > 1:
                self.dfs(path=[k], current=k, depth=0)
        for pair, candidates_list in self.paths.items():
            source, target = pair[0], pair[1]
            best_path = max(candidates_list, key=lambda item: item[1])[0]
            for path, _ in candidates_list:
                if best_path == path or not self.bubble_possible(source, target):
                    continue
                if self.paths_disjoint(best_path, path) and self.path_exists(path):
                    self.remove_path(path)
    def bubble_possible(self, source, target):
        return len(self.graph[source][0]) > 1 and self.graph[target][1] > 1
    def path_exists(self, path):
        for j in range(len(path) - 1):
            if path[j + 1] not in self.graph[path[j]][0]:
                return False
        return True
    def remove_path(self, path):
        for j in range(len(path) - 1):
            self.graph[path[j]][0].remove(path[j + 1])
            self.graph[path[j + 1]][1] -= 1
            del self.coverage[(path[j], path[j + 1])]
    def paths_disjoint(self, a, b):
        return len(set(a) & set(b)) == 2  
    def dfs(self, path, current, depth):
        if current != path[0] and self.incoming_num(current) > 1:
            weight = sum(self.coverage[(path[i], path[i + 1])] for i in range(len(path) - 1)) / len(path)
            self.paths.setdefault((path[0], current), list()).append((path[:], weight))
        if depth == self.threshold:
            return
        for next_ in self.graph[current][0]:
            if next_ not in path:
                path.append(next_)
                self.dfs(path, next_, depth + 1)
                path.remove(next_)
class PhiX174GenomeAssembler(BubbleRemoval):
    def __init__(self, k, reads):
        BubbleRemoval.__init__(self, k, reads)
    def make_Euler_cycle(self):
        verteces = deque()
        path = []
        current = next(iter(self.graph))
        verteces.append(current)
        while verteces:
            current = verteces[0]
            if len(self.graph[current][0]) != 0:
                t = next(iter(self.graph[current][0]))
                verteces.append(t)
                self.graph[current][0].remove(t)
                continue
            path.append(current)
            verteces.popleft()
        return path
    def assemble(self):
        self.remove_tips()
        self.remove_leaves()
        self.remove_bubbles()
        cycle = self.make_Euler_cycle()
        circular_genome = self.kmer_ids.kmers[cycle[0]]
        for i in range(1, len(cycle) - (self.k - 1)):
            circular_genome += self.kmer_ids.kmers[cycle[i]][-1]
        return circular_genome
def pre_process():
    reads = sys.stdin.read().strip().split()
    kmers = [kmer for read in reads for kmer in [read[j:j + k] for j in range(len(read) - k + 1)]]
    return build_deBruijn_graph(kmers)
def build_deBruijn_graph(kmers):
    graph = defaultdict(lambda: [set(), 0])
    coverage = defaultdict(lambda: 0)
    for kmer in kmers:
        prefix, suffix = kmer[:-1], kmer[1:]
        if prefix != suffix:
            coverage[(prefix, suffix)] += 1
            if suffix not in graph[prefix][0]:
                graph[prefix][0].add(suffix)
                graph[suffix][1] += 1
    return graph, coverage
def tips_removal(graph):
    for value in graph.values():
        if len(value[0]) == 1 and value[1] == 0:
            find_and_remove = remove_incoming
        elif len(value[0]) > 1:
            find_and_remove = remove_outgoing
        else:
            continue
        condition = True
        while condition:
            condition = False
            for edge in value[0]:
                removed, graph = find_and_remove(edge, 0, graph)
                if removed:
                    value[0].remove(edge)
                    condition = True
                    break
    return graph
def remove_outgoing(current, depth, graph):
    k = 20
    if len(graph[current][0]) > 1 or graph[current][1] > 1 or depth == k:
        return False, graph
    elif len(graph[current][0]) == 0:
        return True, graph
    removed, graph = remove_outgoing(next(iter(graph[current][0])), depth + 1, graph)
    if removed:
        to = next(iter(graph[current][0]))
        graph[current][0].pop()
        graph[to][1] -= 1
        return True, graph
    return False, graph
def remove_incoming(current, depth, graph):
    k = 20
    if depth == k: return False, graph
    if len(graph[current][0]) == 0 or graph[current][1] > 1: return True, graph
    removed, graph = remove_incoming(next(iter(graph[current][0])), depth + 1, graph)
    if removed:
        to = next(iter(graph[current][0]))
        graph[current][0].pop()
        graph[to][1] -= 1
        return True, graph
    return False, graph
def leaves_removal(graph):
    removable = [key for key, value in graph.items() if len(value[0]) == 0]
    for node in removable:
        del graph[node]
    return graph
if __name__ == "__main__":
    k = 20
    reads = sys.stdin.read().split()
    assembler = PhiX174GenomeAssembler(k, reads)
    print(assembler.assemble())
