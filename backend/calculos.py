from dataclasses import replace
from datetime import date, datetime
from sqlalchemy.orm import Session
from database import Receita, DespesaFixa, Divida, Gasto, Configuracao

# Funções aux de Data
def dias_restantes_mes(hoje: date = None) -> int:
    if hoje is None:
        hoje = date.today()
    ultimo_dia = date(hoje.year, hoje.month + 1, 1) - replace(days=1)
    from datetime import timedelta
    ultimo_dia = ultimo_dia - timedelta(days=1)
    return (ultimo_dia.day - hoje.day + 1)

def ultimo_dia_mes(hoje: date = None) -> int:
    if hoje is None:
        hoje = date.today()
    proximo_mes = date(hoje.year, hoje.month + 1, 1) if hoje.month < 12 else date(hoje.year + 1, 1, 1)
    from datetime import timedelta
    return (proximo_mes - timedelta(days=1)).day

# Busca de COnfiguração
def get_config(db: Session, chave: str, default: float = 0.0) -> float:
    config = db.query(Configuracao).filter(Configuracao.chave == chave).first()
    if config:
        try:
            return float(config.valor)
        except:
            return default
    return default

# Cálculo do Resumo Financeiro
def calcular_resumo(db: Session) -> dict:
    hoje = date.today()

    # Receitas ativas
    receitas = db.query(Receita).filter(Receita.ativo == True).all()
    total_receitas = sum(r.valor for r in receitas)

    # receitas fixas ativas
    despesas = db.query(DespesaFixa).filter(DespesaFixa.ativo == True).all()
    total_despesas_fixas = sum(d.valor for d in despesas)

    # parcelas do mês (dívidas ativas)
    dividas = db.query(Divida).filter(Divida.ativo == True).all()
    total_parcelas_mes = sum(d.valor_parcela for d in dividas)

    # total de dividas (saldo devedor restante)
    total_dividas = sum(
        d.valor_parcela * (d.parcelas_total - d.parcelas_pagas)
        for d in dividas
    )

    # Reserva para cartão
    reserva_cartao = get_config(db, "reserva_cartao", 0.0)

    # Saldo disponível no mês
    saldo_disponivel = total_receitas - total_despesas_fixas - total_parcelas_mes - reserva_cartao

    # Gastos já lançados no mês atual
    primeiro_dia_mes = hoje.replace(day=1)
    gastos_mes = db.query(Gasto).filter(
        Gasto.data >= primeiro_dia_mes,
        Gasto.data <= hoje
    ).all()
    total_gasto_mes = sum(g.valor for g in gastos_mes)

    # Saldo restante e orçamento diário
    saldo_restante = max(0.0, saldo_disponivel - total_gasto_mes)
    dias_restantes = dias_restantes_mes(hoje)
    orcamento_diario = saldo_restante / dias_restantes if dias_restantes > 0 else 0.0

    # Gastos de hoje
    gastos_hoje = sum(g.valor for g in gastos_mes if g.data == hoje)
    pode_gastar_hoje = max(0.0, orcamento_diario - gastos_hoje)

    return {
        "total_receitas":       round(total_receitas, 2),
        "total_despesas_fixas": round(total_despesas_fixas, 2),
        "total_parcelas_mes":   round(total_parcelas_mes, 2),
        "reserva_cartao":       round(reserva_cartao, 2),
        "saldo_disponivel":     round(saldo_disponivel, 2),
        "total_gasto_mes":      round(total_gasto_mes, 2),
        "saldo_restante":       round(saldo_restante, 2),
        "orcamento_diario":     round(orcamento_diario, 2),
        "pode_gastar_hoje":     round(pode_gastar_hoje, 2),
        "total_dividas":        round(total_dividas, 2),
        "dias_restantes_mes":   dias_restantes,
    }

# Calendário do mês com orçamento por dia
def calcular_calendario(db: Session) -> list:
    hoje = date.today()
    resumo = calcular_resumo(db)
    saldo_restante = resumo["saldo_restante"]
    ultimo = ultimo_dia_mes(hoje)

    calendario = []
    for dia in range(hoje.day, ultimo + 1):
        data_dia = hoje.replace(day=dia)
        dias_a_partir = ultimo - dia + 1
        orc_dia = round(saldo_restante / dias_a_partir, 2) if dias_a_partir > 0 else 0.0

        gastos_dia = db.query(Gasto).filter(Gasto.data == data_dia).all()
        gasto_dia = sum(g.valor for g in gastos_dia)

        calendario.append({
            "dia":          dia,
            "data":         data_dia.isoformat(),
            "orcamento":    orc_dia,
            "gasto":        round(gasto_dia, 2),
            "saldo_dia":    round(orc_dia - gasto_dia, 2),
            "eh_hoje":      dia == hoje.day,
        })

        saldo_restante = max(0.0, saldo_restante - orc_dia)

    return calendario