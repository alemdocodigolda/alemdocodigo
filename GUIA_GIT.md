# Guia Rápido: Como Sincronizar este Projeto

## 1. Instalar num Novo Computador (Só faz uma vez)
Se estiver num computador novo (Portátil 2 ou 3):

1.  Instale o **Git** (se não tiver).
2.  Abra o VS Code ou Terminal.
3.  Vá para a pasta onde quer guardar o projeto.
4.  Escreva:
    ```bash
    git clone https://github.com/alemdocodigolda/alemdocodigo.git
    ```
5.  O projeto vai aparecer numa pasta nova!

---

## 2. No Dia-a-Dia (Rotina)

### QUANDO COMEÇA A TRABALHAR (Importante!)
Para não sobrepor trabalho de ontem, traga sempre as novidades da nuvem primeiro:

```bash
git pull
```

### QUANDO TERMINA (Para guardar)
Para enviar o seu trabalho para a nuvem:

1.  **Registar tudo:**
    ```bash
    git add .
    ```

2.  **Dar nome ao trabalho:**
    ```bash
    git commit -m "fiz alteracoes na pagina x"
    ```

3.  **Enviar:**
    ```bash
    git push
    ```

---

## Dúvidas Comuns
*   **Erro "Conflict"**: Acontece se mexer na mesma linha em 2 PCs sem fazer `git pull`. Se acontecer, chame a IA (eu)!
*   **Onde escrevo isto?**: No "Terminal" do VS Code (Menu Terminal -> New Terminal).
