# Shared rules for compliance checking
# This file is used by both the Crawler (for visual highlighting) and the Compliance Engine (for logic)

FORBIDDEN_TERMS = {
    "crédito fácil": "Uso de termo proibido que sugere facilidade excessiva.",
    "sem verificação": "Sugere ausência de avaliação de solvabilidade.",
    "sem burocracia": "Termo enganoso, sugere processo sem trâmites legais.",
    "aprovação garantida": "Promessa falsa, a aprovação depende de análise.",
    "dinheiro imediato": "Sugere rapidez irrealista.",
    "sem juros": "Só permitido se a TAEG for 0%. Verifique se é o caso.",
    "0% de juros": "Só permitido se a TAEG for 0%. Verifique se é o caso.",
    "custo zero": "Proibido se existirem quaisquer encargos (impostos, comissões).",
    "mais baixo do mercado": "Proibido salvo se comprovado documentalmente na mesma publicidade.",
    "melhor taxa": "Subjetivo e proibido sem comprovação objetiva.",
    "resolução imediata": "Sugere automatismo proibido na concessão de crédito."
}
