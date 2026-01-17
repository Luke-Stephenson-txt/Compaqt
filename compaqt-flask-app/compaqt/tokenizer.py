import tiktoken

class Tokenizer():
    def __init__(self, encoding_name=None):
        if encoding_name is None:
            encoding_name = "o200k_base"

        self.encoding = tiktoken.get_encoding(encoding_name)

    def name(self):
        return self.encoding.name
    
    def encode(self, text):
        return self.encoding.encode(text)

    def decode(self, tokens):
        return self.encoding.decode(tokens)

    def num_tokens(self, text):
        return len(self.encoding.encode(text))

    # Returns a list of integers, each corresponding to the 
    # index where a new token starts
    def token_starts(self, text):
        tokens = self.encoding.encode(text)
        starts = [0] * len(tokens)

        for i in range(1, len(tokens)): 
            cur_bytes = self.encoding.decode_single_token_bytes(tokens[i-1])
            starts[i] = starts[i-1] + len(cur_bytes)

        return starts
