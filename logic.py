import numpy as np
import random

class Connection:
    def __init__(self, node, weight : float = None) -> None:
        self.node : Node = node
        if weight == None:
            self.weight = float(random.randrange(-100,100))/100.0
        else:
            self.weight = weight

class Node:
    def __init__(self, function, bias : float, val : float, con_from : list[Connection]) -> None:
        self.con_to = []
        self.con_from : list[Connection] = con_from
        for connection in self.con_from:
            connection.node.con_to.append(Connection(self, connection.weight))
        self.function = function
        self.bias = bias
        self.value = val
        
    def calculate(self):
        self.value += self.bias
        self.function(self) 
    
    def identity(self):
        pass
    
    def thresh_step(self):
        if self.value >= 0.5:
            self.value = 1
        else:
            self.value = 0
    
    def tanh(self):
        self.value = np.tanh(self.value)
    
    def ReLu(self):
        self.value = max(0.0, self.value)
    
    def bs(self):
        self.value = float(self.value >= 1.0)

    def sigmoid(self):
        self.value = 1 / (1 + np.exp(-self.value))

class Graph:
    def __init__(self) -> None:
        self.nodes : list[list[Node]] = []
    
    def sort(self):
        index_dict = {}
        max = 0
        for i, row in enumerate(self.nodes):
            if len(row) > max:
                max = len(row)
            for j, node in enumerate(row):
                index_dict[node] = (i,j)
        for k, v in index_dict.items():
            index_dict[k] = (v[0]*max) + v[1]
        for row in self.nodes:
            for node in row:
                node.con_to = sorted(node.con_to, key=lambda x: index_dict[x.node])
    
    def run(self, inputs : list[float]) -> list[float]:
        self.sort()
        for row, node_list in enumerate(self.nodes):
            for i, node in enumerate(node_list):
                if row == 0:
                    node.value = inputs[i]
                node.calculate()
                for connection in node.con_to:
                    connection.node.value += node.value*connection.weight
        outputs = [output.value for output in self.nodes[-1]]
        for _ in self.nodes:
            for node in _:
                node.value = 0.0
        return outputs

class Agent:
    def __init__(self, inputs : int, outputs : int, output_func, hidden_max : int, hidden_func) -> None:
        self.graph = Graph()
        self.inputs = inputs
        self.outputs = outputs
        self.output_func = output_func
        self.hidden_max = hidden_max
        self.hidden_func = hidden_func
        self.fitness = 0
        self.graph.nodes.append([])
        self.graph.nodes.append([])
        for _ in range(inputs):
            self.graph.nodes[0].append(Node(Node.identity,0.0,0.0,[]))
        for _ in range(outputs):
            self.graph.nodes[1].append(Node(self.output_func,0.0,0.0,[Connection(random.choice(self.graph.nodes[0]))]))
    
    """def fitness_calc(self):
        self.fitness = 0
        for xi, xo in zip(xor_inputs, xor_outputs):
            val = self.graph.run(xi)
            if val[0] == xo[0]:
                self.fitness += 1"""
    
    def mutate(self):
        choice = random.randint(0,5)
        if choice == 0:
            return
        if choice == 1: #Add node
            try:
                node_from_row = random.randrange(0,self.graph.nodes-2)
            except:
                node_from_row = 0
            try:
                node_from = random.choice([node for node in self.graph.nodes[node_from_row] if node.con_to != []])
            except:
                return
            org_connection = random.choice(node_from.con_to)
            org_weight : float = org_connection.weight
            node_to : Node = org_connection.node
            [node_from.con_to.remove(con) for con in node_from.con_to if con.node == node_to]
            [node_to.con_from.remove(con) for con in node_to.con_from if con.node == node_from]
            node_to_row = 0
            for i, row in enumerate(self.graph.nodes):
                if node_to in row:
                    node_to_row = i
                    break
            if node_to_row-node_from_row == 1:
                if len(self.graph.nodes) == self.hidden_max+2:
                    return
                self.graph.nodes.insert(node_to_row, [])
                new_row_index = node_to_row
            else:
                new_row_index = node_from_row+1
            new_node = Node(self.hidden_func, round(random.random(),2), 0.0, [Connection(node_from, org_weight)])
            new_weight = float(random.randrange(-100,100))/100.0
            new_node.con_to.append(Connection(node_to, new_weight))
            node_to.con_from.append(Connection(new_node, new_weight))
            node_from.con_to.append(Connection(new_node, org_weight))
            self.graph.nodes[new_row_index].append(new_node)
        if choice == 2: #New Connection
            options_to = []
            options_from = []
            for j in range(1, len(self.graph.nodes)):
                nodes_before = 0
                for i in range(j):
                    for _ in self.graph.nodes[i]:
                        nodes_before += 1
                for node in self.graph.nodes[j]:
                    if len(node.con_from) < nodes_before:
                        options_to.append((node,j))
                for node in self.graph.nodes[j-1]:
                    options_from.append((node,j-1))
            try:
                node_to = random.choice(options_to)
            except:
                return
            node_from = random.choice(options_from)
            while node_from[1] >= node_to[1] or node_from[0] in [con.node for con in node_to[0].con_from]:
                node_from = random.choice(options_from)
            weight = float(random.randrange(-100,100))/100.0
            node_to[0].con_from.append(Connection(node_from[0],weight))
            node_from[0].con_to.append(Connection(node_to[0],weight))
        if choice == 3: #Remove Connection
            options_from = []
            options_to = []
            for j in range(2, len(self.graph.nodes)):
                for node in self.graph.nodes[j-1]:
                    if len(node.con_to) > 1:
                        options_from.append(node)
                for node in self.graph.nodes[j]:
                    if len(node.con_from) > 1:
                        options_to.append(node)
            if options_from == [] or options_to == []:
                return
            node_from = random.choice(options_from)
            node_to = random.choice(options_to)
            while node_to not in [con.node for con in node_from.con_to]:
                node_to = random.choice(options_to)
            [node_from.con_to.remove(con) for con in node_from.con_to if con.node == node_to]
            [node_to.con_from.remove(con) for con in node_to.con_from if con.node == node_from]
        if choice == 4: #Change connection weight
            options_from = []
            for j in range(1, len(self.graph.nodes)):
                for node in self.graph.nodes[j-1]:
                    if len(node.con_to) != 0:
                        options_from.append(node)
            if options_from == []:
                return
            node_from = random.choice(options_from)
            node_to = random.choice(node_from.con_to).node
            new_weight = float(random.randrange(-100,100))/100.0
            for con in node_from.con_to:
                if con.node == node_to:
                    con.weight = new_weight
            for con in node_to.con_from:
                if con.node == node_from:
                    con.weight = new_weight
        if choice == 5: #Change bias weight
            try:
                node = random.choice(random.choice(self.graph.nodes[1:-1]))
            except:
                return
            node.bias = round(random.random(),2)
            
            
            
        