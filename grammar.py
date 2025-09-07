import torch
from gramformer import Gramformer

# Initialize once and reuse
gf = Gramformer(models=1, use_gpu=torch.cuda.is_available())

def improve_grammar(text: str) -> str:
    try:
        corrections = list(gf.correct(text, max_candidates=1))
        return corrections[0] if corrections else text
    except Exception as e:
        print(f"Grammar correction failed: {e}")
        return text
