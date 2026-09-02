---
title: "GNN Interpretability"
date: 2026-09-02
programme: "III"
kicker: "Trustworthy Reasoning"
summary: "A programme for explanations that respect graph structure, message-passing dynamics, and attribution principles."
thesis: "A faithful graph explanation should reveal how information moves through the model, which structures sustain that movement, and why their contributions satisfy meaningful axioms."
questions:
  - "When does an explanation reflect the model's actual message flow rather than a plausible subgraph found after the fact?"
  - "How should node, edge, feature, and substructure contributions be reconciled within one attribution framework?"
  - "Can architecture design remove the approximation error and evaluation cost of path-based attribution?"
works:
  - title: "FSX: Message Flow Sensitivity Enhanced Structural Explainer for Graph Neural Networks"
    meta: "Message-flow sensitivity · Cooperative games · arXiv:2601.14730"
    paper: "https://arxiv.org/abs/2601.14730"
  - title: "A Polynomial Architecture-Attribution Co-Design Framework for Exact Aumann-Shapley Attribution in GNNs"
    meta: "APEX · Exact attribution · arXiv:2607.21094"
    paper: "https://arxiv.org/abs/2607.21094"
    code: "https://github.com/Muyuzhierchengse/APEX"
directions:
  - title: "Message-flow faithful explanation"
    text: "Use internal information pathways to constrain the external substructures considered by an explainer."
  - title: "Structural cooperative games"
    text: "Develop contribution rules that account for interactions between graph components instead of treating them as independent features."
  - title: "Architecture-attribution co-design"
    text: "Build GNNs whose mathematical form makes complete and exact attribution computationally accessible."
applications:
  - "Model debugging"
  - "Scientific graph analysis"
  - "Reasoning audits"
  - "Reliable graph learning"
---
