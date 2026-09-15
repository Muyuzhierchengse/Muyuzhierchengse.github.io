---
title: "Graph Learning & Interpretability"
date: 2026-09-02
programme: "III"
kicker: "Structured Learning"
summary: "A programme for explanations that respect graph structure, message-passing dynamics, and attribution principles."
topics: "Message flows · Cooperative games · Exact attribution"
thesis: "A faithful graph explanation should reveal how information moves through the model, which structures sustain that movement, and why their contributions satisfy meaningful axioms."
questions:
  - "When does an explanation reflect the model's actual message flow rather than a plausible subgraph found after the fact?"
  - "How should node, edge, feature, and substructure contributions be reconciled within one attribution framework?"
  - "Can architecture design remove the approximation error and evaluation cost of path-based attribution?"
works:
  - title: "FSX: Message Flow Sensitivity Enhanced Structural Explainer for Graph Neural Networks"
    type: "Paper"
    featured: true
    status: "Revision Planned"
    status_key: "revision-planned"
    summary: "A structural explainer that relates graph explanations to the sensitivity of internal message flows."
    meta: "Message-flow sensitivity · Cooperative games · arXiv:2601.14730"
    paper: "https://arxiv.org/abs/2601.14730"
  - title: "A Polynomial Architecture-Attribution Co-Design Framework for Exact Aumann-Shapley Attribution in GNNs"
    type: "Paper"
    featured: true
    status: "Under Review"
    status_key: "under-review"
    summary: "An exact attribution framework obtained by designing graph architecture and explanation together."
    meta: "APEX · Exact attribution · arXiv:2607.21094"
    paper: "https://arxiv.org/abs/2607.21094"
    code: "https://github.com/Muyuzhierchengse/APEX"
  - title: "Graph Neural Network Interpretability"
    type: "Research Direction"
    featured: false
    status: "Coming Soon"
    status_key: "coming-soon"
    summary: "Further work on structural, message-aware, and mathematically grounded explanations for graph models."
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
