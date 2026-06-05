from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from datetime import date
import os

from database import get_db, criar_tabelas, Receita, DespesaFixa, Divida, Gasto, Configuracao
from models import (
    ReceitaCreate, ReceitaResponse,
    DespesaFixaCreate, DespesaFixaResponse,
    DividaCreate, DividaResponse,
    GastoCreate, GastoResponse,
    ConfiguracaoCreate, ConfiguracaoResponse,
    ResumoFinanceiro,
)
from calculos import calcular_resumo, calcular_calendario

app = FastAPI(title="Fiscal Analytics", version="1.0.0")

criar_tabelas()

# Serve os arquivos do frontend
app.mount("/static", StaticFiles(directory="../frontend"), name="static")

# Rota raiz
@app.get("/")
def root():
    return FileResponse("../frontend/index.html")

# Rotas de Receitas
@app.get("/receitas", response_model=list[ReceitaResponse])
def listar_receitas(db: Session = Depends(get_db)):
    return db.query(Receita).filter(Receita.ativo == True).all()


@app.post("/receitas", response_model=ReceitaResponse)
def criar_receita(receita: ReceitaCreate, db: Session = Depends(get_db)):
    nova = Receita(**receita.model_dump())
    db.add(nova)
    db.commit()
    db.refresh(nova)
    return nova


@app.delete("/receitas/{id}")
def deletar_receita(id: int, db: Session = Depends(get_db)):
    receita = db.query(Receita).filter(Receita.id == id).first()
    if not receita:
        raise HTTPException(status_code=404, detail="Receita não encontrada")
    receita.ativo = False
    db.commit()
    return {"ok": True}

# Rotas de Despesas Fixas
@app.get("/despesas", response_model=list[DespesaFixaResponse])
def listar_despesas(db: Session = Depends(get_db)):
    return db.query(DespesaFixa).filter(DespesaFixa.ativo == True).all()


@app.post("/despesas", response_model=DespesaFixaResponse)
def criar_despesa(despesa: DespesaFixaCreate, db: Session = Depends(get_db)):
    nova = DespesaFixa(**despesa.model_dump())
    db.add(nova)
    db.commit()
    db.refresh(nova)
    return nova


@app.delete("/despesas/{id}")
def deletar_despesa(id: int, db: Session = Depends(get_db)):
    despesa = db.query(DespesaFixa).filter(DespesaFixa.id == id).first()
    if not despesa:
        raise HTTPException(status_code=404, detail="Despesa não encontrada")
    despesa.ativo = False
    db.commit()
    return {"ok": True}

# Rotas de Dívidas
@app.get("/dividas", response_model=list[DividaResponse])
def listar_dividas(db: Session = Depends(get_db)):
    return db.query(Divida).filter(Divida.ativo == True).all()


@app.post("/dividas", response_model=DividaResponse)
def criar_divida(divida: DividaCreate, db: Session = Depends(get_db)):
    nova = Divida(**divida.model_dump())
    db.add(nova)
    db.commit()
    db.refresh(nova)
    return nova


@app.put("/dividas/{id}/parcela")
def registrar_parcela(id: int, db: Session = Depends(get_db)):
    divida = db.query(Divida).filter(Divida.id == id).first()
    if not divida:
        raise HTTPException(status_code=404, detail="Dívida não encontrada")
    if divida.parcelas_pagas < divida.parcelas_total:
        divida.parcelas_pagas += 1
    if divida.parcelas_pagas == divida.parcelas_total:
        divida.ativo = False
    db.commit()
    db.refresh(divida)
    return divida


@app.delete("/dividas/{id}")
def deletar_divida(id: int, db: Session = Depends(get_db)):
    divida = db.query(Divida).filter(Divida.id == id).first()
    if not divida:
        raise HTTPException(status_code=404, detail="Dívida não encontrada")
    divida.ativo = False
    db.commit()
    return {"ok": True}

# Rotas de Gastos
@app.get("/gastos", response_model=list[GastoResponse])
def listar_gastos(db: Session = Depends(get_db)):
    return db.query(Gasto).order_by(Gasto.data.desc()).all()


@app.get("/gastos/hoje", response_model=list[GastoResponse])
def gastos_hoje(db: Session = Depends(get_db)):
    hoje = date.today()
    return db.query(Gasto).filter(Gasto.data == hoje).all()


@app.post("/gastos", response_model=GastoResponse)
def criar_gasto(gasto: GastoCreate, db: Session = Depends(get_db)):
    novo = Gasto(**gasto.model_dump())
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo


@app.delete("/gastos/{id}")
def deletar_gasto(id: int, db: Session = Depends(get_db)):
    gasto = db.query(Gasto).filter(Gasto.id == id).first()
    if not gasto:
        raise HTTPException(status_code=404, detail="Gasto não encontrado")
    db.delete(gasto)
    db.commit()
    return {"ok": True}

# Rotas de Configurações
@app.get("/configuracoes", response_model=list[ConfiguracaoResponse])
def listar_configuracoes(db: Session = Depends(get_db)):
    return db.query(Configuracao).all()


@app.post("/configuracoes", response_model=ConfiguracaoResponse)
def salvar_configuracao(config: ConfiguracaoCreate, db: Session = Depends(get_db)):
    existente = db.query(Configuracao).filter(Configuracao.chave == config.chave).first()
    if existente:
        existente.valor = config.valor
        db.commit()
        db.refresh(existente)
        return existente
    nova = Configuracao(**config.model_dump())
    db.add(nova)
    db.commit()
    db.refresh(nova)
    return nova

# Rotas de Calculos
@app.get("/resumo")
def resumo_financeiro(db: Session = Depends(get_db)):
    return calcular_resumo(db)


@app.get("/calendario")
def calendario_mes(db: Session = Depends(get_db)):
    return calcular_calendario(db)