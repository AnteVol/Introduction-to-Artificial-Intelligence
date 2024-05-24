import math
import sys
def load_data(dataset):
    with open(  dataset, mode='r') as file:
        data_dict = {'label': [], 'data': []}
        lines = file.readlines()
        header = []

        for index, line in enumerate(lines):
            data = line.strip().split(',')
            if index == 0:
                header = data[:-1]
            else:
                data_dict['label'].append(data[-1])
                data_dict['data'].append(data[:-1])

    return header, data_dict


class Node:
    def __init__(self, label, subtrees, y, labels):
        self.label = label
        self.subtrees = subtrees
        self.y = y
        self.labels = labels


class Leaf:
    def __init__(self, label):
        self.label = label


class Model:
    def __init__(self, depth):
        self.features = []
        self.trainData = {'label': [], 'data': []}
        self.testData = {'label': [], 'data': []}
        self.treeForPrint = None
        self.depth = depth

    def fit(self, trainData):
        self.features, helpDict = load_data(trainData)
        self.trainData['label'] = helpDict['label']
        self.trainData['data'] = helpDict['data']
        self.tree = ID3(self.trainData, self.trainData, self.features, 1, self.depth)
        print("[BRANCHES]: ")
        self.printTree(self.tree)

    def printTree(self, node, path=[]):
        if isinstance(node, Leaf):
            print(''.join(path) + f'{node.label}')
        else:
            for i, (value, subtree) in enumerate(node.subtrees):
                new_path = path + [f'{node.y}:{node.label}={value} ']
                self.printTree(subtree, new_path)

    def predict(self, testData):
        self.features, helpDict = load_data(testData)
        self.testData['label'] = helpDict['label']
        self.testData['data'] = helpDict['data']
        print("[PREDICTIONS]: ", end='')
        predictions = []
        #predict
        for line in self.testData['data']:
            node = self.tree
            while not isinstance(node, Leaf):
                x = node.label
                type = line[self.features.index(x)]

                same = False
                for value, subtree in node.subtrees:
                    if value == type:
                        node = subtree
                        same = True
                        break

                if not same:
                    label_counts = {}
                    for label in node.labels:
                        if label in label_counts:
                            label_counts[label] += 1
                        else:
                            label_counts[label] = 1

                    sorted_labels = sorted(label_counts.items(), key=lambda x: (x[1], x[0]))
                    best = max(sorted_labels, key=lambda x: x[1])
                    predictions.append(best[0])
                    break

            if isinstance(node, Leaf):
                predictions.append(node.label)

        for prediction in predictions:
            print(f'{prediction} ', end='')
        print()

        #accuracy
        correct = 0
        for index1, label1 in enumerate(self.testData['label']):
            for index2, label2 in enumerate(predictions):
                if index1 == index2 and label1 == label2:
                    correct+= 1
        total = len(predictions)
        accuracy = round(correct/total, 5)
        print(f'[ACCURACY]: {accuracy:.5f}')

        #matrix
        print("[CONFUSION_MATRIX]:")
        unique_labels = sorted(set(self.testData['label']))
        confusion_matrix = [[0 for _ in unique_labels] for _ in unique_labels]

        for true, predicted in zip(self.testData['label'], predictions):
            true_index = unique_labels.index(true)
            predicted_index = unique_labels.index(predicted)
            confusion_matrix[true_index][predicted_index] += 1

        for row in confusion_matrix:
            print(' '.join(map(str, row)))



def ID3(D, Dp, X, y, border):
    if len(D['data']) == 0:
        countOfDp = {}
        for element in Dp['label']:
            if element not in countOfDp:
                countOfDp[element] = 1
            else:
                countOfDp[element] += 1
        v = max(countOfDp.items(), key=lambda item: (item[1], -ord(item[0][0])))[0]
        return Leaf(v)

    if len(set(D['label'])) == 1:
        return Leaf(D['label'][0])

    if float(y) > float(border):
        values = sorted(list(set(D['label'])))
        v = max(values, key=D['label'].count)
        return Leaf(v)

    if len(X) == 0:
        countOfD = {}
        for element in D['label']:
            if element not in countOfD:
                countOfD[element] = 1
            else:
                countOfD[element] += 1
        v = max(countOfD, key=countOfD.get)
        return Leaf(v)

    IG_values = [IG(D, x) for x in range(len(X))]
    max_IG_value = max(IG_values)
    max_IG_names = [X[i] for i, ig in enumerate(IG_values) if ig == max_IG_value]
    x = max_IG_names[0]
    index_x = X.index(x)

    print_IGs(X, IG_values)

    subtrees = []
    Vx = sorted(set([line[index_x] for line in D['data']]))
    for v in Vx:
        newX = [feature for feature in X if feature != x]
        Dxv = {'label': [], 'data': []}
        for i, line in enumerate(D['data']):
            if line[index_x] == v:
                new_data = line[:index_x] + line[index_x + 1:]
                Dxv['data'].append(new_data)
                Dxv['label'].append(D['label'][i])
        t = ID3(Dxv, D, newX, y + 1, border)
        subtrees.append((v, t))
    return Node(x, subtrees, y, D['label'])

def print_IGs(features, IG_values):
    IG_pairs = []
    for i in range(len(features)):
        IG_pairs.append((features[i], IG_values[i]))
    IG_pairs.sort(key=lambda x: (-x[1], x[0]))
    print(" ".join(["IG(" + pair[0] + ")=" + str(round(pair[1], 4)) for pair in IG_pairs]))
def IG(D, index):
    Ed = Entropy(D['label'])
    sum = 0
    dictOfValues = {}

    for line in D['data']:
        label = line[index]
        if label not in dictOfValues:
            dictOfValues[label] = 1
        else:
            dictOfValues[label] += 1

    for key in dictOfValues.keys():
        v = key
        Dxv = []
        for i, line in enumerate(D['data']):
            if line[index] == v:
                Dxv.append(D['label'][i])

        size = len(Dxv)
        EDxv = Entropy(Dxv)
        sum += (size * EDxv) / len(D['data'])

    IG_value = Ed - sum
    return IG_value


def Entropy(K):
    distinct_labels = set(K)
    total = len(K)
    entropy = 0
    for label in distinct_labels:
        p = K.count(label) / total
        entropy += p * math.log2(p)
    realEntropy = -entropy

    return realEntropy



if __name__ == "__main__":
    train_data_path = sys.argv[1]
    test_data_path = sys.argv[2]

    if len(sys.argv) == 4:
        depth = sys.argv[3]
        id3 = Model(depth)
    else:
        depth =float('inf')
        id3 = Model(depth)

    id3.fit(train_data_path)
    id3.predict(test_data_path)
