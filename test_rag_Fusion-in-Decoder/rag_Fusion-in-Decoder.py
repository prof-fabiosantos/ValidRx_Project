import requests
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple


# ======================================
# 1. Configurações
# ======================================

OLLAMA_URL = "http://localhost:11434/api"


def ollama_embed(model: str, text: str) -> np.ndarray:
    """Gera embeddings via Ollama /embed."""
    payload = {"model": model, "input": text}

    response = requests.post(f"{OLLAMA_URL}/embed", json=payload)
    response.raise_for_status()

    emb = response.json()["embeddings"][0]
    return np.array(emb, dtype=float)


def ollama_chat(model: str, prompt: str) -> str:
    """Gera resposta via Ollama /generate sem streaming."""
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(f"{OLLAMA_URL}/generate", json=payload)
    response.raise_for_status()

    data = response.json()

    # A resposta correta está SEMPRE aqui
    return data.get("response", "").strip()


# ======================================
# 2. Estruturas
# ======================================

@dataclass
class Chunk:
    id: int
    doc_id: str
    text: str


# ======================================
# 3. Corpus de Exemplo
# ======================================

def build_corpus() -> List[Chunk]:
    docs = {
        "doc_1": """
        Protocolo de dosagem pediátrica de Adrenalina:
        - Crianças de 1 a 5 anos: 0,05 mg via inalação.
        - Crianças de 6 a 12 anos: 0,1 mg via inalação.
        - Adultos: 0,3 mg via inalação.
        """,

        "doc_2": """
        Protocolo de segurança:
        - Nunca administrar Adrenalina intravenosa em ambiente não controlado.
        - Sempre fazer dupla checagem da via de administração.
        """,

        "doc_3": """
        Procedimentos gerais:
        - Registrar alergias, peso e sinais vitais.
        """
    }

    chunks = []
    idx = 0

    for doc_id, raw in docs.items():
        clean = " ".join(line.strip() for line in raw.splitlines() if line.strip())
        chunks.append(Chunk(id=idx, doc_id=doc_id, text=clean))
        idx += 1

    return chunks


# ======================================
# 4. RAG
# ======================================

class OllamaRAG:
    def __init__(self, chunks: List[Chunk]):
        self.chunks = chunks
        self.embeddings = None

    def build_index(self):
        print("Gerando embeddings com embeddinggemma...")
        embs = []
        for c in self.chunks:
            vec = ollama_embed("embeddinggemma:latest", c.text)
            vec = vec / np.linalg.norm(vec)
            embs.append(vec)
        self.embeddings = np.vstack(embs)

    def retrieve(self, query: str, top_k: int = 3) -> List[Tuple[Chunk, float]]:
        query_emb = ollama_embed("embeddinggemma:latest", query)
        query_emb = query_emb / np.linalg.norm(query_emb)

        sims = np.dot(self.embeddings, query_emb)
        top_idx = sims.argsort()[::-1][:top_k]

        return [(self.chunks[i], float(sims[i])) for i in top_idx]

    def build_prompt(self, question: str, retrieved: List[Tuple[Chunk, float]]) -> str:
        ctx = ""
        for i, (chunk, score) in enumerate(retrieved, start=1):
            ctx += f"\n[Trecho {i} | doc={chunk.doc_id} | score={score:.3f}]\n{chunk.text}\n"

        return f"""
Você é um assistente que responde SOMENTE com base nos trechos fornecidos.

Tarefas:
1. Leia todos os trechos.
2. Correlacione informações de diferentes documentos.
3. Responda à pergunta citando de onde veio cada informação.

=== CONTEXTO ===
{ctx}
=== FIM DO CONTEXTO ===

Pergunta: {question}

Responda de forma clara e objetiva.
""".strip()

    def answer(self, question: str):
        retrieved = self.retrieve(question)

        print("\n=== TRECHOS RECUPERADOS ===")
        for c, s in retrieved:
            print(f"\n> doc={c.doc_id} (score={s:.3f})")
            print(c.text)

        prompt = self.build_prompt(question, retrieved)

        print("\n=== PROMPT ENVIADO AO LLM ===")
        print(prompt)

        print("\n=== RESPOSTA DO MODELO ===\n")
        answer = ollama_chat("llama3.1:8b", prompt)
        print(answer)


# ======================================
# 5. Execução
# ======================================

def main():
    chunks = build_corpus()
    rag = OllamaRAG(chunks)

    rag.build_index()

    question = (
        "Qual é a dose recomendada de Adrenalina para uma criança de 6 anos "
        "e qual alerta de segurança o protocolo menciona?"
    )

    rag.answer(question)


if __name__ == "__main__":
    main()
