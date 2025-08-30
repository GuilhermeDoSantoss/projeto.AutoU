async function processarEmail() {
            const texto = document.getElementById("texto").value.trim();
            const arquivo = document.getElementById("arquivo").files[0];
            const resultadoDiv = document.getElementById("resultado");
            const erroDiv = document.getElementById("erro");
            const loadingDiv = document.getElementById("loading");
            const btn = document.getElementById("btnProcessar");

            resultadoDiv.style.display = "none";
            erroDiv.style.display = "none";

            if (!arquivo && !texto) {
                erroDiv.innerText = "Por favor, insira um texto ou selecione um arquivo.";
                erroDiv.style.display = "block";
                return;
            }

            loadingDiv.style.display = "block";
            btn.disabled = true;

            try {
                let response;
                if (arquivo) {
                    const formData = new FormData();
                    formData.append("file", arquivo);

                    response = await fetch("http://127.0.0.1:5000/processar-email", {
                        method: "POST",
                        body: formData
                    });
                } else {
                    response = await fetch("http://127.0.0.1:5000/processar-email", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ texto })
                    });
                }

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.error || "Erro ao processar o email.");
                }

                resultadoDiv.innerHTML = `
                    <strong>Categoria:</strong> ${data.categoria}<br>
                    <div class="explicacao"><strong>Motivo:</strong> ${data.explicacao}</div>
                    <br>
                    <strong>Resposta sugerida:</strong><br>
                    <span>${data.resposta}</span>
                `;
                resultadoDiv.style.display = "block";
            } catch (err) {
                erroDiv.innerText = err.message;
                erroDiv.style.display = "block";
            } finally {
                loadingDiv.style.display = "none";
                btn.disabled = false;
            }
        }
