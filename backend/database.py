from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Date, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

DATABASE_URL = "sqlite:///./fiscal.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} 
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Receita(Base):
    __tablename__ = "receitas"

    id               = Column(Integer, primary_key=True, index=True)
    nome             = Column(String, nullable=False) #ex: "Salário", "Alguel Recebido"
    valor            = Column(Float, nullable=False)
    dia_recebimento  = Column(Integer, nullable=False) #dia do mês que a receita é recebida
    ativo            = Column(Boolean, default=True)
    criado_em        = Column(DateTime, default=datetime.utcnow)

class DespesaFixa(Base):
    __tablename__ = "despesas_fixas"

    id               = Column(Integer, primary_key=True, index=True)
    nome             = Column(String, nullable=False) #ex: "Aluguel", "Conta de Luz"
    valor            = Column(Float, nullable=False)
    dia_vencimento   = Column(Integer, nullable=False) #dia do mês que a despesa vence
    categoria        = Column(String, nullable=False) #ex: "Moradia", "Transporte", "Alimentação"
    ativo            = Column(Boolean, default=True)
    criado_em        = Column(DateTime, default=datetime.utcnow)

class Divida(Base):
    __tablename__ = "dividas"

    id               = Column(Integer, primary_key=True, index=True)
    nome             = Column(String, nullable=False)    #ex: Financiamento Apto
    valor_total      = Column(Float, nullable=False)     #valor original da dívida
    valor_parcela    = Column(Float, nullable=False)     #valor de cada parcela
    parcelas_pagas   = Column(Integer, default=0)
    parcelas_total   = Column(Integer, nullable=False)
    dia_vencimento   = Column(Integer, nullable=False)
    status           = Column(String, default="em_dia")  #em_dia ou atrasado
    ativo            = Column(Boolean, default=True)
    criado_em        = Column(DateTime, default=datetime.utcnow)

class Gasto(Base):
    __tablename__ = "gastos"

    id               = Column(Integer, primary_key=True, index=True)
    descricao        = Column(String, nullable=False) #ex: "Jantar Fora", "Cinema"
    valor            = Column(Float, nullable=False)
    data             = Column(Date, nullable=False) #data do gasto
    categoria        = Column(String, nullable=False) #ex: "Lazer", "Alimentação"
    eh_cartao        = Column(Boolean, default=True)
    criado_em        = Column(DateTime, default=datetime.utcnow)

class Configuracao(Base):
    __tablename__ = "configuracoes"

    id               = Column(Integer, primary_key=True, index=True)
    chave            = Column(String, unique=True, nullable=False) #ex: "meta_poupanca", "dia_pagamento"
    valor            = Column(String, nullable=False) #valor da configuração

def criar_tabelas():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    criar_tabelas()
    print("Banco de Dados criado com sucesso!")
    print("Tabelas: receitas, despesas_fixas, dividas, gastos, configuracoes")