import math

import torch
from torch import optim
from torch.nn import CrossEntropyLoss

from models import LSTMSimple
from utils import SlidingWindowLoader, read_songs_from, char_mapping

# Check if cuda is supported
if torch.cuda.is_available():
    print("CUDA supported")
    computing_device = torch.device("cuda")
else:
    print("CUDA not supported")
    computing_device = torch.device("cpu")


def encode_songs(songs, char_to_idx):
    """
    Return a list of encoded songs where each char in a song is mapped to an index as in char_to_idx
    :param songs: List[String]
    :param char_to_idx: Dict{char -> int}
    :return: List[Tensor]
    """
    songs_encoded = [0] * len(songs)
    for i, song in enumerate(songs):
        chars = list(song)
        result = torch.zeros(len(chars)).to(computing_device)
        for j, ch in enumerate(chars):
            result[j] = char_to_idx[ch]
        songs_encoded[i] = result
    return songs_encoded


def to_onehot(t):
    """
    Take a list of indexes and return a one-hot encoded tensor
    :param t: 1D Tensor of indexes
    :return: 2D Tensor
    """
    inputs_onehot = torch.zeros(t.shape[0], VOCAB_SIZE).to(computing_device)
    inputs_onehot.scatter_(1, t.unsqueeze(1).long(), 1.0)  # Remember inputs is indexes, so must be integer
    return inputs_onehot


def load_data(file):
    songs = read_songs_from('data/' + file)
    songs_encoded = encode_songs(songs, char_to_idx)
    return songs, songs_encoded


# Load Data
char_to_idx, idx_to_char = char_mapping()

train, train_encoded = load_data('train.txt')
val, val_encoded = load_data('val.txt')

# Initialize model
VOCAB_SIZE = len(char_to_idx.keys())
EPOCHS = 10
CHUNK_SIZE = 100

model = LSTMSimple(VOCAB_SIZE, 100, VOCAB_SIZE)

criterion = CrossEntropyLoss()
optimizer = optim.Adam(model.parameters())

training_losses = []
validation_losses = []
for epoch in range(1, EPOCHS + 1):
    print("Epoch", epoch)
    train_epoch_loss = []
    model.train()
    for i, song in enumerate(train_encoded):
        optimizer.zero_grad()
        p = 0
        n = math.ceil(len(song) / CHUNK_SIZE)
        loss = 0

        # Reset H for each song
        model.init_h(computing_device)

        # Divide songs into chunks
        for mini in range(n):
            if p + CHUNK_SIZE + 1 > len(song):
                inputs = song[p:-1]
                targets = song[p + 1:]
            else:
                inputs = song[p:p + CHUNK_SIZE]
                targets = song[p + 1: p + CHUNK_SIZE + 1]
            p += CHUNK_SIZE

            # Skip if empty
            if inputs.size()[0] == 0:
                continue

            # One-hot chunk tensor
            inputs_onehot = to_onehot(inputs)

            # Forward through model
            output = model(inputs_onehot.unsqueeze(1))  # Turn input into 3D (chunk_length, batch, vocab_size)

            # Calculate
            output.squeeze_(1)  # Back to 2D

            loss += criterion(output, targets.long())

        avg_train_song_loss = loss.item() / n
        train_epoch_loss.append(avg_train_song_loss)  # Average loss over one song
        loss.backward()
        optimizer.step()

        if i % 100 == 0:
            print("Song: {}, AvgTrainLoss: {}".format(i, sum(train_epoch_loss) / len(train_epoch_loss)))

    avg_train_songs_loss = sum(train_epoch_loss) / len(train_epoch_loss)  # Average loss overall songs
    training_losses.append(avg_train_songs_loss)

    with torch.no_grad():
        print("Validating...")
        model.eval()
        validation_song_losses = []
        for i, song in enumerate(val_encoded):
            optimizer.zero_grad()
            p = 0
            n = math.ceil(len(song) / CHUNK_SIZE)
            loss = 0

            for mini in range(n):
                if p + CHUNK_SIZE + 1 > len(song):
                    inputs = song[p:-1]
                    targets = song[p + 1:]
                else:
                    inputs = song[p:p + CHUNK_SIZE]
                    targets = song[p + 1: p + CHUNK_SIZE + 1]
                p += CHUNK_SIZE

                # Skip if empty
                if inputs.size()[0] == 0:
                    continue

                # One-hot chunk tensor
                inputs_onehot = to_onehot(inputs)

                # Forward through model
                output = model(inputs_onehot.unsqueeze(1))  # Turn input into 3D (chunk_length, batch, vocab_size)

                # Calculate
                output.squeeze_(1)  # Back to 2D

                loss += criterion(output, targets.long())

            avg_val_song_loss = loss.item() / n
            validation_song_losses.append(avg_val_song_loss)
        avg_val_songs_loss = sum(validation_song_losses) / len(validation_song_losses)
        validation_losses.append(avg_val_songs_loss)

        print("Epoch {}, Training loss: {}, Validation Loss: {}".format(epoch, avg_train_songs_loss, avg_val_songs_loss))
