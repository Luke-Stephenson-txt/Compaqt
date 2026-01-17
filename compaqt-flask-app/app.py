from flask import Flask, render_template, request, jsonify, Response
import os
from compaqt.packer import pack_files
from compaqt.tokenizer import count_tokens

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
    files = load_sample_files()
    total_tokens = sum(f['tokens'] for f in files)
    return render_template('index.html', files=files, total_tokens=total_tokens)


@app.route('/pack', methods=['POST'])
def pack():
    data = request.get_json()
    token_budget = int(data.get('token_budget', 4000))
    
    files = load_sample_files()
    result = pack_files(files, token_budget)
    
    return jsonify(result)


@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    packed_text = data.get('packed_text', '')
    
    return Response(
        packed_text,
        mimetype='text/plain',
        headers={'Content-Disposition': 'attachment;filename=packed_prompt.txt'}
    )


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
