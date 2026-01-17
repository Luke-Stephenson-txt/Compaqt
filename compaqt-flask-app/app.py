from flask import Flask, render_template, request, jsonify, Response
import os
from compaqt.packer import pack_files, minimize_code
from compaqt.tokenizer import count_tokens, get_tokenizer_info
import json

app = Flask(__name__)

SAMPLE_REPO_PATH = os.path.join(os.path.dirname(__file__), 'compaqt', 'sample_repo')


def load_sample_files():
    """Load all Python files from the sample repository."""
    files = []
    for filename in sorted(os.listdir(SAMPLE_REPO_PATH)):
        if filename.endswith('.py'):
            filepath = os.path.join(SAMPLE_REPO_PATH, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            files.append({
                'name': filename,
                'content': content,
                'tokens': count_tokens(content)
            })
    return files


@app.route('/')
def index():
    """Home page with overview."""
    return render_template('index.html')


@app.route('/about')
def about():
    """About/Explanation page."""
    return render_template('about.html')


@app.route('/examples')
def examples():
    """Examples page with demos."""
    # Example data - could be loaded from a file or database
    examples_data = [
        {
            'name': 'Web Application Stack',
            'description': 'Full-stack web application with frontend and backend code',
            'before_tokens': 15230,
            'after_tokens': 8734,
            'files': 12
        },
        {
            'name': 'Data Processing Pipeline',
            'description': 'Python data processing scripts with data cleaning and analysis',
            'before_tokens': 9876,
            'after_tokens': 5234,
            'files': 8
        },
        {
            'name': 'API Microservices',
            'description': 'RESTful API services with authentication and database connections',
            'before_tokens': 12456,
            'after_tokens': 7654,
            'files': 15
        },
        {
            'name': 'Machine Learning Models',
            'description': 'ML model training and inference code with preprocessing',
            'before_tokens': 18345,
            'after_tokens': 10234,
            'files': 10
        }
    ]
    return render_template('examples.html', examples=examples_data)


@app.route('/tokenization')
def tokenization():
    """Tokenization visualization page."""
    tokenizer_info = get_tokenizer_info()
    return render_template('tokenization.html', tokenizer_info=tokenizer_info)


@app.route('/developers')
def developers():
    """Meet the Developers page."""
    developers_data = [
        {
            'name': 'Your Name',
            'role': 'Lead Developer',
            'bio': 'Passionate about building efficient AI tools and optimizing developer workflows. Focused on making LLM integrations more cost-effective and performant.',
            'github': 'https://github.com/yourusername',
            'linkedin': 'https://linkedin.com/in/yourprofile',
            'avatar': '👨‍💻'
        },
        {
            'name': 'Co-Developer',
            'role': 'Full Stack Developer',
            'bio': 'Specializes in backend systems and prompt engineering. Enthusiastic about creating developer tools that reduce complexity and improve productivity.',
            'github': 'https://github.com/codeveloper',
            'linkedin': 'https://linkedin.com/in/codeveloper',
            'avatar': '👩‍💻'
        }
    ]
    return render_template('developers.html', developers=developers_data)


# API Routes

@app.route('/pack', methods=['POST'])
def pack():
    """Pack files into token budget."""
    data = request.get_json()
    token_budget = int(data.get('token_budget', 4000))
    
    files = load_sample_files()
    result = pack_files(files, token_budget)
    
    return jsonify(result)


@app.route('/tokenize', methods=['POST'])
def tokenize():
    """Tokenize code input and return tokens."""
    data = request.get_json()
    code = data.get('code', '')
    
    # Count tokens
    token_count = count_tokens(code)
    
    # Get individual tokens using tiktoken if available
    try:
        import tiktoken
        encoding = tiktoken.get_encoding("cl100k_base")
        tokens = encoding.encode(code)
        token_list = [encoding.decode_single_token_bytes(token).decode('utf-8', errors='ignore') for token in tokens]
    except:
        # Fallback: simple tokenization
        token_list = code.split()
    
    return jsonify({
        'token_count': token_count,
        'tokens': token_list[:500]  # Limit to first 500 tokens for display
    })


@app.route('/compress', methods=['POST'])
def compress():
    """Compress/minimize code and return token comparison."""
    data = request.get_json()
    code = data.get('code', '')
    
    # Get original tokens
    original_tokens = count_tokens(code)
    
    # Minimize code
    minimized_code = minimize_code(code)
    compressed_tokens = count_tokens(minimized_code)
    
    # Get token lists
    try:
        import tiktoken
        encoding = tiktoken.get_encoding("cl100k_base")
        
        orig_tokens = encoding.encode(code)
        orig_token_list = [encoding.decode_single_token_bytes(t).decode('utf-8', errors='ignore') for t in orig_tokens[:500]]
        
        comp_tokens = encoding.encode(minimized_code)
        comp_token_list = [encoding.decode_single_token_bytes(t).decode('utf-8', errors='ignore') for t in comp_tokens[:500]]
    except:
        orig_token_list = code.split()[:500]
        comp_token_list = minimized_code.split()[:500]
    
    return jsonify({
        'original_code': code,
        'minimized_code': minimized_code,
        'original_tokens': original_tokens,
        'compressed_tokens': compressed_tokens,
        'savings': original_tokens - compressed_tokens,
        'savings_percentage': round((1 - compressed_tokens / original_tokens) * 100, 1) if original_tokens > 0 else 0,
        'original_token_list': orig_token_list,
        'compressed_token_list': comp_token_list
    })


@app.route('/download', methods=['POST'])
def download():
    """Download packed text."""
    data = request.get_json()
    packed_text = data.get('packed_text', '')
    
    return Response(
        packed_text,
        mimetype='text/plain',
        headers={'Content-Disposition': 'attachment;filename=packed_prompt.txt'}
    )


@app.route('/download-tokens', methods=['POST'])
def download_tokens():
    """Download tokens as JSON."""
    data = request.get_json()
    tokens_data = data.get('tokens_data', {})
    
    return Response(
        json.dumps(tokens_data, indent=2),
        mimetype='application/json',
        headers={'Content-Disposition': 'attachment;filename=tokens.json'}
    )


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
