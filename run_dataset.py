import argparse
import os
import pathlib

import matplotlib.pyplot as plt
import numpy as np

import torch
from torch import nn
from torchtext.data import BucketIterator
from tqdm import tqdm

from random import getrandbits
from utils import train_batch, evaluate, load_dataset, select_model, load_npy_files

# ############ #
# Presentation #
# ############ #

def plot(epochs, plottable, ylabel, name):
    plt.clf()
    plt.xlabel('Epoch')
    plt.ylabel(ylabel)
    plt.plot(epochs, plottable)
    plt.title(name)
    plt.savefig('%s.pdf' % name, bbox_inches='tight')
    plt.close()


def train(model_name, dataset, opt):

    device = torch.device("cuda:0" if torch.cuda.is_available() and opt.cuda else "cpu")

    if not opt.quiet:
        print(f"*** Setting up {model_name} model on device {device} ***", end="", flush=True)

    model = select_model(model_name, dataset, opt, device)

    if not opt.quiet: print(" (Done)", flush=True)

    if not opt.quiet: print(f"*** Setting up {opt.optimizer} optimizer ***", end="", flush=True)

    optimizer = {
        "adam": torch.optim.Adam,
        "sgd": torch.optim.SGD
    }[opt.optimizer](
        model.parameters(),
        lr=opt.learning_rate,
        weight_decay=opt.l2_decay
    )
    criterion = nn.CrossEntropyLoss()

    if not opt.quiet: print(" (Done)\n", flush=True)

    if not opt.quiet:
        print(f"# ##################### #", flush=True)
        print(f"# Training {model_name} #", flush=True)
        print(f"# ##################### #", flush=True)

    epochs = torch.arange(1, opt.epochs + 1)
    train_mean_losses = []
    valid_accs = []
    train_losses = []

    trainloader, valloader, testloader = BucketIterator.splits((dataset.training, dataset.validation, dataset.test), shuffle=True, batch_size=opt.batch_size, sort_key=dataset.sort_key)

    for epoch in epochs:

        if not opt.quiet: print('\nTraining epoch {}'.format(epoch), flush=True)

        for batch in tqdm(trainloader) if opt.tqdm else trainloader:
            loss = train_batch(batch, model, optimizer, criterion)
            train_losses.append(loss)

        mean_loss = torch.tensor(train_losses).mean().item()
        if not opt.quiet: print('Training loss: %.4f \n' % mean_loss, flush=True)

        train_mean_losses.append(mean_loss)
        valid_accs.append(evaluate(model, valloader))
        if not opt.quiet: print('Valid acc: %.4f \n' % (valid_accs[-1]), flush=True)

    final_test_accuracy = evaluate(model, testloader)
    if not opt.quiet: print('\nFinal Test acc: %.4f \n' % final_test_accuracy, flush=True)

    return train_mean_losses, valid_accs, final_test_accuracy


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    # Main arguments
    parser.add_argument('dataset', choices=['yelp', 'yahoo', 'imdb', 'amazon'], help="Which dataset to train the model on?")

    # Model Parameters
    parser.add_argument('-embeddings_size', type=int, help="Length of the word embeddings.", default=200)
    parser.add_argument('-layers', type=int, help="Number of layers", default=1)
    parser.add_argument('-hidden_sizes', type=int, help="Number of units per hidden layer", default=50)
    parser.add_argument('-bidirectional', action="store_true")
    parser.add_argument('-dropout', type=float, help="Dropout probability", default=0.1)
    parser.add_argument('-attention_threshold', type=float, help="Minimum attention value for phan", default=0.05)

    # Optimization Parameters
    parser.add_argument('-epochs', type=int, default=20)
    parser.add_argument('-optimizer', choices=['sgd', 'adam'], default='adam')
    parser.add_argument('-learning_rate', type=float, default=0.001)
    parser.add_argument('-l2_decay', type=float, default=0.0)
    parser.add_argument('-batch_size', type=int, default=64)
    parser.add_argument('-cuda', action='store_true', help='Use cuda for parallelization if devices available')

    # Miscellaneous
    parser.add_argument('-polarity', action='store_true', help="Positive/Negative labels for datasets.")
    parser.add_argument('-ngrams', type=int, help="N value for the datasets N-Grams.", default=1)
    parser.add_argument('-debug', action='store_true', help="Datasets pruned into smaller sizes for faster loading.")
    parser.add_argument('-quiet', action='store_true', help='No execution output.')
    parser.add_argument('-tqdm', action='store_true', help='Whether or not to use TQDM progress bar in training.')
    parser.add_argument('-nrun', type=int, help="N number of runs.", default=1)
    parser.add_argument('-no_plot', action='store_true', help='Whether or not to plot training losses and validation accuracies.')
    parser.add_argument('-sample',  action='store_true', help="Use sample dataset which correspont to 20% from the entire dataset")
    parser.add_argument('-dataset_size', type=float, help="% to split.", default=.01)

    models = ['han', 'hsan'] # TODO -> Add PSAN when done

    opt = parser.parse_args()

    dataset = load_dataset(opt)

    nruns = torch.arange(1, opt.nrun + 1)

    for nrun in nruns:
        if not opt.quiet: print(f"*** run number  {nrun} ***", end="", flush=True)

        results = {}
        runid = getrandbits(64)
        for model in models:
            train_mean_losses, valid_accs, final_test_accuracy = train(model, dataset, opt)
            results[model] = train_mean_losses, valid_accs, final_test_accuracy
            root = f"results/{opt.dataset}/{model}"
            pathlib.Path(root).mkdir(parents=True, exist_ok=True)
            with open(f"{root}/final_test_accuracy_{runid}.txt", "w") as text_file: text_file.write(f"{final_test_accuracy}")
            np.save(root+f"/train_mean_losses_{runid}.npy", np.array(train_mean_losses))
            np.save(root+f"/valid_accs_{runid}.npy", np.array(valid_accs))
        if not opt.quiet: print(f"*** Plotting validation accuracies and training losses ***", end="", flush=True)
        for model in models:
            root = f"/results/{opt.dataset}/{model}"

            if not opt.debug: path = root
            else: path = f"{root}/debug"

            # from npy files
           #  train_losses, accs,final_accuracy = load_npy_files(path)

            train_mean_losses, valid_accs, final_test_accuracy = results[model]
            try: os.mkdir("plots")
            except FileExistsError: pass
            plot(torch.arange(1, opt.epochs + 1), train_mean_losses, ylabel='Loss', name=f"plots/{runid}-{opt.dataset}-{model}-training-loss")
            plot(torch.arange(1, opt.epochs + 1), valid_accs, ylabel='Accuracy', name=f"plots/{runid}-{opt.dataset}-{model}-validation-accuracy")
        if not opt.quiet: print(" (Done)\n", flush=True)
