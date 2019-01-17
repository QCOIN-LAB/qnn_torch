# -*- coding: utf-8 -*-

import torch
import torch.nn as nn
import torch.nn.functional as F

class SentiFastText(nn.Module): 
    def __init__(self, opt): 
        super(SentiFastText, self).__init__() 
        self.opt = opt
        sentiment_lexicon = opt.sentiment_dic
        if sentiment_lexicon is not None:
            self.sentiment_lexicon = torch.tensor(sentiment_lexicon, dtype=torch.float).to(opt.device)
        embedding_matrix = torch.tensor(opt.lookup_table, dtype=torch.float)
        self.embed = nn.Embedding(embedding_matrix.shape[0], embedding_matrix.shape[1])
        self.linear = nn.Linear(50, 200)
        self.bn = nn.BatchNorm1d(200)
        self.fc = nn.Linear(200, 2)
        self.senti_fc = nn.Linear(50, 2)

    def forward(self, inp):
        text_indices = inp
        embed = self.embed(text_indices) 
        x = torch.mean(embed, dim=1)
        x = self.linear(x)
        x = self.bn(x)  
        output = self.fc(x)

        indices = text_indices.flatten(-2, -1) # batch_size*seq_len
        choices = self.sentiment_lexicon.index_select(0, indices).squeeze(-1) # batch_size*seq_len
        nonzero_indices = torch.nonzero(choices).squeeze(-1)
        indices = indices.index_select(0, nonzero_indices)
        choices = choices.index_select(0, nonzero_indices)
        masked_embed = self.embed(indices)
        senti_output = self.senti_fc(masked_embed)
        senti_target = (choices.long() + 1) / 2

        return senti_output, senti_target, output