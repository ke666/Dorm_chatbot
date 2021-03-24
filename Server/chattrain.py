import nltk
from nltk.stem import WordNetLemmatizer
import json
import pickle
import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout, LSTM
from keras.optimizers import SGD
import random
import os,shutil
import matplotlib.pyplot as plt

def create_model(X_Train, Y_Train, jsonname):
    model = Sequential()
    model.add(Dense(256, input_shape=(len(X_Train[0]),), activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(128, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(len(Y_Train[0]), activation='softmax'))

    if jsonname =='switch':
        sgd = SGD(lr=0.01, decay=1e-8, momentum=0.85, nesterov=True)
    else:
        sgd = SGD(lr=0.01, decay=1e-8, momentum=0.82, nesterov=True)
    model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])
    history = model.fit(np.array(X_Train), np.array(Y_Train), batch_size=5, epochs=200,  verbose=2)
    return model, history

def make_train_set(jsonname):
    lemmatizer = WordNetLemmatizer()
    shutil.copyfile('./words.pkl','./words/'+jsonname+'.pkl')
    shutil.copyfile('./classes.pkl','./classes/'+jsonname+'.pkl')
    words=[]
    classes = []
    documents = []
    ignore_words = ['?', '!','.']
    data_file = open('./json file/' + jsonname + '.json',encoding='utf8').read()
    intents = json.loads(data_file)
    for intent in intents[jsonname]:
        for pattern in intent['patterns']:
            #tokenize each word
            w = nltk.word_tokenize(pattern)
            words.extend(w)
            #add documents in the corpus
            documents.append((w, intent['tag']))
            # add to our classes list
            if intent['tag'] not in classes:
                classes.append(intent['tag'])

    # lemmaztize and lower each word and remove duplicates
    words = [lemmatizer.lemmatize(w.lower()) for w in words if w not in ignore_words]
    words = sorted(list(set(words)))
    classes = sorted(list(set(classes)))
    print (len(documents), "documents", documents)
    print (len(classes), "classes", classes)
    print (len(words), "unique lemmatized words", words)

    pickle.dump(words,open('./words/' + jsonname + '.pkl','wb'))
    pickle.dump(classes,open('./classes/' + jsonname + '.pkl','wb'))
    training = []
    output_empty = [0] * len(classes)
    for doc in documents:
        bag = []
        pattern_words = doc[0]
        pattern_words = [lemmatizer.lemmatize(word.lower()) for word in pattern_words]
        

        for w in words:
            bag.append(1) if w in pattern_words else bag.append(0)
        
        
        output_row = list(output_empty)
        output_row[classes.index(doc[1])] = 1

        training.append([bag, output_row])
    
    random.shuffle(training)
    training = np.array(training)
    train_x = list(training[:,0])
    train_y = list(training[:,1])
    return train_x, train_y

def train(jsonname,fig,axs,col,row):
    X_Train, Y_Train = make_train_set(jsonname)
    model, history = create_model(X_Train,Y_Train,jsonname)
    print(history.history.keys())
    axs[row,col].plot(history.history['loss'])
    axs[row,col].plot(history.history['accuracy'])
    axs[row,col].set_title(jsonname, color='r')
    #fitting and saving the model 
    model.save('./model h5/' + jsonname + '.h5', history)
    print("model created !!!!!!!")

def main():
    arr = os.listdir('./json file')
    if os.path.exists('./model h5'):
        shutil.rmtree('./model h5')
    if os.path.exists('./classes'):
        shutil.rmtree('./classes')
    if os.path.exists('./words'):
        shutil.rmtree('./words')

    os.mkdir('./words')
    os.mkdir('./classes')
    os.mkdir('./model h5')

    row = 0
    column = 0
    fig,axs = plt.subplots(2,3)
    fig.suptitle("Result of Training Model ", fontsize=15, color = 'b')
    for i in arr:
        train(os.path.splitext(i)[0],fig,axs,column,row)
        if (row == 1 and column == 2):
            for ax in axs.flat:
                ax.set(xlabel='epoch', ylabel='value')
            for ax in axs.flat:
                ax.label_outer()
            plt.show()
            return
        elif (row==1):
            row = 0
            column = column + 1
        else:
            row = row + 1
    

main()