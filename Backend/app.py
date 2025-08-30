from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import openai
import PyPDF2
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


openai.api_key = *** 


app = Flask(__name__)
CORS(app)
@app.route("/")
def home():
    return render_template("index.html")

def preprocessar_texto(texto):
    tokens = nltk.word_tokenize(texto.lower())
    stop_words = set(stopwords.words('portuguese'))
    lemmatizer = WordNetLemmatizer()
    tokens_filtrados = [lemmatizer.lemmatize(t) for t in tokens if t.isalpha() and t not in stop_words]
    return " ".join(tokens_filtrados)

def classificar_produtividade(texto):
    prompt = (
        "Classifique o seguinte email como 'Produtivo' ou 'Improdutivo' e explique brevemente o motivo:\n"
        f"Email: {texto}\n"
        "Resposta:"
    )
    resposta = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=60,
        temperature=0.2,
        n=1,
        stop=None,
    )
    texto_resposta = resposta.choices[0].text.strip()
    if "produtivo" in texto_resposta.lower():
        categoria = "Produtivo"
    else:
        categoria = "Improdutivo"
    return categoria, texto_resposta

def gerar_resposta_automatica(texto, categoria):
    prompt = (
        f"Considere o seguinte email classificado como '{categoria}'. "
        "Gere uma resposta automática educada e adequada para o remetente:\n"
        f"Email: {texto}\n"
        "Resposta:"
    )
    resposta = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=60,
        temperature=0.5,
        n=1,
        stop=None,
    )
    return resposta.choices[0].text.strip()

@app.route("/processar-email", methods=["POST"])
def processar_email():
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

        texto_preprocessado = preprocessar_texto(content)
        categoria, explicacao = classificar_produtividade(texto_preprocessado)
        resposta = gerar_resposta_automatica(content, categoria)
        return jsonify({"categoria": categoria, "explicacao": explicacao, "resposta": resposta})

    else:
        data = request.json
        texto = data.get("texto", "")
        texto_preprocessado = preprocessar_texto(texto)
        categoria, explicacao = classificar_produtividade(texto_preprocessado)
        resposta = gerar_resposta_automatica(texto, categoria)
        return jsonify({"categoria": categoria, "explicacao": explicacao, "resposta": resposta})

if __name__ == "__main__":
    app.run(debug=True)