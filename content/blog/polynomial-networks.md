---
title: "Polynomial Networks"
date: 2026-09-02
programme: "I"
kicker: "Algebraic Models"
summary: "A programme for neural architectures whose algebraic structure is explicit enough to study, control, and reuse."
thesis: "Polynomial structure can serve as a common language between approximation theory, neural architecture design, and exact interpretation."
questions:
  - "Which neural constructions are genuinely new, and which are reparameterisations of polynomial models?"
  - "How does polynomial degree govern expressivity, stability, trainability, and computational cost?"
  - "Can algebraically constrained networks make attribution exact without surrendering predictive performance?"
works:
  - title: "Exploring Kolmogorov-Arnold Networks for Realistic Image Sharpness Assessment"
    meta: "TaylorKAN · IEEE ICASSP 2025"
    paper: "https://doi.org/10.1109/ICASSP49660.2025.10890447"
    code: "https://github.com/Muyuzhierchengse/TaylorKAN"
  - title: "A Polynomial Architecture-Attribution Co-Design Framework for Exact Aumann-Shapley Attribution in GNNs"
    meta: "APEX · arXiv:2607.21094"
    paper: "https://arxiv.org/abs/2607.21094"
    code: "https://github.com/Muyuzhierchengse/APEX"
directions:
  - title: "From TaylorKAN to a family of polynomial architectures"
    text: "Generalise the Taylor-series construction beyond a single model and organise polynomial networks by basis, degree, interaction order, and compositional depth."
  - title: "Expressivity and equivalence"
    text: "Characterise when new neural modules change representational power and when they merely induce a different parameterisation or optimisation geometry."
  - title: "Exact interpretation by construction"
    text: "Co-design architectures and attribution rules so that explanations follow analytically from the model rather than from post-hoc approximation."
applications:
  - "Image quality assessment"
  - "Scientific machine learning"
  - "Exact model attribution"
  - "Compact neural architectures"
---
