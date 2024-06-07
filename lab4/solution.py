import numpy as np
import sys

def load_data(file_path):
    with open(file_path, 'r') as f:
        header = f.readline().strip().split(',')
        lines = f.readlines()

    data = []
    for line in lines:
        parts = line.strip().split(',')
        features = list(map(float, parts[:-1]))
        labels = float(parts[-1])
        data.append(features + [labels])

    data = np.array(data)
    X = data[:, :-1]
    y = data[:, -1]
    return header, X, y

class NeuralNetwork:
    def __init__(self, input_size, hidden_layers, output_size=1):
        self.weights = []
        self.biases = []
        self.different_squared = 999999.0

        layer_sizes = [input_size] + hidden_layers + [output_size]
        for i in range(len(layer_sizes) - 1):
            self.weights.append(np.random.normal(0, 0.01, (layer_sizes[i], layer_sizes[i + 1])))
            self.biases.append(np.random.normal(0, 0.01, (layer_sizes[i + 1],)))

def sigmoid(net):
    return 1 / (1 + np.exp(-net))

def evaluate(X, y, population):
    for p in population:
        different_squared = 0.0

        for index1 in range(len(X)):
            input_data = X[index1].copy()

            for index2, layer in enumerate(p.weights):
                result = np.add(np.dot(input_data, layer), p.biases[index2])
                if index2 != len(p.weights) - 1:
                    result = sigmoid(result)
                input_data = result
            different_squared += (y[index1] - result) ** 2

        different_squared = different_squared / len(X)
        p.different_squared = different_squared

def crossover(parent1, parent2):
    child = NeuralNetwork(len(parent1.weights[0]), [w.shape[1] for w in parent1.weights[:-1]], 1)
    for i in range(len(parent1.weights)):
        child.weights[i] = (parent1.weights[i] + parent2.weights[i]) / 2
        child.biases[i] = (parent1.biases[i] + parent2.biases[i]) / 2
    return child

def mutate(individual, mutation_rate, mutation_scale):
    for i in range(len(individual.weights)):
        if np.random.rand() < mutation_rate:
            individual.weights[i] += np.random.normal(0, mutation_scale, individual.weights[i].shape)
        if np.random.rand() < mutation_rate:
            individual.biases[i] += np.random.normal(0, mutation_scale, individual.biases[i].shape)

def genetic_algorithm(X_train, y_train, nn_arch, popsize, elitism, mutation_rate, mutation_scale, iterations):
    population = [NeuralNetwork(len(X_train[0]), nn_arch, 1) for _ in range(popsize)]
    for i in range(iterations):
        evaluate(X_train, y_train, population)
        selected_parents = population
        elite = sorted(selected_parents, key=lambda x: x.different_squared)[:elitism]

        if (i + 1) % 2000 == 0:
            print(f"[Train error @{i + 1}]: {elite[0].different_squared[0]}")

        children = []
        while len(children) < popsize:
            parent1 = np.random.choice(selected_parents)
            parent2 = np.random.choice(selected_parents)
            child = crossover(parent1, parent2)
            mutate(child, mutation_rate, mutation_scale)
            children.append(child)

        population = elite + children[len(elite):]
    return population


if __name__ == "__main__":
    train_path = sys.argv[2]
    test_path = sys.argv[4]
    nn_type = sys.argv[6]
    nn_arch = []
    if nn_type == "5s":
        nn_arch.append(5)
    elif nn_type == "20s":
        nn_arch.append(20)
    elif nn_type == "5s5s":
        nn_arch.append(5)
        nn_arch.append(5)
    popsize = int(sys.argv[8])
    elitism = int(sys.argv[10])
    mutation_rate = float(sys.argv[12])
    mutation_scale = float(sys.argv[14])
    iterations = int(sys.argv[16])


    header_train, X_train, y_train = load_data(train_path)
    header_test, X_test, y_test = load_data(test_path)

    final_population = genetic_algorithm(X_train, y_train, nn_arch, popsize, elitism, mutation_rate, mutation_scale, iterations)

    evaluate(X_test, y_test, final_population)
    best_individual = min(final_population, key=lambda x: x.different_squared)
    print(f"[Test error]: {best_individual.different_squared[0]}")
