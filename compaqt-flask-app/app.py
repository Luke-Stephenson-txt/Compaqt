from flask import Flask, render_template, request, jsonify, Response, abort
import os
from compaqt.tokenizer import Tokenizer
from compaqt.minify import minify_c
from compaqt.examples_data import get_all_examples, get_example_by_id
import json

app = Flask(__name__)

tokenizer = Tokenizer()

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
    examples_data = get_all_examples()
    return render_template('examples.html', examples=examples_data)


@app.route('/example/<example_id>')
def example_detail(example_id):
    """Detailed view of a specific example."""
    example = get_example_by_id(example_id)
    if example is None:
        abort(404)
    return render_template('example_detail.html', example=example)


@app.route('/tokenization')
def tokenization():
    """Tokenization visualization page."""
    return render_template('tokenization.html', tokenizer_name=tokenizer.name())


@app.route('/developers')
def developers():
    """Meet the Developers page."""
    developers_data = [
        {
            'name': 'Luke Stephenson',
            'role': 'Developer',
            'bio': 'Freshman at Case Western Reserve University studying Electrical Engineering and Computer Engineering.',
            'github': 'https://github.com/Luke-Stephenson-txt',
            'linkedin': 'https://www.linkedin.com/in/luke-e-stephenson/',
            'image': 'luke-stephenson.png'
        },
        {
            'name': 'Ian Dvorin',
            'role': 'Developer',
            'bio': 'Freshman at Case Western Reserve University studying Electrical Engineering and Computer Science.',
            'github': 'https://github.com/magicalbat',
            'linkedin': 'https://www.linkedin.com/in/ian-dvorin-7b4a84395/',
            'youtube': 'https://www.youtube.com/@Magicalbat',
            'image': 'ian-dvorin.jpg'
        }
    ]
    return render_template('developers.html', developers=developers_data)


# API Routes

@app.route('/pack', methods=['POST'])
def pack():
    """Pack files into token budget."""
    data = request.get_json()
    token_budget = int(data.get('token_budget', 4000))
    
    #files = load_sample_files()
    #result = pack_files(files, token_budget)
    
    #return jsonify(result)
    return ""


@app.route('/token_starts', methods=['POST'])
def token_starts():
    """Tokenize code input and return tokens."""
    data = request.get_json()
    code = data.get('code', '')
    
    return jsonify({
        'token_starts': tokenizer.token_starts(code)
    })


@app.route('/compress', methods=['POST'])
def compress():
    """Compress/minimize code and return token comparison."""
    data = request.get_json()
    code = data.get('code', '')

    # Get original tokens
    original_tokens = tokenizer.num_tokens(code)
    original_token_starts = tokenizer.token_starts(code)

    # Minimize code using minify_c
    minimized_code = minify_c(code)
    compressed_tokens = tokenizer.num_tokens(minimized_code)
    compressed_token_starts = tokenizer.token_starts(minimized_code)

    return jsonify({
        'original_code': code,
        'minimized_code': minimized_code,
        'original_tokens': original_tokens,
        'compressed_tokens': compressed_tokens,
        'original_token_starts': original_token_starts,
        'compressed_token_starts': compressed_token_starts,
        'savings': original_tokens - compressed_tokens,
        'savings_percentage': round((1 - compressed_tokens / original_tokens) * 100, 1) if original_tokens > 0 else 0
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
