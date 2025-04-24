import numpy as np
import category_encoders as ce
class CustomEncoder():
    def __init__(self, N) -> None:
        self.N = N
        self.ohe_encoder = ce.OneHotEncoder()
        self.unique_tokens = []
        self.unique_tokens_out_var = []
        self.vocab_out_var = {}
        self.ohe_res = []
        self.pos_enc_values = []
        self.vocab = {}
        self.vec_size = None

    def build_prevocab_keys(self, input_strings_tokens):
        for file in input_strings_tokens:
            for token in file:
                if token not in self.unique_tokens:
                    self.unique_tokens.append(token)

    def build_ohe_vocab_keys(self):
        self.unique_tokens_out_var = [token for token in self.unique_tokens if not (token[0] == "v" and "var" in token)] + ["var"]

    def build_vocab_out_var(self):
        for idx in range(len(self.ohe_res)):
            self.vocab_out_var[self.unique_tokens_out_var[idx]] = self.ohe_res[idx]

    def build_pos_enc_dimensions(self):
        self.pos_enc_values = []
        for token in self.unique_tokens:
            if token[0] == "v" and "var" in token:
                i = int(token[3:])
                self.pos_enc_values.append([np.cos(2*(i-1)/self.N), np.sin(2*(i-1)/self.N)])
            else:
                self.pos_enc_values.append([0, 0])
        self.pos_enc_values = np.array(self.pos_enc_values)
    
    def build_vocab_w_pos_enc(self):
        for idx, token in enumerate(self.unique_tokens):
            if token[0] == "v" and "var" in token:
                key = "var"
            else:
                key = token
            self.vocab[token] = np.concatenate((self.vocab_out_var[key], self.pos_enc_values[idx]))

    def fit(self, input_strings_tokens):
        self.build_prevocab_keys(input_strings_tokens)
        self.build_ohe_vocab_keys()
        self.ohe_res = self.ohe_encoder.fit_transform(self.unique_tokens_out_var).values
        self.build_vocab_out_var()
        self.build_pos_enc_dimensions()
        self.build_vocab_w_pos_enc()
        self.vec_size = len(list(self.vocab.values())[0])

    def transform(self, input_tokenized_string):
        return np.array([self.vocab[token] for token in input_tokenized_string if token in self.vocab])