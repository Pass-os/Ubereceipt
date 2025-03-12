Segue abaixo o conteúdo completo do arquivo **README.md** para o projeto. Você pode copiar esse conteúdo e salvar em um arquivo chamado `README.md` na raiz do projeto:

---

```markdown
# UberCost

Projeto para buscar, processar e exibir e-mails de recibos da Uber utilizando Python.  
A interface gráfica é construída com **ttkbootstrap** para um visual moderno e o PyWebView é usado para pré-visualizar os e-mails em HTML.

---

## Pré-Requisitos

- **Python 3.11** (ou versão similar)
- **Conta do Gmail** habilitada para acesso IMAP  
  > Caso utilize verificação em duas etapas, gere uma senha de aplicativo.
- **Git** (opcional, para clonar o repositório)

---

## Como Baixar o Projeto

### Opção A: Clonar via Git

```bash
git clone https://github.com/seu-usuario/uber-cost.git
cd uber-cost
```

### Opção B: Download do ZIP

1. Acesse a página do repositório no GitHub.
2. Clique em **Code** e, em seguida, **Download ZIP**.
3. Extraia o arquivo ZIP na pasta de sua preferência e abra um terminal nesta pasta.

---

## Configuração do Ambiente

### 1. Criar e Ativar o Ambiente Virtual

Crie um ambiente virtual:

```bash
python -m venv venv
```

Ative o ambiente virtual:

- **Windows**:
  ```bash
  venv\Scripts\activate
  ```
- **Linux / macOS**:
  ```bash
  source venv/bin/activate
  ```

> Quando o ambiente estiver ativo, o prompt exibirá algo como `(venv)`.

### 2. Instalar Dependências

Com o ambiente virtual ativo, instale as dependências. Caso o projeto possua um arquivo `requirements.txt`, utilize:

```bash
pip install -r requirements.txt
```

Caso contrário, instale manualmente as bibliotecas necessárias:

```bash
pip install ttkbootstrap pywebview python-dotenv
```

---

## Configuração de Variáveis de Ambiente

Crie um arquivo chamado **.env** na raiz do projeto (no mesmo local de `app.py`) com o seguinte conteúdo:

```
MY_EMAIL=seuemail@gmail.com
IMAP_KEY=sua_senha_ou_senha_de_aplicativo
```

> **Atenção:** O arquivo `.env` contém suas credenciais e **não deve** ser versionado.

---

## Executando o Projeto

Com o ambiente virtual ativo e as dependências instaladas, execute:

```bash
python app.py
```

A interface gráfica será iniciada. Insira o mês e o ano desejados e clique em **Buscar Emails** para carregar os recibos da Uber.

---

## Recursos e Funcionamento

- **Busca e Processamento de E-mails:**  
  O módulo `connect_email.py` conecta-se ao Gmail via IMAP e busca e-mails de `noreply@uber.com` filtrados pelo período (mês/ano).  
  Em `app.py`, os e-mails são processados para extrair informações como valor, motorista, e para classificar como "Viagem" ou "Recarga".  
  Para recargas, é utilizado um critério que busca por textos contendo "adicionou" e "uber cash".

- **Interface Gráfica:**  
  A interface utiliza **ttkbootstrap** para oferecer um visual moderno (você pode escolher temas como "flatly", "darkly", etc.) e é dividida em:
  - **Top Bar:** Para inserir o mês e ano e disparar a busca.
  - **Área Principal:** Dividida em dois painéis com um `Panedwindow`:
    - **Esquerda:** Uma tabela (Treeview) com as colunas **Dia**, **Hora**, **Motorista**, **Valor (R$)** e **Classificação**.  
      - Na coluna “Valor”, para viagens o valor é exibido com sinal negativo e para recargas com sinal positivo.  
      - A ordenação por coluna é possível clicando no cabeçalho, com setas (▲ ou ▼) indicando a direção.
      - Para diferenciar as linhas, são usadas tags: linhas de "Viagem" aparecem em vermelho e de "Recarga", em verde.
    - **Direita (Dashboard):** Um painel fixo que exibe os seguintes indicadores:
      - **Viagens:** Número total de viagens.
      - **Recarga:** Número total de recargas.
      - **Total gasto:** Soma dos valores efetivamente pagos (viagens + recargas).
      - **Total sem descontos:** Para viagens, soma de (valor + gorjeta); para recargas, o mesmo valor.
- **Pré-visualização de E-mails:**  
  Ao dar duplo clique em uma linha da tabela, o e-mail é exibido em uma nova janela usando **PyWebView**.

- **Ordenação das Colunas:**  
  Ao clicar no cabeçalho de cada coluna, os dados são ordenados (e a seta indicadora muda de direção).

---

## Contribuições

1. Faça um **fork** do repositório.
2. Crie um **branch** com suas alterações.
3. Abra um **Pull Request** descrevendo suas mudanças.

Para dúvidas ou problemas, abra uma **issue** ou entre em contato.

---

## Observações

- Caso encontre problemas com os critérios de busca IMAP (por exemplo, erros do tipo `SEARCH command error: BAD`), verifique o formato das datas e, se necessário, simplifique o critério em `connect_email.py`.
- As expressões regulares utilizadas para extrair valores podem precisar de ajustes conforme o padrão dos e-mails.
- Certifique-se de que o arquivo `.env` esteja corretamente configurado com suas credenciais.

---

Pronto! Agora você tem um guia completo para configurar, executar e contribuir com o projeto "UberCost" em outro computador.
```

---

Basta copiar esse conteúdo, colá-lo em um arquivo chamado `README.md` na raiz do seu projeto e versioná-lo com o repositório.
