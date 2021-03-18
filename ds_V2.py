import re
import pandas as pd

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)

####################################
#            read csv              #
####################################

df = pd.read_csv('train.csv', index_col=0)

df[['POI', 'street']] = pd.DataFrame(df['POI/street'].str.split(pat="/").tolist(), index=df.index)

df['POI'] = df['POI'].str.replace('.','').replace('.','')

df['street'] = df['street'].str.replace('.','').replace(',','')

df['raw_address#POI'] = df['raw_address'] + '#' + df['POI']
lines = df['raw_address#POI'].tolist()


input_texts = []
target_texts = []
input_characters = set()
target_characters = set()

num_samples = 10000

for line in lines[: 100]:
  input_text, target_text = line.split('#')
  target_text = '\t' + target_text + '\n'
  input_texts.append(input_text)
  target_texts.append(target_text)
  for char in input_text:
    if char not in input_characters:
      input_characters.add(char)
  for char in target_text:
    if char not in target_characters:
      target_characters.add(char)

input_characters = sorted(list(input_characters))
target_characters = sorted(list(target_characters))
num_encoder_tokens = len(input_characters)
num_decoder_tokens = len(target_characters)
max_encoder_seq_length = max([len(txt) for txt in input_texts])
max_decoder_seq_length = max([len(txt) for txt in target_texts])

print('Number of samples:', len(input_texts))
print('Number of unique input tokens:', num_encoder_tokens)
print('Number of unique output tokens:', num_decoder_tokens)
print('Max sequence length for inputs:', max_encoder_seq_length)
print('Max sequence length for outputs:', max_decoder_seq_length)


input_token_index = dict([(char, i) for i, char in enumerate(input_characters)])
target_token_index = dict([(char, i) for i, char in enumerate(target_characters)])

import numpy as np

encoder_input_data = np.zeros((len(input_texts), max_encoder_seq_length, num_encoder_tokens),dtype='float32')
decoder_input_data = np.zeros((len(input_texts), max_decoder_seq_length, num_decoder_tokens),dtype='float32')
decoder_target_data = np.zeros((len(input_texts), max_decoder_seq_length, num_decoder_tokens),dtype='float32')


for i, (input_text, target_text) in enumerate(zip(input_texts, target_texts)):
  for t, char in enumerate(input_text):
    encoder_input_data[i, t, input_token_index[char]] = 1.
  for t, char in enumerate(target_text):
    # decoder_target_data is ahead of decoder_input_data by one timestep
    decoder_input_data[i, t, target_token_index[char]] = 1.
    if t > 0:
      # decoder_target_data will be ahead by one timestep
      # and will not include the start character.
      decoder_target_data[i, t - 1, target_token_index[char]] = 1.

import keras, ds_V2
from keras.models import Model
from keras.layers import Input, LSTM, Dense
import numpy as np

batch_size = 64  # batch size for training
epochs = 100  # number of epochs to train for
latent_dim = 256  # latent dimensionality of the encoding space


encoder_inputs = Input(shape=(None, num_encoder_tokens))
encoder = LSTM(latent_dim, return_state=True)
encoder_outputs, state_h, state_c = encoder(encoder_inputs)
encoder_states = [state_h, state_c]



decoder_inputs = Input(shape=(None, num_decoder_tokens))
decoder_lstm = LSTM(latent_dim, return_sequences=True, return_state=True)
decoder_outputs, _, _ = decoder_lstm(decoder_inputs,initial_state=encoder_states)
decoder_dense = Dense(num_decoder_tokens, activation='softmax')
decoder_outputs = decoder_dense(decoder_outputs)



model = Model(inputs=[encoder_inputs, decoder_inputs],outputs=decoder_outputs)

model = Model([encoder_inputs, decoder_inputs], decoder_outputs)
model.compile(optimizer='rmsprop', loss='categorical_crossentropy')


encoder_model = Model(encoder_inputs, encoder_states)

decoder_state_input_h = Input(shape=(latent_dim,))
decoder_state_input_c = Input(shape=(latent_dim,))
decoder_states_inputs = [decoder_state_input_h, decoder_state_input_c]

decoder_outputs, state_h, state_c = decoder_lstm(decoder_inputs, initial_state=decoder_states_inputs)
decoder_states = [state_h, state_c]
decoder_outputs = decoder_dense(decoder_outputs)

decoder_model = Model([decoder_inputs] + decoder_states_inputs,[decoder_outputs] + decoder_states)


# reverse-lookup token index to turn sequences back to characters
reverse_input_char_index = dict((i, char) for char, i in input_token_index.items())
reverse_target_char_index = dict((i, char) for char, i in target_token_index.items())


def decode_sequence(input_seq):
  # encode the input sequence to get the internal state vectors.
  states_value = encoder_model.predict(input_seq)

  # generate empty target sequence of length 1 with only the start character
  target_seq = np.zeros((1, 1, num_decoder_tokens))
  target_seq[0, 0, target_token_index['\t']] = 1.

  # output sequence loop
  stop_condition = False
  decoded_sentence = ''
  while not stop_condition:
    output_tokens, h, c = decoder_model.predict(
      [target_seq] + states_value)

    # sample a token and add the corresponding character to the
    # decoded sequence
    sampled_token_index = np.argmax(output_tokens[0, -1, :])
    sampled_char = reverse_target_char_index[sampled_token_index]
    decoded_sentence += sampled_char

    # check for the exit condition: either hitting max length
    # or predicting the 'stop' character
    if (sampled_char == '\n' or
            len(decoded_sentence) > max_decoder_seq_length):
      stop_condition = True

    # update the target sequence (length 1).
    target_seq = np.zeros((1, 1, num_decoder_tokens))
    target_seq[0, 0, sampled_token_index] = 1.

    # update states
    states_value = [h, c]

  return decoded_sentence


for seq_index in range(10):
  input_seq = encoder_input_data[seq_index: seq_index + 1]
  decoded_sentence = decode_sequence(input_seq)
  print('-')
  print('Input sentence:', input_texts[seq_index])
  print('Decoded sentence:', decoded_sentence)



input_sentence = f"{str(df['raw_address'][0])}"
test_sentence_tokenized = np.zeros((1, max_encoder_seq_length, num_encoder_tokens), dtype='float32')
for t, char in enumerate(input_sentence):
  test_sentence_tokenized[0, t, input_token_index[char]] = 1.
print(input_sentence)
print(decode_sequence(test_sentence_tokenized))


val_input_texts = []
val_target_texts = []
line_ix = 12000
for line in lines[line_ix:line_ix+10]:
  input_text, target_text = line.split('#')
  val_input_texts.append(input_text)
  val_target_texts.append(target_text)

val_encoder_input_data = np.zeros((len(val_input_texts), max([len(txt) for txt in val_input_texts]),num_encoder_tokens), dtype='float32')

for i, input_text in enumerate(val_input_texts):
  for t, char in enumerate(input_text):
    val_encoder_input_data[i, t, input_token_index[char]] = 1.


for seq_index in range(10):
  input_seq = val_encoder_input_data[seq_index: seq_index + 1]
  decoded_sentence = decode_sequence(input_seq)
  print('-')
  print('Input sentence:', val_input_texts[seq_index])
  print('Decoded sentence:', decoded_sentence[:-1])
  print('Ground Truth sentence:', val_target_texts[seq_index])