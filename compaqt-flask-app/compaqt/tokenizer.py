"""
Token counting module using tiktoken with fallback to whitespace tokenizer.
"""

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False


def count_tokens(text: str) -> int:
    """
    Count the number of tokens in the given text.
    Uses tiktoken if available, otherwise falls back to whitespace tokenizer.
    
    Args:
        text: The text to count tokens for.
        
    Returns:
        The number of tokens in the text.
    """
    if TIKTOKEN_AVAILABLE:
        try:
            encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(text))
        except Exception:
            pass
    
    # Fallback: simple whitespace tokenizer
    # Approximates tokens by splitting on whitespace and punctuation
    tokens = 0
    for word in text.split():
        # Roughly estimate: 1 word = 1-2 tokens on average
        tokens += max(1, len(word) // 4 + 1)
    return tokens


def get_tokenizer_info() -> dict:
    """Return information about the current tokenizer being used."""
    return {
        'tiktoken_available': TIKTOKEN_AVAILABLE,
        'tokenizer': 'tiktoken (cl100k_base)' if TIKTOKEN_AVAILABLE else 'whitespace (fallback)'
    }
