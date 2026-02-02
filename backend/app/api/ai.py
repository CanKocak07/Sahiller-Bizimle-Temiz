from __future__ import annotations

import os
from typing import Any, Dict

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel


router = APIRouter(prefix="/api/ai", tags=["ai"])


class BeachReportRequest(BaseModel):
    beach: Dict[str, Any]


def _get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise HTTPException(status_code=503, detail=f"Missing server config: {name}")
    return value


@router.post("/beach-report")
async def beach_report(payload: BeachReportRequest):
    """Generate a short Turkish report for the given beach payload.

    We keep the OpenAI key on the server (never in the frontend).
    """

    api_key = _get_required_env("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    beach = payload.beach

    system = (
                    """
            Sen bir çevresel veri analisti ve seyahat yazarı gibisin.
            Görevin: verilen sahil verilerine dayanarak KISA, DOĞAL ve
            birbirinden FARKLI metinler üretmek.

            ZORUNLU KURALLAR:
            - Sadece verilen verileri kullan.
            - Veri yoksa açıkça belirt.
            - Sayı uydurma, sebep uydurma.
            - Aynı sahil için yazıların dili tekrar etmemeli.
            - Aynı öneri kalıplarını tekrar etme (örn: "sabah daha uygun").

            STİL:
            - İnsan yazmış gibi, akıcı Türkçe
            - Teknik terimleri sadeleştir ama yok etme
            - Her raporda vurgu farklı olsun (bazen rüzgâr, bazen su, bazen konfor)

            ÇIKIŞ:
            - 3–5 cümle
            - Son cümle: tek, net, özgül bir öneri
            """
    )

    user = (
        "Aşağıdaki sahil verilerini analiz et ve turistler için 3-5 cümlelik kısa bir rapor yaz. "
        "Yüzme/güneşlenme için uygunluk, su kalitesi, hava kalitesi ve sıcaklığa odaklan. "
        "Son cümlede 1 net öneri ver (örn. ‘Sabah saatleri daha uygun’).\n\n"
        f"DATA: {beach}"
    )

    # OpenAI Responses API
    url = "https://api.openai.com/v1/responses"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    body = {
        "model": model,
        "input": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.4,
        "max_output_tokens": 220,
    }

    timeout = httpx.Timeout(20.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            resp = await client.post(url, headers=headers, json=body)
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"OpenAI request failed: {e}")

    if resp.status_code >= 400:
        raise HTTPException(status_code=502, detail=f"OpenAI error {resp.status_code}: {resp.text}")

    data = resp.json()

    # Response shape: output_text is usually present; fallback to parsing output blocks.
    text = data.get("output_text")
    if not text:
        output = data.get("output") or []
        chunks: list[str] = []
        for item in output:
            for c in item.get("content", []) or []:
                if c.get("type") in ("output_text", "text"):
                    chunks.append(c.get("text") or "")
        text = "\n".join([c for c in chunks if c]).strip()

    return {"report": text or "Analiz şu anda üretilemedi."}
