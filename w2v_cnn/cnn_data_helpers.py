import numpy as np
import re
import itertools
from collections import Counter


def load_data_and_labels(dataset):
    """
    Loads MR polarity data from files, splits the data into words and generates labels.
    Returns split sentences and labels.
    """
    template_txt = '../data/tweets/txt/%s'


    pathtxt = template_txt % dataset

    x_text=[line.split('\t')[2] for line in open(pathtxt, "r").readlines()]
    x_text = [s.split(" ") for s in x_text]

    y = []
    for line in open(pathtxt, "r").readlines():
        senti=line.split('\t')[1]
        if  senti == 'objective':
            y.append([0, 1, 0])

        elif senti == 'positive':
            y.append([0, 0, 1])

        else:  # negative
            y.append([1, 0, 0])

    return [x_text, y]


def pad_sentences(sentences, padlen, padding_word="<PAD/>"):
    """
    Pads all sentences to the same length. The length is defined by the longest sentence.
    Returns padded sentences.
    """
    if padlen==None:
        sequence_length = max(len(x) for x in sentences)
    else:
        sequence_length=padlen

    padded_sentences = []
    for i in range(len(sentences)):
        sentence = sentences[i]
        num_padding = sequence_length - len(sentence)
        new_sentence = sentence + [padding_word] * num_padding
        padded_sentences.append(new_sentence)
    return padded_sentences


def build_vocab(sentences):
    """
    Builds a vocabulary mapping from word to index based on the sentences.
    Returns vocabulary mapping and inverse vocabulary mapping.
    """
    # Build vocabulary
    word_counts = Counter(itertools.chain(*sentences))
    # Mapping from index to word
    vocabulary_inv = [x[0] for x in word_counts.most_common()]
    vocabulary_inv = list(sorted(vocabulary_inv))
    # Mapping from word to index
    vocabulary = {x: i for i, x in enumerate(vocabulary_inv)}
    return [vocabulary, vocabulary_inv]



def build_input_data_with_w2v(sentences, labels, w2vmodel):
    """
    Maps sentencs and labels to vectors based on a vocabulary.
    """
    def get_index_of_voca(model, word):
        try:
            return model[word]
        except:
            return np.array([np.float32(0.0)]*400)

    x = np.array([[get_index_of_voca(w2vmodel,word) for word in sentence] for sentence in sentences])
    y = np.array(labels)
    return [x, y]


def load_data(dataset, w2vmodel, padlen=None):
    """
    Loads and preprocessed data for the MR dataset.
    Returns input vectors, labels, vocabulary, and inverse vocabulary.
    """
    # Load and preprocess data
    sentences, labels = load_data_and_labels(dataset)
    sentences_padded = pad_sentences(sentences, padlen)

    x, y = build_input_data_with_w2v(sentences_padded, labels, w2vmodel)
    return [x, y]


def batch_iter(data, batch_size, num_epochs, shuffle=True):
    """
    Generates a batch iterator for a dataset.
    """
    data = np.array(data)
    data_size = len(data)
    num_batches_per_epoch = int(len(data)/batch_size) + 1
    for epoch in range(num_epochs):
        # Shuffle the data at each epoch
        if shuffle:
            shuffle_indices = np.random.permutation(np.arange(data_size))
            shuffled_data = data[shuffle_indices]
        else:
            shuffled_data = data
        for batch_num in range(num_batches_per_epoch):
            start_index = batch_num * batch_size
            end_index = min((batch_num + 1) * batch_size, data_size)
            yield shuffled_data[start_index:end_index]
