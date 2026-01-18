import re
import numpy as np
from sentence_transformers import SentenceTransformer

class MinifySemantic():
    def __init__(self, model_name=None):
        if model_name is None:
            model_name = "all-MiniLM-L6-v2"
        
        self.model = SentenceTransformer(model_name)

    def most_redundant_word(self, sentence, batch_size=32, min_words=5):
        spans = word_spans(sentence)

        if len(spans) < min_words:
            return sentence, None

        original_emb = self.model.encode(
            sentence,
            normalize_embeddings=True,
            convert_to_numpy=True
        )

        variants = []
        meta = []

        for word, start, end in spans:
            modified = remove_word_at_span(sentence, (start, end))
            if modified.strip():
                variants.append(modified)
                meta.append((word, start, end))

        # Batch encode all variants at once
        variant_embs = self.model.encode(
            variants,
            batch_size=batch_size,
            normalize_embeddings=True,
            convert_to_numpy=True
        )

        sims = variant_embs @ original_emb  # cosine similarity

        idx = int(np.argmax(sims))
        best_word, start, end = meta[idx]

        reduced = remove_word_at_span(sentence, (start, end))
        return reduced, best_word

    def compress_prompt(self, prompt, min_words=5, ratio=0.7):
        parts = split_sentences_with_delimiters(prompt)
        compressed_prompt = ""

        for sentence, delimiter in parts:
            reduced_sentence, removed_word = sentence, " "
            while len(reduced_sentence) / len(sentence) > ratio and removed_word is not None:
                reduced_sentence, removed_word = self.most_redundant_word(reduced_sentence, min_words)

            compressed_prompt += reduced_sentence + delimiter

        return compressed_prompt

def split_sentences_with_delimiters(text):
    """
    Splits text into (sentence, delimiter) pairs.
    Delimiters include punctuation + whitespace or newlines.
    """
    text = text.replace("\r\n", "\n")

    pattern = re.compile(r'(.*?)([.!?]\s+|\n+|$)', re.DOTALL)
    parts = []

    for match in pattern.finditer(text):
        sentence = match.group(1)
        delimiter = match.group(2)
        if sentence:
            parts.append((sentence, delimiter))

    return parts

# Returns list of (word, start, end) preserving original string.
def word_spans(sentence):
    word_re = re.compile(r"\b\w+\b")
    return [(m.group(), m.start(), m.end()) for m in word_re.finditer(sentence)]

def remove_word_at_span(sentence, span):
    """
    Remove a word by character span, cleaning up adjacent whitespace
    without disturbing punctuation.
    """
    start, end = span
    s = sentence

    # Remove trailing space if present
    if end < len(s) and s[end].isspace():
        end += 1
    # Otherwise remove leading space if present
    elif start > 0 and s[start - 1].isspace():
        start -= 1

    return s[:start] + s[end:]
