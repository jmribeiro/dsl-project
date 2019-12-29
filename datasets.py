from abc import abstractmethod

import torch
from torch.utils.data.dataset import Dataset
from torchtext import datasets
from torchtext.data import Field, LabelField, TabularDataset
from torch.utils.data.dataset import random_split
from torchtext.datasets import text_classification


class BaseDataset(Dataset):

    def __init__(self, val_ratio):

        words = Field(batch_first=True, eos_token=".", tokenize="spacy")
        labels = LabelField(dtype=torch.long)

        directory = self.load_dataset(".data")
        training, test = TabularDataset.splits(path=directory, train='train.csv', test='test.csv', format='csv', fields=[('label', labels), ('text', words)])

        # Vocabs
        words.build_vocab(training)
        labels.build_vocab(training)

        # Validation Split
        full_train_len = len(training)
        val_len = int(val_ratio * full_train_len)
        train_len = int(full_train_len - val_len)
        training, validation = random_split(training, [train_len, val_len])

        training.fields = {'text': words, 'label': labels}
        test.fields = {'text': words, 'label': labels}
        validation.fields = {'text': words, 'label': labels}

        # Attributes
        self.n_classes = len(labels.vocab)
        self.n_words = len(words.vocab)
        self.training = training
        self.validation = validation
        self.test = test
        self.padding_value = words.vocab.itos.index(words.pad_token)
        self.end_of_sentence_value = words.vocab.itos.index(words.eos_token)
        self.sort_key = lambda example: example.text

    @abstractmethod
    def load_dataset(self, root):
        raise NotImplementedError()

    def __len__(self):
        return len(self.training)


class YelpDataset(BaseDataset):

    def __init__(self, full=True, ngrams=3):
        self.full = full
        self.ngrams = ngrams
        super(YelpDataset, self).__init__(val_ratio=0.10) # TODO - Confirm correct val ratio

    def load_dataset(self, root):
        if self.full: text_classification.YelpReviewFull(ngrams=self.ngrams, root=root)
        else: text_classification.YelpReviewPolarity(ngrams=self.ngrams, root=root)
        return '.data/yelp_review_full_csv'


class YahooDataset(BaseDataset):

    def __init__(self, ngrams=5):
        self.ngrams = ngrams
        super(YahooDataset, self).__init__(val_ratio=0.10) # TODO - Confirm correct val ratio

    def load_dataset(self, root):
        text_classification.YahooAnswers(ngrams=self.ngrams)
        return '.data/yelp_review_full_csv' # FIXME -> Correct to right directory


class AmazonDataset(Dataset):

    def __init__(self, full=True, ngrams=5):
        self.full = full
        self.ngrams = ngrams
        super(AmazonDataset, self).__init__(val_ratio=0.10) # TODO - Confirm correct val ratio

    def load_dataset(self, root):
        if self.full: text_classification.AmazonReviewPolarity(ngrams=self.ngrams)
        else: text_classification.AmazonReviewPolarity(ngrams=self.ngrams)
        return '.data/yelp_review_full_csv' # FIXME -> Correct to right directory


class IMDBDataset(Dataset):

    def __init__(self):

        words = Field(batch_first=True, eos_token=".", tokenize="spacy")
        labels = LabelField(dtype=torch.long)

        training, test = datasets.IMDB.splits(words, labels)
        training, validation = training.split()

        #words.build_vocab(training, vectors=GloVe(name='6B', dim=300))
        words.build_vocab(training)
        labels.build_vocab(training)

        print(training.examples[0])
        self.n_classes = len(labels.vocab)
        self.n_words = len(words.vocab)
        self.padding_value = words.vocab.itos.index(words.pad_token)
        self.end_of_sentence_value = words.vocab.itos.index(words.eos_token)
        self.training = training
        self.validation = validation
        self.test = test

    def __len__(self):
        return len(self.training)


class YelpDebugDataset(BaseDataset):

    def __init__(self, full=True, ngrams=3):
        self.full = full
        self.ngrams = ngrams
        super(YelpDebugDataset, self).__init__(val_ratio=0.10)  # TODO - Confirm correct val ratio

    def load_dataset(self, root):
        return '.data/yelp_review_full_csv_debug'