from flask import Flask, render_template, request, jsonify, Response, abort
import os
from compaqt.tokenizer import Tokenizer
from compaqt.minify_c import minify_c
from compaqt.minify_semantic import MinifySemantic
from compaqt.examples_data import get_all_examples, get_example_by_id
from compaqt.elite_plus import get_elite_plus_encoder
import json

app = Flask(__name__)

tokenizer = Tokenizer()
semantic_minifier = MinifySemantic()
elite_plus_encoder = get_elite_plus_encoder()

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

@app.route('/compress_c', methods=['POST'])
def compress_c():
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
        'minimized_code': minimized_code,
        'original_tokens': original_tokens,
        'compressed_tokens': compressed_tokens,
        'original_token_starts': original_token_starts,
        'compressed_token_starts': compressed_token_starts,
        'savings': original_tokens - compressed_tokens,
        'savings_percentage': round((1 - compressed_tokens / original_tokens) * 100, 1) if original_tokens > 0 else 0
    })

@app.route('/compress_prompt', methods=['POST'])
def compress_prompt():
    data = request.get_json()
    prompt = data.get('prompt', '')
    ratio = data.get('ratio', 0.7)
    min_words = data.get('min_words', 5)

    # Get original tokens
    original_tokens = tokenizer.num_tokens(prompt)
    original_token_starts = tokenizer.token_starts(prompt)

    # Minimize prompt using semantic compression
    minimized_prompt = semantic_minifier.compress_prompt(prompt, min_words=min_words, ratio=ratio)
    compressed_tokens = tokenizer.num_tokens(minimized_prompt)
    compressed_token_starts = tokenizer.token_starts(minimized_prompt)

    return jsonify({
        'minimized_prompt': minimized_prompt,
        'original_tokens': original_tokens,
        'compressed_tokens': compressed_tokens,
        'original_token_starts': original_token_starts,
        'compressed_token_starts': compressed_token_starts,
        'savings': original_tokens - compressed_tokens,
        'savings_percentage': round((1 - compressed_tokens / original_tokens) * 100, 1) if original_tokens > 0 else 0
    })

@app.route('/compress_combined', methods=['POST'])
def compress_combined():
    """Compress both C code and prompt, return combined results."""
    data = request.get_json()
    code = data.get('code', '').strip()
    prompt = data.get('prompt', '').strip()
    ratio = data.get('ratio', 0.7)
    min_words = data.get('min_words', 5)
    elite_plus = data.get('elite_plus', False)

    # Process C code if provided
    code_original_tokens = 0
    code_compressed_tokens = 0
    minimized_code = ''
    code_original_token_starts = []
    code_compressed_token_starts = []
    
    if code:
        code_original_tokens = tokenizer.num_tokens(code)
        code_original_token_starts = tokenizer.token_starts(code)
        
        # Use Elite+ compression if enabled and available
        if elite_plus and elite_plus_encoder.is_available():
            elite_result = elite_plus_encoder.compress(code)
            if elite_result and elite_result.get('code'):
                minimized_code = elite_result['code']
            else:
                # Fallback to regular minification if Elite+ fails
                minimized_code = minify_c(code)
        else:
            minimized_code = minify_c(code)
        
        code_compressed_tokens = tokenizer.num_tokens(minimized_code)
        code_compressed_token_starts = tokenizer.token_starts(minimized_code)

    # Process prompt if provided
    prompt_original_tokens = 0
    prompt_compressed_tokens = 0
    minimized_prompt = ''
    prompt_original_token_starts = []
    prompt_compressed_token_starts = []
    
    if prompt:
        prompt_original_tokens = tokenizer.num_tokens(prompt)
        prompt_original_token_starts = tokenizer.token_starts(prompt)
        minimized_prompt = semantic_minifier.compress_prompt(prompt, min_words=min_words, ratio=ratio)
        prompt_compressed_tokens = tokenizer.num_tokens(minimized_prompt)
        prompt_compressed_token_starts = tokenizer.token_starts(minimized_prompt)

    # Combine for total tokenization
    combined_original = (code + '\n\n' if code else '') + (prompt if prompt else '')
    combined_compressed = (minimized_code + '\n\n' if minimized_code else '') + (minimized_prompt if minimized_prompt else '')
    
    # Tokenize combined strings directly for accurate token positions
    original_tokens = tokenizer.num_tokens(combined_original) if combined_original else 0
    compressed_tokens = tokenizer.num_tokens(combined_compressed) if combined_compressed else 0
    original_token_starts = tokenizer.token_starts(combined_original) if combined_original else []
    compressed_token_starts = tokenizer.token_starts(combined_compressed) if combined_compressed else []

    return jsonify({
        'minimized_code': minimized_code,
        'minimized_prompt': minimized_prompt,
        'original_tokens': original_tokens,
        'compressed_tokens': compressed_tokens,
        'original_token_starts': original_token_starts,
        'compressed_token_starts': compressed_token_starts,
        'code_original_tokens': code_original_tokens,
        'code_compressed_tokens': code_compressed_tokens,
        'code_original_token_starts': code_original_token_starts,
        'code_compressed_token_starts': code_compressed_token_starts,
        'prompt_original_tokens': prompt_original_tokens,
        'prompt_compressed_tokens': prompt_compressed_tokens,
        'prompt_original_token_starts': prompt_original_token_starts,
        'prompt_compressed_token_starts': prompt_compressed_token_starts,
        'savings': original_tokens - compressed_tokens,
        'savings_percentage': round((1 - compressed_tokens / original_tokens) * 100, 1) if original_tokens > 0 else 0,
        'elite_plus_used': elite_plus and elite_plus_encoder.is_available() and code != '',
        'elite_plus_available': elite_plus_encoder.is_available()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
