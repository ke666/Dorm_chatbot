 
import math 
from random import shuffle 

def ReadData(fileName):
    f = open(fileName,'r')
    lines = f.read().splitlines()
    f.close()
    features = lines[0].split(', ')[:-1]
    items = []
    for i in range(1, len(lines)):
        line = lines[i].split(', ')
        itemFeatures = {'Class': line[-1]}
        for j in range(len(features)):
            f = features[j]
            v = float(line[j])
            itemFeatures[f] = v
        items.append(itemFeatures)
    shuffle(items)
    return items


def EuclideanDistance(x, y): 
	S = 0
	for key in x.keys(): 
		S += math.pow(x[key] - y[key], 2) 
	return math.sqrt(S) 

def CalculateNeighborsClass(neighbors, k): 
	count = {} 
	for i in range(k): 
		if neighbors[i][1] not in count: 
			count[neighbors[i][1]] = 1
		else: 
			count[neighbors[i][1]] += 1
	return count 

def FindMax(Dict): 
	maximum = -1
	classification = '' 
	for key in Dict.keys(): 
		if Dict[key] > maximum: 
			maximum = Dict[key] 
			classification = key 
	return (classification, maximum) 


def Classify(nItem, k, Items):
	neighbors = []
	for item in Items:
		# Find Euclidean Distance 
		distance = EuclideanDistance(nItem, item)
		# Update neighbors, either adding the
		# current item in neighbors or not. 
		neighbors = UpdateNeighbors(neighbors, item, distance, k)

	# Count the number of each class 
	# in neighbors 
	count = CalculateNeighborsClass(neighbors, k) 
	# Find the max in count, aka the 
	# class with the most appearances 
	return FindMax(count) 


def UpdateNeighbors(neighbors, item, distance, k, ): 
	if len(neighbors) < k: 
		# List is not full, add 
		# new item and sort 
		neighbors.append([distance, item['Class']]) 
		neighbors = sorted(neighbors) 
	else: 
		# List is full Check if new 
		# item should be entered 
		if neighbors[-1][0] > distance: 
			# If yes, replace the 
			# last element with new item 
			neighbors[-1] = [distance, item['Class']] 
			neighbors = sorted(neighbors) 
	return neighbors 

def K_FoldValidation(K, k, Items): 
	if K > len(Items): 
		return -1
	# The number of correct classifications 
	correct = 0
	# The total number of classifications 
	total = len(Items) * (K - 1) 
	# The length of a fold 
	l = int(len(Items) / K)
	for i in range(K): 
		# Split data into training set 
		# and test set 
		trainingSet = Items[i * l:(i + 1) * l] 
		testSet = Items[:i * l] + Items[(i + 1) * l:] 

		for item in testSet: 
			itemClass = item['Class'] 
			itemFeatures = {} 
			# Get feature values 
			for key in item: 
				if key != 'Class': 
					# If key isn't "Class", add 
					# it to itemFeatures 
					itemFeatures[key] = item[key] 
			# Categorize item based on 
			# its feature values 
			guess = Classify(itemFeatures, k, trainingSet)[0] 
			if guess == itemClass: 
				# Guessed correctly 
				correct += 1
	accuracy = correct / float(total) 
	return accuracy 


def Evaluate(K, k, items, iterations): 
	# Run algorithm the number of 
	# iterations, pick average 
	accuracy = 0
	for i in range(iterations):
		shuffle(items)
		accuracy += K_FoldValidation(K, k, items)
	print(accuracy / float(iterations))


def main(): 
	items = ReadData('map_data.csv') 
	Evaluate(5, 5, items, 100) 

if __name__ == '__main__': 
    main() 
