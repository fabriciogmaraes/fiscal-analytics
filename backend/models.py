from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


# Schemas de Receitas
class ReceitaCreate(BaseModel):
    nome: str
    valor: float
    dia_recebimento: int
    recorrente: Optional[bool] = True
    mes_referencia: Optional[int] = None
    ano_referencia: Optional[int] = None

class ReceitaResponse(BaseModel):
    id: int
    nome: str
    valor: float
    dia_recebimento: int
    recorrente: bool
    mes_referencia: Optional[int] = None
    ano_referencia: Optional[int] = None
    ativo: bool

    model_config = {"from_attributes": True}

# Schemas de Despesas Fixas
class DespesaFixaCreate(BaseModel):
    nome: str
    valor: float
    dia_vencimento: int
    categoria: str

class DespesaFixaResponse(BaseModel):
    id: int
    nome: str
    valor: float
    dia_vencimento: int
    categoria: str
    ativo: bool

    model_config = {"from_attributes": True}

# Schemas de Dívidas
class DividaCreate(BaseModel):
    nome: str
    valor_total: float
    valor_parcela: float
    parcelas_pagas: int
    parcelas_total: int
    dia_vencimento: int
    status: Optional[str] = "em_dia"

class DividaResponse(BaseModel):
    id: int
    nome: str
    valor_total: float
    valor_parcela: float
    parcelas_pagas: int
    parcelas_total: int
    dia_vencimento: int
    status: str
    ativo: bool

    model_config = {"from_attributes": True}

# Schemas de Gastos
class GastoCreate(BaseModel):
    descricao: str
    valor: float
    data: date
    categoria: str
    eh_cartao: Optional[bool] = True

class GastoResponse(BaseModel):
    id: int
    descricao: str
    valor: float
    data: date
    categoria: str
    eh_cartao: bool
    criado_em: datetime

    model_config = {"from_attributes": True}

# Schemas de Configurações e Resumos
class ConfiguracaoCreate(BaseModel):
    chave: str
    valor: str

class ConfiguracaoResponse(BaseModel):
    id: int
    chave: str
    valor: str

    model_config = {"from_attributes": True}

class ResumoFinanceiro(BaseModel):
    total_receitas: float
    total_despesas_fixas: float
    total_parcela_mes: float
    reserva_cartao: float
    saldo_disponivel: float
    total_gasto_mes: float
    saldo_restante: float
    orcamento_diario: float
    pode_gastar_hoje: float
    total_dividas: float
    dia_restantes_mes: int