# music-generation-rnn
Songs generator using LSTM and Vanila Recurrent Neural Networks with PyTorch.

Using a dataset of songs, this report will present one possible solution to build a predictor using different RNN architectures.

This project includes:
* Songs dataset encoding.
* LSTM and Vanilla models implemented with PyTorch.
* Dropouts Layer and Hyper-Parameters configurations.
* Song Generation Class to use the trained model to create new, dataset silimar, songs.
* Hidden neurons visualized weights.

## Setup
Install the dependencies in the requirements.txt file.

## Overview
**train.py**:
Main class, this is where the training, testing and graph generation is happening.

**models.py**:
All of our Pytorch models is located here, including the fit function, evaluation function calculating negative 
log likelihood.

**utils.py**:
Helper methods 

**generator.py**
Includes function for generating a song.

**generate_song.py**
Script for generating song with settings

**generate_heatmaps.py**
Script for generating the heatmap presented in the last task of the report.


## Configuration
Our default settings is listed below
```
config = {
    "EPOCHS": 15,
    "CHUNK_SIZE": 100,
    "VOCAB_SIZE": len(char_to_idx.keys()),
    "LR": 0.001,  # Default in Adam 0.001,
    "WEIGHT_DECAY": 0,  # Default in Adam 0
    "HIDDEN": 100,

    # For songs sampling
    "TEMPERATURE": 1,
    "TAKE_MAX_PROBABLE": False,
    "LIMIT_LEN": 300
}
```
