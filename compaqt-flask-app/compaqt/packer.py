"""
Prompt packing module for minimizing and packing code files into a token budget.
"""

from typing import List, Dict, Any
from .tokenizer import count_tokens


def minimize_code(content: str) -> str:
    """
    Minimize Python code by removing comments, docstrings, and blank lines.
    
    Args:
        content: The source code to minimize.
        
    Returns:
        Minimized code with functionality preserved.
    """
    lines = content.split('\n')
    result_lines = []
    in_docstring = False
    docstring_char = None
    
    for line in lines:
        stripped = line.strip()
        
        # Skip empty lines
        if not stripped:
            continue
        
        # Handle docstrings
        if not in_docstring:
            # Check for docstring start
            if stripped.startswith('"""') or stripped.startswith("'''"):
                docstring_char = stripped[:3]
                # Check if docstring ends on same line
                if stripped.count(docstring_char) >= 2 and len(stripped) > 3:
                    continue  # Single-line docstring, skip it
                in_docstring = True
                continue
        else:
            # Check for docstring end
            if docstring_char in stripped:
                in_docstring = False
                docstring_char = None
            continue
        
        # Skip comment-only lines
        if stripped.startswith('#'):
            continue
        
        # Remove inline comments (but preserve strings)
        # Simple approach: remove # and everything after if not in a string
        processed_line = remove_inline_comments(line)
        
        # Normalize whitespace (preserve indentation)
        indent = len(line) - len(line.lstrip())
        processed_stripped = processed_line.strip()
        if processed_stripped:
            result_lines.append(' ' * indent + processed_stripped)
    
    return '\n'.join(result_lines)


def remove_inline_comments(line: str) -> str:
    """
    Remove inline comments from a line while preserving strings.
    """
    result = []
    in_string = False
    string_char = None
    i = 0
    
    while i < len(line):
        char = line[i]
        
        if not in_string:
            if char in ('"', "'"):
                in_string = True
                string_char = char
                result.append(char)
            elif char == '#':
                # Found comment, stop here
                break
            else:
                result.append(char)
        else:
            result.append(char)
            if char == string_char and (i == 0 or line[i-1] != '\\'):
                in_string = False
                string_char = None
        
        i += 1
    
    return ''.join(result)


def pack_files(files: List[Dict[str, Any]], token_budget: int) -> Dict[str, Any]:
    """
    Pack files into a token budget using greedy approach.
    
    Args:
        files: List of file dictionaries with 'name', 'content', and 'tokens' keys.
        token_budget: Maximum number of tokens for the packed output.
        
    Returns:
        Dictionary containing packed text, included/excluded files, and stats.
    """
    # Minimize all files and calculate new token counts
    minimized_files = []
    for f in files:
        minimized_content = minimize_code(f['content'])
        minimized_tokens = count_tokens(minimized_content)
        minimized_files.append({
            'name': f['name'],
            'original_content': f['content'],
            'minimized_content': minimized_content,
            'original_tokens': f['tokens'],
            'minimized_tokens': minimized_tokens,
            'savings': f['tokens'] - minimized_tokens
        })
    
    # Sort by minimized token count (largest first for greedy packing)
    minimized_files.sort(key=lambda x: x['minimized_tokens'], reverse=True)
    
    # Greedy packing
    packed_sections = []
    included_files = []
    excluded_files = []
    current_tokens = 0
    
    # Reserve some tokens for headers
    header_overhead_per_file = 20  # Approximate tokens for metadata header
    
    for f in minimized_files:
        file_total = f['minimized_tokens'] + header_overhead_per_file
        
        if current_tokens + file_total <= token_budget:
            # Create file section with metadata header
            header = f"# === {f['name']} ({f['minimized_tokens']} tokens) ==="
            section = f"{header}\n{f['minimized_content']}\n"
            packed_sections.append(section)
            included_files.append({
                'name': f['name'],
                'original_tokens': f['original_tokens'],
                'packed_tokens': f['minimized_tokens'],
                'savings': f['savings']
            })
            current_tokens += file_total
        else:
            excluded_files.append({
                'name': f['name'],
                'tokens': f['minimized_tokens'],
                'reason': 'Exceeded token budget'
            })
    
    packed_text = '\n'.join(packed_sections)
    final_tokens = count_tokens(packed_text)
    
    # Calculate statistics
    original_total = sum(f['original_tokens'] for f in minimized_files)
    included_original = sum(f['original_tokens'] for f in included_files)
    
    return {
        'packed_text': packed_text,
        'included_files': included_files,
        'excluded_files': excluded_files,
        'stats': {
            'original_total_tokens': original_total,
            'packed_tokens': final_tokens,
            'token_budget': token_budget,
            'tokens_saved': included_original - final_tokens,
            'savings_percentage': round((1 - final_tokens / included_original) * 100, 1) if included_original > 0 else 0,
            'files_included': len(included_files),
            'files_excluded': len(excluded_files)
        }
    }
