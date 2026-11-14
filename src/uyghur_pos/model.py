from collections import Counter
import torch
from torch import nn
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence
from .data import UPOS, validate_tokens

def vocabulary(rows):
    words = Counter(w for r in rows for w in r['tokens'])
    chars = sorted(set(c for w in words for c in w))
    return dict(words={w:i+2 for i,w in enumerate(sorted(words))},
                chars={c:i+2 for i,c in enumerate(chars)}, frequencies=dict(words), labels=UPOS)

def batch(rows, vocab, device):
    for row in rows: validate_tokens(row['tokens'])
    lengths = [len(r['tokens']) for r in rows]
    if not lengths or min(lengths) == 0: raise ValueError('empty training sentences')
    width = max(lengths)
    char_width = max(len(w) for r in rows for w in r['tokens'])
    word_ids = torch.zeros(len(rows), width, dtype=torch.long)
    char_ids = torch.zeros(len(rows), width, char_width, dtype=torch.long)
    char_lengths = torch.ones(len(rows), width, dtype=torch.long)
    labels = torch.full((len(rows), width), -100, dtype=torch.long)
    label_ids = {label:i for i,label in enumerate(vocab['labels'])}
    for i,row in enumerate(rows):
        for j,word in enumerate(row['tokens']):
            word_ids[i,j] = vocab['words'].get(word, 1)
            chars = [vocab['chars'].get(c,1) for c in word]
            char_ids[i,j,:len(chars)] = torch.tensor(chars)
            char_lengths[i,j] = len(chars)
            if 'upos' in row: labels[i,j] = label_ids[row['upos'][j]]
    return word_ids.to(device), char_ids.to(device), char_lengths, lengths, labels.to(device)

class Tagger(nn.Module):
    def __init__(self, vocab, word_dim=64, char_dim=24, char_hidden=32, hidden=128, dropout=.25, use_chars=True, word_dropout=0.):
        super().__init__()
        self.use_chars = use_chars
        if not 0 <= word_dropout < 1: raise ValueError('word_dropout must be in [0,1)')
        self.word_dropout = word_dropout
        self.words = nn.Embedding(len(vocab['words'])+2, word_dim, padding_idx=0)
        if use_chars:
            self.chars = nn.Embedding(len(vocab['chars'])+2, char_dim, padding_idx=0)
            self.char_rnn = nn.GRU(char_dim, char_hidden, batch_first=True, bidirectional=True)
        self.dropout = nn.Dropout(dropout)
        self.rnn = nn.LSTM(word_dim + (2*char_hidden if use_chars else 0), hidden,
                           batch_first=True, bidirectional=True)
        self.head = nn.Linear(hidden*2, len(vocab['labels']))

    def forward(self, words, chars, char_lengths, lengths):
        emb = self.words(words)
        if self.training and self.word_dropout:
            keep = torch.rand((*words.shape,1),device=words.device) >= self.word_dropout
            emb = emb * keep / (1-self.word_dropout)
        if self.use_chars:
            b,t,c = chars.shape
            packed = pack_padded_sequence(self.chars(chars.reshape(b*t,c)),
                                          char_lengths.reshape(-1), batch_first=True, enforce_sorted=False)
            _, h = self.char_rnn(packed)
            encoded = torch.cat([h[0],h[1]],-1).reshape(b,t,-1)
            emb = torch.cat([emb,encoded],-1)
        packed = pack_padded_sequence(self.dropout(emb), lengths, batch_first=True, enforce_sorted=False)
        out,_ = self.rnn(packed)
        out,_ = pad_packed_sequence(out,batch_first=True,total_length=words.shape[1])
        return self.head(self.dropout(out))

def load_model(path, device='cpu'):
    state = torch.load(path, map_location=device, weights_only=True)
    model = Tagger(state['vocab'], **state['config']).to(device)
    model.load_state_dict(state['model']); model.eval()
    return model, state

@torch.inference_mode()
def predict(model, rows, vocab, device='cpu', batch_size=32):
    model.eval()
    result = []
    for start in range(0,len(rows),batch_size):
        group = rows[start:start+batch_size]
        # CLI handles empty rows separately; datasets must contain nonempty sentences.
        words,chars,clens,lens,_ = batch(group,vocab,device)
        ids = model(words,chars,clens,lens).argmax(-1).cpu().tolist()
        for row,values,n in zip(group,ids,lens):
            result.append(dict(sent_id=row.get('sent_id',''),tokens=row['tokens'],
                               upos=[vocab['labels'][i] for i in values[:n]]))
    return result
