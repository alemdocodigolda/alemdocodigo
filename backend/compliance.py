from typing import List, Dict
import re

async def analyze_compliance(pages_data: List[Dict]) -> Dict:
    """
    Analyzes compliance for each page crawled.
    pages_data: List of {'url': ..., 'text': ..., 'screenshot': ...}
    """
    
    total_score = 100
    all_issues = []
    
    # Analyze each page
    for page in pages_data:
        # Normalize text: remove line breaks to handle phrases split across lines (e.g. footer columns)
        raw_text = page['text'].lower()
        text = re.sub(r'\s+', ' ', raw_text.replace('\n', ' '))
        
        url = page['url']
        screenshot = page['screenshot']
        
        print(f"Analyzing page: {url} | Text length: {len(text)}")
        
        page_issues = []
        
        # Rule 0: Content Check
        if len(text) < 200:
             page_issues.append({
                "rule": "Erro de Leitura",
                "severity": "high",
                "description": "Não foi possível ler conteúdo suficiente nesta página.",
                "suggestion": "Verifique se o site bloqueia bots ou se está acessível.",
                "context": "Texto extraído insuficiente.",
                "url": url,
                "screenshot": screenshot
            })
             total_score -= 100 # Fail immediately
             all_issues.extend(page_issues)
             continue

        # Rule 0.1: Context Relevance Check (User Request)
        # Check if the site is actually about credit
        credit_keywords = ["crédito", "credito", "financiamento", "empréstimo", "emprestimo", 
                          "hipotecário", "hipotecario", "mútuo", "mutuo", "taeg", "tan", "mtic"]
        
        relevance_score = 0
        for kw in credit_keywords:
            if kw in text:
                relevance_score += 1
        
        if relevance_score < 2: # Very low threshold, just to catch completely unrelated sites
             page_issues.append({
                "rule": "Site Não Identificado como Intermediação",
                "severity": "info", # Not a penalty, just info
                "description": "O site analisado não apresenta conteúdo típico de intermediação de crédito.",
                "suggestion": "Se este é um site de crédito, adicione termos claros como 'Crédito', 'Financiamento', etc.",
                "context": "Ausência de termos financeiros chave.",
                "url": url,
                "screenshot": screenshot,
                "location_guide": "Análise Global"
            })
             # Don't penalize score heavily if it's just the wrong site, but show it's not compliant/relevant
             # We assume 100 score (compliant) for a non-credit site? Or 0?
             # User asked to "say it does not present characteristics".
             # Let's set a specific status logic later.
             # For now, we continue but mark it.
             pass

        # Rule 1: Identification (Aviso n.º 5/2024)
        # Regex updated to include 'autorizado' which is common
        # RELAXED RULE: Check for presence of key terms anywhere, not necessarily adjacent
        # Many footers have "Registo: XXX" .... [Header text] ... "Supervisionado pelo Banco de Portugal"
        
        has_bdp = "banco de portugal" in text
        has_registo = any(term in text for term in ["registo", "autorizado", "licença", "n.º", "nº", "número"])
        
        # Rule 1 Check
        if not (has_bdp and has_registo):
             # Only penalize if page has substantial text
            page_issues.append({
                "rule": "Identificação de Registo",
                "severity": "high",
                "description": "Não foi encontrada a menção obrigatória ao registo/autorização E ao Banco de Portugal.",
                "suggestion": "Certifique-se que tem 'Registo n.º XXX' e 'Banco de Portugal' visíveis no rodapé.",
                "context": "Falta menção explícita ao regulador ou número de registo.",
                "url": url,
                "screenshot": screenshot,
                "location_guide": "Rodapé/Cabeçalho"
            })
            total_score -= 10
        else:
             # SUCCESS: Rule 1 passed
             page_issues.append({
                "rule": "Identificação de Registo",
                "severity": "success",
                "description": "A identificação de registo e menção ao Banco de Portugal estão presentes.",
                "suggestion": "Nada a corrigir.",
                "context": "Registo e Regulador identificados corretamente.",
                "url": url,
                "screenshot": screenshot,
                "location_guide": "Rodapé Encontrado"
            })

        # Rule 1.1: Activity Category (Guia Prático)
        if "intermediário de crédito" not in text and "intermediario de credito" not in text:
             page_issues.append({
                "rule": "Menção à Atividade",
                "severity": "high",
                "description": "A designação 'Intermediário de Crédito' é obrigatória e não foi encontrada.",
                "suggestion": "Deve identificar-se inequivocamente como 'Intermediário de Crédito' (Vinculado/Acessório/etc).",
                "context": "Falta a designação da atividade.",
                "url": url,
                "screenshot": screenshot,
                "location_guide": "Geral (Todo o Site)"
            })
             total_score -= 10
        else:
             page_issues.append({
                "rule": "Menção à Atividade",
                "severity": "success",
                "description": "A designação 'Intermediário de Crédito' foi encontrada.",
                "suggestion": "Manter a designação clara e visível.",
                "context": "Designação da atividade presente.",
                "url": url,
                "screenshot": screenshot,
                "location_guide": "Geral (Todo o Site)"
            })

        # Rule 2: Forbidden Terms (Extended per Aviso 5/2024)
        from .rules import FORBIDDEN_TERMS
        
        # Parse HTML for Location Guide
        soup = None
        if 'html' in page:
            from bs4 import BeautifulSoup
            try:
                soup = BeautifulSoup(page['html'], 'html.parser')
                # Remove script and style elements to avoid matching CSS/JS
                for script in soup(["script", "style"]):
                    script.extract()
            except:
                pass

        for term, reason in FORBIDDEN_TERMS.items():
            if term in text:
                # Extract context window
                start = max(0, text.find(term) - 50)
                end = min(len(text), text.find(term) + 50)
                context_snippet = "..." + text[start:end].replace('\n', ' ') + "..."
                
                # Dynamic suggestion based on term
                suggestion_text = f"O termo '{term}' é considerado de risco. Substitua por uma descrição objetiva do processo."
                if "fácil" in term or "imediato" in term:
                    suggestion_text = f"Substitua '{term}' por 'processo ágil' ou 'resposta rápida' (condicionado à realidade). Evite promessas de automatismo."
                elif "sem juros" in term or "0%" in term:
                    suggestion_text = f"Só pode usar '{term}' se a TAEG for efetivamente 0%. Caso contrário, deve indicar a TAEG correta."
                elif "garantida" in term:
                    suggestion_text = f"Remova '{term}'. A concessão de crédito depende sempre da análise de solvabilidade e não pode ser garantida a priori."
                
                # Determine Location Guide
                location_guide = "Texto encontrado na página."
                if soup:
                     matches = soup.find_all(string=re.compile(re.escape(term), re.IGNORECASE))
                     if matches:
                         # Pick the first one
                         target = matches[0]
                         parent = target.parent
                         tag_name = parent.name
                         classes = "." + ".".join(parent.get('class', [])) if parent.get('class') else ""
                         location = f"Tag: <{tag_name}{classes}>"
                         # Extract context around term
                         start_idx = target.lower().find(term.lower())
                         context_snippet = f"...{target[max(0, start_idx-20):start_idx+len(term)+20]}..."

                page_issues.append({
                    "rule": "Termo Proibido Detectado",
                    "severity": "critical",
                    "description": reason,
                    "suggestion": f"Remova a expressão '{term}' e substitua por linguagem mais objetiva.",
                    "context": context_snippet,
                    "url": url,
                    "screenshot": screenshot,
                    "location_guide": location
                })
                total_score -= 5
        
        if not found_forbidden:
             page_issues.append({
                "rule": "Termos Proibidos",
                "severity": "success",
                "description": "Não foram detetados termos proibidos (ex: 'crédito fácil', 'sem burocracia').",
                "suggestion": "Continue a usar linguagem clara e objetiva.",
                "context": "Nenhuma inconformidade detetada.",
                "url": url,
                "screenshot": screenshot,
                "location_guide": "Análise Global"
            })
            
        # Rule 3: TAEG (If numbers/rates are present) changes
        # Refined to avoid false positives like "Top 5%", "100% Online"
        
        has_suspicious_rate = False
        suspicious_element = None
        
        ignored_contexts = ["top", "scoring", "online", "digital", "satisfação", "cliente", "processo", "100%"]
        
        pass_check_taeg = False 

        if "%" in text and "taeg" not in text and "taxa anual" not in text:
            if soup:
                # Find elements with "%" text
                elements_with_percent = soup.find_all(string=re.compile(r'\d+([.,]\d+)?\s*%'))
                
                for el in elements_with_percent:
                    text_lower = el.lower()
                    # Check if this specific occurrence is safe
                    is_safe = False
                    for ignore in ignored_contexts:
                        if ignore in text_lower:
                            is_safe = True
                            break
                    
                    if not is_safe:
                        has_suspicious_rate = True
                        suspicious_element = el
                        break
            else:
                # Fallback for non-HTML text analysis
                has_suspicious_rate = True
        elif "%" in text and ("taeg" in text or "taxa anual" in text):
             pass_check_taeg = True

        if has_suspicious_rate:
             # Heuristic: if there is a percentage but no mention of TAEG
             # Try to find the specific element with the % to give a location
            taeg_location = "Geral (Página contém % sem TAEG explícita)"
            found_context = "Oferta de valores/taxas sem TAEG explícita"
            
            if suspicious_element:
                target = suspicious_element
                parent = target.parent
                tag_name = parent.name
                classes = "." + ".".join(parent.get('class', [])) if parent.get('class') else ""
                
                found_context = f"...{target.strip()[:50]}..."
                taeg_location = f"Tag: <{tag_name}{classes}> (contém '{target.strip()[:20]}...')"

            page_issues.append({
                "rule": "Falta de TAEG",
                "severity": "high",
                "description": "Existem taxas (%) apresentadas sem a correspondente TAEG.",
                "suggestion": "Sempre que apresentar taxas de juro, deve apresentar a TAEG com destaque igual ou superior.",
                "context": found_context,
                "url": url,
                "screenshot": screenshot,
                "location_guide": taeg_location
            })
            total_score -= 10
        elif pass_check_taeg:
             page_issues.append({
                "rule": "Exibição de TAEG",
                "severity": "success",
                "description": "As taxas apresentadas parecem estar acompanhadas da respetiva TAEG.",
                "suggestion": "Manter a consistência na apresentação de taxas.",
                "context": "Contexto adequado encontrado.",
                "url": url,
                "screenshot": screenshot,
                "location_guide": "Verificação de Taxas"
            })
            
        all_issues.extend(page_issues)

    # Deduplicate issues
    unique_issues = []
    seen_signatures = set()
    
    for issue in all_issues:
        signature = (issue['rule'], issue['description'], issue['context'])
        
        if signature not in seen_signatures:
            seen_signatures.add(signature)
            unique_issues.append(issue)
    
    # Recalculate score based on UNIQUE issues to avoid double penalization for site-wide template errors
    # Reset score to 100 and subtract based on unique findings
    final_score = 100
    for issue in unique_issues:
        if issue['severity'] == 'high':
            final_score -= 10
        elif issue['severity'] == 'medium':
            final_score -= 5
        elif issue['severity'] == 'low':
            final_score -= 2
            
    final_score = max(0, min(100, final_score)) # Ensure score is between 0 and 100
    # Determine status
    status = "Conforme"
    
    # Check for relevance flag
    is_irrelevant = any(i['rule'] == "Site Não Identificado como Intermediação" for i in unique_issues)
    
    if is_irrelevant:
        status = "Não Aplicável / Sem Conteúdo de Crédito"
        # Filter out other compliance errors if it's not a credit site to avoid confusion?
        # User said "podes mesmo dizer que o site nao apresenta caracteristica".
        # We keep the "Info" issue and maybe hide others or keep them as backup.
        # Let's keep them but the main status tells the story.
        final_score = 0 # Or N/A
    elif final_score < 50:
        status = "Crítico"
    elif final_score < 80:
        status = "Atenção Necessária"
    elif final_score < 100:
        status = "Bom (Com avisos)"

    return {
        "score": max(0, final_score),
        "status": status,
        "issues": unique_issues,
        "scanned_pages": len(pages_data)
    }
