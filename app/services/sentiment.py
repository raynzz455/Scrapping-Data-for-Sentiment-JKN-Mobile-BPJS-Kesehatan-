"""
Service: analisis sentimen menggunakan IndoBERT.
Model: taufiqdp/indonesian-sentiment (fine-tuned IndoBERT)
Output: positif | netral | negatif
"""
import os
import logging
from functools import lru_cache

from tqdm import tqdm

logger = logging.getLogger(__name__)

MODEL_NAME  = os.getenv("SENTIMENT_MODEL", "taufiqdp/indonesian-sentiment")
BATCH_SIZE  = int(os.getenv("SENTIMENT_BATCH_SIZE", "32"))
LABEL_MAP   = {0: "negatif", 1: "netral", 2: "positif"}


# ── Model loader (singleton) ──────────────────────────────

@lru_cache(maxsize=1)
def _load_model():
    """Load tokenizer + model sekali, cache selamanya."""
    try:
        import torch
        from transformers import (
            AutoTokenizer,
            AutoModelForSequenceClassification,
        )
    except ImportError:
        raise ImportError("Jalankan: uv add transformers torch")

    logger.info(f"Memuat model: {MODEL_NAME}")
    logger.info("Download ~450 MB pertama kali, lalu dari cache HuggingFace.")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model     = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
    model.eval()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model  = model.to(device)
    logger.info(f"Model siap — device: {device.upper()}")
    return tokenizer, model, device


# ── Inference ─────────────────────────────────────────────

def _predict_batch(texts: list[str], tokenizer, model, device: str) -> list[str]:
    import torch
    inputs = tokenizer(
        texts,
        padding=True,
        truncation=True,
        max_length=128,
        return_tensors="pt",
    ).to(device)
    with torch.inference_mode():
        logits = model(**inputs).logits
    preds = logits.argmax(dim=1).cpu().tolist()
    return [LABEL_MAP[p] for p in preds]


def predict_sentiment(reviews: list[dict]) -> list[dict]:
    """
    Tambahkan field 'sentiment' dan 'sentiment_bin' ke setiap review.

    Args:
        reviews: list of dict — hasil scraping

    Returns:
        list of dict dengan 2 field baru:
          sentiment:     "positif" | "netral" | "negatif"
          sentiment_bin: "positif" | "negatif/netral"
    """
    if not reviews:
        return reviews

    tokenizer, model, device = _load_model()

    # Pisahkan yang punya konten dan yang kosong
    contents   = [r.get("content", "").strip() for r in reviews]
    sentiments = ["netral"] * len(reviews)

    non_empty = [(i, c) for i, c in enumerate(contents) if c]
    texts_ne  = [c for _, c in non_empty]
    idxs_ne   = [i for i, _ in non_empty]

    logger.info(f"Menganalisis sentimen {len(texts_ne)} ulasan (dari {len(reviews)} total)...")

    with tqdm(total=len(texts_ne), desc="🧠 Sentiment", unit="ulasan") as pbar:
        for start in range(0, len(texts_ne), BATCH_SIZE):
            batch_texts = texts_ne[start:start + BATCH_SIZE]
            batch_preds = _predict_batch(batch_texts, tokenizer, model, device)
            for j, pred in enumerate(batch_preds):
                sentiments[idxs_ne[start + j]] = pred
            pbar.update(len(batch_texts))

    for i, review in enumerate(reviews):
        s = sentiments[i]
        review["sentiment"]     = s
        review["sentiment_bin"] = "positif" if s == "positif" else "negatif/netral"

    # Log distribusi
    from collections import Counter
    counts = Counter(sentiments)
    total  = len(reviews)
    logger.info("Distribusi sentimen:")
    for label in ["positif", "netral", "negatif"]:
        n   = counts.get(label, 0)
        pct = n / total * 100 if total else 0
        logger.info(f"  {label:10s}: {n:4d} ({pct:.1f}%)")

    return reviews
