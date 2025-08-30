from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import PyPDF2
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from openai import OpenAI

# -----------------------------
# Configuração NLTK
# -----------------------------
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# -----------------------------
# Inicialização OpenAI
# -----------------------------
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -----------------------------
# Inicialização Flask
# -----------------------------
app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# -----------------------------
# Rota principal
# -----------------------------
@app.route("/")
def home():
    """
    Renderiza a página principal
    """
    return render_template("index.html")

# -----------------------------
# Função: Pré-processamento de texto
# -----------------------------
def preprocessar_texto(texto):
    """
    Tokeniza, remove stopwords e aplica lematização
    """
    tokens = nltk.word_tokenize(texto.lower())
    stop_words = set(stopwords.words('portuguese'))
    lemmatizer = WordNetLemmatizer()
    tokens_filtrados = [lemmatizer.lemmatize(t) for t in tokens if t.isalpha() and t not in stop_words]
    return " ".join(tokens_filtrados)

# -----------------------------
# Função: Classificar produtividade
# -----------------------------
def classificar_produtividade(texto):
    """
    Classifica o email como 'Produtivo' ou 'Improdutivo' usando OpenAI.
    Se a API não estiver disponível ou a quota zerada, retorna fallback gratuito.
    """
    prompt = (
        "Classifique o seguinte email como 'Produtivo' ou 'Improdutivo' e explique brevemente o motivo:\n"
        f"Email: {texto}\n"
        "Resposta:"
    )

    try:
        resposta = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você é um assistente que classifica emails."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.3
        )

        conteudo = resposta.choices[0].message.content
        categoria = "Produtivo" if "produtivo" in conteudo.lower() else "Improdutivo"
        return categoria, conteudo

    except Exception:
        # Fallback caso API não tenha créditos
        return "Produtivo", (
            "Simulação: email classificado como produtivo "
            "(API disponível, mas sua conta OpenAI não possui créditos suficientes)"
        )

# -----------------------------
# Função: Gerar resposta automática
# -----------------------------
def gerar_resposta_automatica(texto, categoria):
    """
    Gera uma resposta automática com base na categoria do email
    """
    try:
        resposta = client.completions.create(
            model="text-davinci-003",
            prompt=(
                f"Considere o seguinte email classificado como '{categoria}'. "
                "Gere uma resposta automática educada e adequada para o remetente:\n"
                f"Email: {texto}\n"
                "Resposta:"
            ),
            max_tokens=60,
            temperature=0.5
        )
        return resposta.choices[0].text.strip()

    except Exception:
        # Fallback caso API não tenha créditos
        return f"Simulação de resposta automática para email classificado como '{categoria}'."

# -----------------------------
# Endpoint: Processar email
# -----------------------------
@app.route("/processar-email", methods=["POST"])
def processar_email():
    try:
        # Verifica se enviou arquivo
        if "file" in request.files:
            file = request.files["file"]
            content = ""
            if file.filename.endswith(".txt"):
                content = file.read().decode("utf-8")
            elif file.filename.endswith(".pdf"):
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    content += page.extract_text() or ""
            else:
                return jsonify({"error": "Formato de arquivo não suportado"}), 400
        else:
            # Texto direto no corpo da requisição
            data = request.json
            content = data.get("texto", "")

        # Pré-processamento
        texto_preprocessado = preprocessar_texto(content)
        # Classificação
        categoria, explicacao = classificar_produtividade(texto_preprocessado)
        # Resposta automática
        resposta = gerar_resposta_automatica(content, categoria)

        return jsonify({"categoria": categoria, "explicacao": explicacao, "resposta": resposta})

    except Exception as e:
        return jsonify({"categoria": "Erro", "explicacao": str(e), "resposta": ""})

# -----------------------------
# Endpoint: Validar arquivo
# -----------------------------
@app.route("/validate", methods=["POST"])
def validate_file():
    if "file" not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400
    return jsonify({"status": "ok"})

# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    # Para deploy, alterar host='0.0.0.0' e remover debug
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
