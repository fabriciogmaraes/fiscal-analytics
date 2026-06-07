import pdfplumber
import re
import sys
from datetime import date, datetime
from sqlalchemy.orm import Session
from database import SessionLocal, Gasto, Divida

# ── Mapeamento de categorias por palavras-chave ──────────────────
CATEGORIAS = {
    "alimentação": [
        "restaurante", "ifd", "ifood", "lanche", "pizza", "burger",
        "mexicano", "fogo", "espetaria", "delicias", "mate", "pittsburg",
        "brna", "tuca", "culinaria", "panificadora", "sacolao", "estacao",
        "jucelida", "gelaguele", "mp*estacao"
    ],
    "supermercado": [
        "supermercado", "nordestao", "mercadinho", "estrela", "superbrihodi",
        "richelly"
    ],
    "transporte": [
        "uber", "posto", "combustivel", "gasolina", "cirne", "jacutinga",
        "mirasol", "premium praia", "rota do so", "rcm", "rprn"
    ],
    "saúde": [
        "pague menos", "farmacia", "drogaria", "clinica", "hospital", "laboratorio"
    ],
    "serviços": [
        "estacao entregas", "mercadolivre", "amazon", "lc comercio",
        "achetickets", "apple", "midwest", "zn placas", "petz",
        "barbearia", "hype", "sams", "sam s", "gelaguela"
    ],
    "vestuário": [
        "riachuelo", "carlinhos", "renner", "cea", "hering"
    ],
    "educação": [
        "imd", "cambly", "curso", "escola", "faculdade", "futebolcard"
    ],
    "transferência": [
        "amanda", "maria", "karolaine", "rayanne", "pix"
    ],
}

def categorizar(descricao: str) -> str:
    desc = descricao.lower()
    for categoria, palavras in CATEGORIAS.items():
        for palavra in palavras:
            if palavra in desc:
                return categoria
    return "outros"

def extrair_lancamentos(caminho_pdf: str) -> list[dict]:
    lancamentos = []
    ano_atual = date.today().year

    with pdfplumber.open(caminho_pdf) as pdf:
        texto_completo = ""
        for pagina in pdf.pages:
            texto_completo += pagina.extract_text() + "\n"

    linhas = texto_completo.split("\n")

    for linha in linhas:
        linha = linha.strip()
        if not linha:
            continue

        # Padrão: DD/MM DESCRIÇÃO BR R$ X.XXX,XX
        padrao = r"^(\d{2}/\d{2})\s+(.+?)\s+BR\s+R\$\s*([\d\.,]+)$"
        match = re.match(padrao, linha)
        if not match:
            continue

        data_str, descricao, valor_str = match.groups()

        # Ignora pagamentos e saldo anterior
        if any(x in descricao.upper() for x in ["PGTO", "PAGAMENTO", "SALDO FATURA"]):
            continue

        # Converte valor
        valor = float(valor_str.replace(".", "").replace(",", "."))
        if valor <= 0:
            continue

        # Converte data
        dia, mes = map(int, data_str.split("/"))
        try:
            data = date(ano_atual, mes, dia)
        except:
            continue

        # Detecta se é parcelado: PARC XX/YY ou Parcela X de Y
        parcelado = False
        parcela_atual = 1
        parcela_total = 1

        match_parc = re.search(r"PARC\s+(\d+)/(\d+)", descricao.upper())
        if match_parc:
            parcelado = True
            parcela_atual = int(match_parc.group(1))
            parcela_total = int(match_parc.group(2))

        # Limpa descrição
        descricao_limpa = re.sub(r"\s+PARC\s+\d+/\d+", "", descricao).strip()
        descricao_limpa = re.sub(r"\s{2,}", " ", descricao_limpa)

        lancamentos.append({
            "data":          data,
            "descricao":     descricao_limpa,
            "valor":         valor,
            "categoria":     categorizar(descricao_limpa),
            "parcelado":     parcelado,
            "parcela_atual": parcela_atual,
            "parcela_total": parcela_total,
        })

    return lancamentos

def importar(caminho_pdf: str):
    print(f"\nLendo fatura: {caminho_pdf}")
    lancamentos = extrair_lancamentos(caminho_pdf)

    if not lancamentos:
        print("Nenhum lançamento encontrado. Verifique o PDF.")
        return

    print(f"\n{len(lancamentos)} lançamentos encontrados:\n")

    a_vista    = [l for l in lancamentos if not l["parcelado"]]
    parcelados = [l for l in lancamentos if l["parcelado"]]

    print(f"  À vista:    {len(a_vista)}")
    print(f"  Parcelados: {len(parcelados)}")

    db: Session = SessionLocal()

    try:
        # ── Gastos à vista → tabela gastos ──────────────────────
        print("\nImportando gastos à vista...")
        for l in a_vista:
            gasto = Gasto(
                descricao  = f"[BB] {l['descricao']}",
                valor      = l["valor"],
                data       = l["data"],
                categoria  = l["categoria"],
                eh_cartao  = True,
            )
            db.add(gasto)
            print(f"  ✓ {l['data'].strftime('%d/%m')} | {l['descricao'][:35]:<35} | {l['categoria']:<12} | R$ {l['valor']:.2f}")

        # ── Parcelados → tabela dividas ──────────────────────────
        print("\nImportando parcelados...")
        for l in parcelados:
            saldo_restante = l["valor"] * (l["parcela_total"] - l["parcela_atual"] + 1)
            divida = Divida(
                nome           = f"[Cartão BB] {l['descricao']}",
                valor_total    = l["valor"] * l["parcela_total"],
                valor_parcela  = l["valor"],
                parcelas_pagas = l["parcela_atual"] - 1,
                parcelas_total = l["parcela_total"],
                dia_vencimento = 3,  # vencimento do cartão BB
                status         = "em_dia",
                ativo          = True,
            )
            db.add(divida)
            print(f"  ✓ {l['descricao'][:35]:<35} | {l['parcela_atual']}/{l['parcela_total']} parcelas | R$ {l['valor']:.2f}/mês")

        db.commit()
        print(f"\n✅ Importação concluída!")
        print(f"   {len(a_vista)} gastos adicionados")
        print(f"   {len(parcelados)} parcelamentos adicionados")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Erro durante importação: {e}")
        raise
    finally:
        db.close()
        
        
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python importar_fatura.py <caminho_do_pdf>")
        print("Exemplo: python importar_fatura.py ../data/fatura_junho.pdf")
        sys.exit(1)

    caminho = sys.argv[1]
    importar(caminho)