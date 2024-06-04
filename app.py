from flask import Flask, request, render_template_string
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads/'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def lexical_analysis(code):
    result = []
    keywords = {'int', 'for', 'if', 'else', 'while', 'return', 'system.out.println'}
    lines = code.split('\n')
    char_position = 0

    for line_number, line in enumerate(lines, start=1):
        index = 0
        while index < len(line):
            token_detected = False
            for keyword in keywords:
                if line[index:].startswith(keyword) and (index + len(keyword) == len(line) or not line[index + len(keyword)].isalnum()):
                    result.append((line_number, char_position + index, 'Palabra reservada', keyword))
                    index += len(keyword)
                    token_detected = True
                    break
            if token_detected:
                continue

            char = line[index]
            if char in [';', '{', '}', '(', ')']:
                tipo = 'Punto y coma' if char == ';' else 'Llave' if char in ['{', '}'] else 'Paréntesis'
                result.append((line_number, char_position + index, tipo, char))
                index += 1
            elif char.isdigit():
                number_start = index
                while index < len(line) and line[index].isdigit():
                    index += 1
                number = line[number_start:index]
                result.append((line_number, char_position + number_start, 'Número', number))
            elif char.isalpha() or char == '.':
                token_start = index
                while index < len(line) and (line[index].isalnum() or line[index] == '.'):
                    index += 1
                token = line[token_start:index]
                if token in keywords:
                    result.append((line_number, char_position + token_start, 'Palabra reservada', token))
                else:
                    result.append((line_number, char_position + token_start, 'Identificador', token))
            else:
                index += 1
        
        char_position += len(line) + 1  # Add 1 for the newline character

    return result

def syntactic_analysis(code):
    result = []
    correct_keyword = 'system.out.println'
    keywords = {'for', 'if', 'else', 'while', 'return'}
    lines = code.split('\n')
    for line_number, line in enumerate(lines, start=1):
        stripped_line = line.strip()
        if stripped_line.startswith('system.out.'):
            if stripped_line.startswith(correct_keyword):
                result.append((line_number, correct_keyword, True))
            else:
                result.append((line_number, stripped_line.split('(')[0], False))
        elif 'system' in stripped_line or '.out' in stripped_line:
            result.append((line_number, stripped_line.split('(')[0], False))
        else:
            tokens = stripped_line.split()
            for token in tokens:
                if token in keywords:
                    result.append((line_number, token.capitalize(), True))
                elif any(keyword in token for keyword in keywords):
                    result.append((line_number, token.capitalize(), False))
                    break
    return result

@app.route('/', methods=['GET', 'POST'])
def index():
    code = ""
    lexical_result = []
    syntactic_result = []
    if request.method == 'POST':
        if 'file' in request.files and request.files['file'].filename != '':
            file = request.files['file']
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            with open(file_path, 'r') as f:
                code = f.read()
        elif 'code' in request.form and request.form['code'].strip() != '':
            code = request.form['code']
        else:
            return "No file selected or code provided"
        
        lexical_result = lexical_analysis(code)
        syntactic_result = syntactic_analysis(code)
        
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f5f5f5; /* Color de fondo más claro */
                color: #333;
                margin: 0;
                padding: 20px;
            }
            h1 {
                text-align: center;
                color: #333;
            }
            form {
                background-color: #fff;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                margin-bottom: 20px;
            }
            .container {
                max-width: 800px;
                margin: auto;
                background-color: #fff;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }
            .section-title {
                background-color: #e5e5e5;
                padding: 10px;
                border-radius: 4px;
                margin-bottom: 10px;
                text-align: center;
            }
            .lexical-result, .syntactic-result {
                background-color: #fff;
                padding: 10px;
                border-radius: 4px;
                overflow-y: auto;
                max-height: 200px;
                margin-top: 20px;
                border: 1px solid #ddd;
            }
            .lexical-result pre, .syntactic-result pre {
                white-space: pre-wrap;
                word-wrap: break-word;
                color: #333;
            }
            .error {
                color: red;
                font-weight: bold;
            }
            textarea {
                width: 100%;
                height: 200px;
                padding: 10px;
                border-radius: 4px;
                border: 1px solid #ddd;
                box-shadow: inset 0 1px 3px rgba(0,0,0,.12);
                background-color: #f5f5f5;
                color: #333;
                transition: border-color .15s ease-in-out, box-shadow .15s ease-in-out;
            }
            textarea:focus {
                border-color: #4CAF50;
                box-shadow: 0 0 5px rgba(76, 175, 80, .5);
            }
            input[type="submit"] {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                margin: 4px 2px;
                transition-duration: 0.4s;
                cursor: pointer;
                border-radius: 4px;
            }
            input[type="submit"]:hover {
                background-color: white;
                color: #4CAF50;
                border: 2px solid #4CAF50;
            }
        </style>
        <title>Analizador Léxico y Sintáctico</title>
    </head>
    <body>
        <div class="container">
            <h1>Analizador Léxico y Sintáctico</h1>
            <form method="POST" enctype="multipart/form-data">
                <label for="file">Subir Archivo</label>
                <input type="file" name="file">
                <input type="button" value="X" onclick="document.querySelector('input[type=file]').value = '';"><br><br>
                <label for="code">Texto</label><br>
                <textarea name="code">{{ code }}</textarea><br><br>
                <input type="submit" value="Ejecutar">
            </form>

            {% if lexical_result %}
            <div class="section-title">Análisis Léxico</div>
            <div class="lexical-result">
                <pre>
                {% for line in lexical_result %}
Línea: {{ line[0] }}    Tipo: {{ line[2].upper() }}    Valor: {{ line[3] }}
Posición: {{ line[1] }}
                {% endfor %}
                </pre>
            </div>
            {% endif %}

            {% if syntactic_result %}
            <div class="section-title">Análisis Sintáctico</div>
            <div class="syntactic-result">
                <pre>
                {% for line in syntactic_result %}
Línea: {{ line[0] }}    Tipo de Estructura: {{ line[1] }}    {% if line[2] %}Correcta{% else %}Incorrecta{% endif %}
                {% endfor %}
                </pre>
            </div>
            {% endif %}
        </div>
    </body>
    </html>
    """, code=code, lexical_result=lexical_result, syntactic_result=syntactic_result)

if __name__ == '__main__':
    app.run(debug=True)
