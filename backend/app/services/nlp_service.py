import random
from app.core.config import settings


MOCK_INTENTS = [
    {"intent": "abrir_solicitacao", "entities": {"servico": "protocolo administrativo"}, "suggested_action": "create_process"},
    {"intent": "consultar_processo", "entities": {"processo_id": "N/A"}, "suggested_action": "view_process"},
    {"intent": "cancelar_solicitacao", "entities": {}, "suggested_action": "cancel_process"},
    {"intent": "informacao_geral", "entities": {"topico": "prazos"}, "suggested_action": None},
    {"intent": "assinar_documento", "entities": {"documento": "contrato"}, "suggested_action": "sign_document"},
]

MOCK_RESPONSES = {
    "abrir_solicitacao": "Entendido! Vou abrir uma nova solicitação de protocolo administrativo para você. Por favor, preencha os campos necessários.",
    "consultar_processo": "Claro! Para consultar o andamento do seu processo, preciso do número do protocolo. Pode informar?",
    "cancelar_solicitacao": "Compreendo que deseja cancelar a solicitação. Confirme o número do processo para prosseguir.",
    "informacao_geral": "Os prazos padrão são de 5 dias úteis para análise inicial e 10 dias úteis para conclusão do processo.",
    "assinar_documento": "Identifico que há um documento aguardando sua assinatura. Deseja ser redirecionado para a tela de assinatura?",
}


async def analyze(text: str) -> dict:
    if settings.NLP_PROVIDER == "openai" and settings.OPENAI_API_KEY:
        return await _analyze_openai(text)
    return _analyze_mock(text)


def _analyze_mock(text: str) -> dict:
    text_lower = text.lower()
    selected = MOCK_INTENTS[0]
    if "consultar" in text_lower or "status" in text_lower:
        selected = MOCK_INTENTS[1]
    elif "cancelar" in text_lower:
        selected = MOCK_INTENTS[2]
    elif "prazo" in text_lower or "informação" in text_lower or "info" in text_lower:
        selected = MOCK_INTENTS[3]
    elif "assinar" in text_lower or "assinatura" in text_lower:
        selected = MOCK_INTENTS[4]

    return {
        "intent": selected["intent"],
        "confidence": round(random.uniform(0.82, 0.97), 2),
        "entities": selected["entities"],
        "sentiment": "neutral",
        "suggested_action": selected["suggested_action"],
        "response": MOCK_RESPONSES.get(selected["intent"], "Como posso ajudá-lo?"),
    }


async def _analyze_openai(text: str) -> dict:
    import httpx
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
            json={
                "model": "gpt-4o-mini",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are an NLP engine for a government workflow platform. "
                            "Analyze the user text and return JSON with keys: "
                            "intent (string), confidence (float 0-1), entities (object), "
                            "sentiment (positive/neutral/negative), suggested_action (string or null), "
                            "response (string in Portuguese)."
                        ),
                    },
                    {"role": "user", "content": text},
                ],
                "response_format": {"type": "json_object"},
            },
            timeout=10.0,
        )
        data = resp.json()
        import json
        return json.loads(data["choices"][0]["message"]["content"])


async def generate_summary(messages: list[dict]) -> str:
    conversation_text = "\n".join(f"{m['role']}: {m['content']}" for m in messages)
    if settings.NLP_PROVIDER == "openai" and settings.OPENAI_API_KEY:
        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": "Summarize this conversation in 2-3 sentences in Portuguese."},
                        {"role": "user", "content": conversation_text},
                    ],
                },
                timeout=10.0,
            )
            return resp.json()["choices"][0]["message"]["content"]

    return f"Conversa com {len(messages)} mensagens. Principais tópicos abordados: solicitações e consultas ao sistema."
