import torch
from torch.utils.data.dataset import Dataset
from torchtext import datasets
from torchtext.data import Field, LabelField
from torch.utils.data.dataset import random_split
from torchtext.datasets import text_classification


class YelpReviewFullDataset(Dataset):

    def __init__(self, path):
        """
        Training & Validation
        1. dataset
            get_vocab()
            get_labels() [0...4]
            _data
        2. indices
        ---------------------------
        Test
            get_vocab()
            get_labels() [0...4]
            _data
        """

        train_dataset, test_dataset = text_classification.YelpReviewFull(ngrams=3, root=path)

        train_len = int(len(train_dataset) * .9)
        train_dataset, validation_dataset = random_split(train_dataset, [train_len, len(train_dataset) - train_len])

        self.training = train_dataset
        self.validation = validation_dataset
        self.test = test_dataset

    def __len__(self):
        return len(self.training)

    def training(self):
        return self.training

    def validation(self):
        return self.validation

    def test(self):
        return self.test


class Yelp14Dataset(Dataset):

    def __init__(self):

        self.n_classes = None
        self.n_words = None
        self.training = None
        self.validation = None
        self.test = None

    def __len__(self):
        return len(self.training)


class Yelp15Dataset(Dataset):

    def __init__(self):

        training, test = text_classification.YelpReviewPolarity(ngrams=5)
        train_len = int(len(training) * 0.90)
        training, validation = random_split(training, [train_len, len(training) - train_len])
        words = training.get_vocab()

        self.n_classes = len(training.get_labels())
        self.n_words = len(words)
        self.padding_value = words.itos.index(words.pad_token)
        self.training = training
        self.validation = validation
        self.test = test


    def __len__(self):
        return len(self.training)


class YahooDataset(Dataset):

    def __init__(self):

        training, test = text_classification.YahooAnswers(ngrams=5)
        train_len = int(len(training) * 0.90)
        training, validation = random_split(training, [train_len, len(training) - train_len])
        words = training.get_vocab()

        self.n_classes = len(training.get_labels())
        self.n_words = len(words)
        self.padding_value = words.itos.index(words.pad_token)
        self.training = training
        self.validation = validation
        self.test = test


    def __len__(self):
        return len(self.training)


class IMDBDataset(Dataset):

    def __init__(self):

        words = Field(batch_first=True)
        labels = LabelField(dtype=torch.long)
        training, test = datasets.IMDB.splits(words, labels)
        training, validation = training.split()
        words.build_vocab(training)
        labels.build_vocab(training)

        self.n_classes = len(labels.vocab)
        self.n_words = len(words.vocab)
        self.padding_value = words.vocab.itos.index(words.pad_token)
        self.training = training
        self.validation = validation
        self.test = test

    def __len__(self):
        return len(self.training)


class AmazonDataset(Dataset):

    def __init__(self):

        training, test = text_classification.AmazonReviewPolarity(ngrams=5)
        train_len = int(len(training) * 0.90)
        training, validation = random_split(training, [train_len, len(training) - train_len])
        words = training.get_vocab()

        self.n_classes = len(training.get_labels())
        self.n_words = len(words)
        self.padding_value = words.itos.index(words.pad_token)
        self.training = training
        self.validation = validation
        self.test = test

    def __len__(self):
        return len(self.training)

