import torch
from torch.nn import functional as F

def soft_distillation(logits, targets, valid, temperature):
    if temperature<=0 or targets.shape!=logits.shape:raise ValueError('invalid soft target shape/temperature')
    if not torch.isfinite(targets).all() or (targets<0).any():raise ValueError('invalid teacher probabilities')
    if not torch.allclose(targets.sum(-1)[valid],torch.ones_like(targets.sum(-1)[valid]),atol=1e-5):
        raise ValueError('teacher probabilities must sum to 1')
    per_token=F.kl_div(F.log_softmax(logits/temperature,dim=-1),targets,reduction='none').sum(-1)
    return per_token[valid].mean()*temperature**2
