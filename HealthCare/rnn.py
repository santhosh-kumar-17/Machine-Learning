# RNN Example
from tensorflow.keras.layers import SimpleRNN, Embedding

# Define RNN model
rnn_model = Sequential([
    Embedding(input_dim=10000, output_dim=32),
    SimpleRNN(32),
    Dense(1, activation='sigmoid')
])

# Compile model
rnn_model.compile(optimizer='adam',
                  loss='binary_crossentropy',
                  metrics=['accuracy'])
