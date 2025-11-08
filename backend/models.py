"""
Modelos de Datos para Constructoken Backend
Usando Pydantic para validación
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

# ============================================================================
# MODELOS DE REQUEST
# ============================================================================

class StartFundingRequest(BaseModel):
    """
    Request para iniciar el financiamiento de un proyecto
    
    Este es el modelo que recibe el endpoint /start-project-funding
    """
    project_id: str = Field(..., description="ID único del proyecto")
    user_id: str = Field(..., description="ID del usuario (pagador/migrante)")
    stage_amount: int = Field(..., description="Monto total de la etapa en centavos", gt=0)
    payment_amount: int = Field(..., description="Monto de cada pago en centavos", gt=0)
    total_payments: int = Field(..., description="Número total de pagos", gt=0)
    user_qualifies_for_bnpl: bool = Field(
        default=False,
        description="Si el usuario califica para BNPL (determina Caso A vs Caso B)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "project_id": "proyecto_001",
                "user_id": "migrante_001",
                "stage_amount": 100000,  # $1,000 MXN
                "payment_amount": 10000,  # $100 MXN
                "total_payments": 10,
                "user_qualifies_for_bnpl": True
            }
        }


class ExecutePaymentRequest(BaseModel):
    """
    Request para ejecutar un pago individual (opcional)
    
    En un sistema real, esto sería automático vía grants
    """
    project_id: str = Field(..., description="ID del proyecto")


# ============================================================================
# MODELOS DE RESPONSE
# ============================================================================

class StartFundingResponse(BaseModel):
    """
    Response del inicio de financiamiento
    """
    success: bool = Field(..., description="Si la operación fue exitosa")
    message: str = Field(..., description="Mensaje descriptivo")
    project_id: str = Field(..., description="ID del proyecto")
    grant_id: Optional[str] = Field(None, description="ID del grant creado")
    incoming_payment_id: Optional[str] = Field(None, description="ID del incoming payment")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Financiamiento iniciado correctamente",
                "project_id": "proyecto_001",
                "grant_id": "grant_proyecto_001",
                "incoming_payment_id": "inc_pay_abc123"
            }
        }


class PaymentStatusResponse(BaseModel):
    """
    Response del estado de un pago
    """
    success: bool
    payment_id: Optional[str] = None
    payments_received: int
    total_payments: int
    amount_funded: int
    message: str


class ProjectStatusResponse(BaseModel):
    """
    Response del estado de un proyecto
    """
    project_id: str
    user_id: str
    status: str
    payments_received: int
    total_payments: int
    amount_funded: int
    stage_amount: int
    funding_percentage: float
    bnpl_triggered: bool
    user_qualifies_for_bnpl: bool
    created_at: str
    updated_at: str


# ============================================================================
# MODELOS DE WEBHOOK
# ============================================================================

class WebhookEvent(BaseModel):
    """
    Evento de webhook desde Rafiki
    
    Este modelo representa los webhooks que Rafiki envía a nuestro endpoint
    """
    id: str = Field(..., description="ID único del evento")
    type: Literal[
        "incoming_payment.created",
        "incoming_payment.completed",
        "incoming_payment.expired",
        "outgoing_payment.created",
        "outgoing_payment.completed",
        "outgoing_payment.failed"
    ] = Field(..., description="Tipo de evento")
    data: dict = Field(..., description="Datos del evento")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "evt_abc123",
                "type": "incoming_payment.completed",
                "data": {
                    "id": "inc_pay_xyz789",
                    "walletAddressId": "wlt_123",
                    "state": "COMPLETED",
                    "incomingAmount": {
                        "value": "10000",
                        "assetCode": "MXN",
                        "assetScale": 2
                    },
                    "receivedAmount": {
                        "value": "10000",
                        "assetCode": "MXN",
                        "assetScale": 2
                    }
                }
            }
        }


# ============================================================================
# MODELOS DE ESTADO DEL PROYECTO
# ============================================================================

class ProjectState(BaseModel):
    """
    Estado completo de un proyecto en nuestra base de datos
    
    Este es el modelo principal que representa un proyecto y su estado
    """
    # Identificación
    project_id: str = Field(..., description="ID único del proyecto")
    user_id: str = Field(..., description="ID del usuario (pagador)")
    
    # Configuración del proyecto
    stage_amount: int = Field(..., description="Monto total de la etapa (centavos)", gt=0)
    payment_amount: int = Field(..., description="Monto de cada pago (centavos)", gt=0)
    total_payments: int = Field(..., description="Total de pagos a realizar", gt=0)
    
    # Estado de los pagos
    payments_received: int = Field(default=0, description="Pagos recibidos hasta ahora", ge=0)
    amount_funded: int = Field(default=0, description="Monto total fondeado (centavos)", ge=0)
    
    # Referencias a Rafiki
    grant_id: Optional[str] = Field(None, description="ID del grant en Rafiki")
    incoming_payment_id: Optional[str] = Field(None, description="ID del incoming payment")
    
    # Estado de BNPL
    bnpl_triggered: bool = Field(default=False, description="Si el BNPL fue activado")
    bnpl_grant_id: Optional[str] = Field(None, description="ID del grant de recuperación BNPL")
    user_qualifies_for_bnpl: bool = Field(default=False, description="Si el usuario califica")
    
    # Estado general
    status: Literal["pending", "funding", "completed", "bnpl_activated"] = Field(
        default="pending",
        description="Estado actual del proyecto"
    )
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now, description="Fecha de creación")
    updated_at: datetime = Field(default_factory=datetime.now, description="Última actualización")
    
    class Config:
        json_schema_extra = {
            "example": {
                "project_id": "proyecto_001",
                "user_id": "migrante_001",
                "stage_amount": 100000,
                "payment_amount": 10000,
                "total_payments": 10,
                "payments_received": 8,
                "amount_funded": 80000,
                "grant_id": "grant_abc123",
                "incoming_payment_id": "inc_pay_xyz789",
                "bnpl_triggered": True,
                "bnpl_grant_id": "grant_recovery_def456",
                "user_qualifies_for_bnpl": True,
                "status": "bnpl_activated",
                "created_at": "2025-11-08T10:00:00Z",
                "updated_at": "2025-11-08T10:30:00Z"
            }
        }


# ============================================================================
# MODELOS DE RAFIKI (para referencia)
# ============================================================================

class RafikiAmount(BaseModel):
    """Modelo de monto en Rafiki"""
    value: str = Field(..., description="Valor en la unidad más pequeña (string)")
    assetCode: str = Field(..., description="Código de la moneda")
    assetScale: int = Field(..., description="Número de decimales")


class RafikiIncomingPayment(BaseModel):
    """Modelo de IncomingPayment de Rafiki"""
    id: str
    walletAddressId: str
    state: str
    incomingAmount: Optional[RafikiAmount] = None
    receivedAmount: Optional[RafikiAmount] = None
    metadata: Optional[dict] = None
    createdAt: str
    expiresAt: Optional[str] = None


class RafikiOutgoingPayment(BaseModel):
    """Modelo de OutgoingPayment de Rafiki"""
    id: str
    walletAddressId: str
    state: str
    receiveAmount: Optional[RafikiAmount] = None
    sentAmount: Optional[RafikiAmount] = None
    metadata: Optional[dict] = None
    createdAt: str


class RafikiQuote(BaseModel):
    """Modelo de Quote de Rafiki"""
    id: str
    walletAddressId: str
    receiver: str
    sendAmount: RafikiAmount
    receiveAmount: RafikiAmount
    createdAt: str
    expiresAt: str


class RafikiGrant(BaseModel):
    """Modelo de Grant de Rafiki"""
    id: str
    state: str
    access: dict
    startAt: Optional[str] = None
    finishAt: Optional[str] = None


# ============================================================================
# UTILIDADES
# ============================================================================

def format_amount(amount_cents: int, decimals: int = 2) -> str:
    """
    Formatea un monto en centavos a un string legible
    
    Args:
        amount_cents: Monto en centavos
        decimals: Número de decimales a mostrar
    
    Returns:
        String formateado (ej. "$100.00")
    """
    divisor = 10 ** decimals
    amount = amount_cents / divisor
    return f"${amount:.{decimals}f}"


def parse_amount(amount_str: str, decimals: int = 2) -> int:
    """
    Parsea un string de monto a centavos
    
    Args:
        amount_str: String del monto (ej. "100.00" o "$100.00")
        decimals: Número de decimales
    
    Returns:
        Monto en centavos (int)
    """
    # Remover símbolo de moneda si existe
    clean_str = amount_str.replace("$", "").replace(",", "").strip()
    
    # Convertir a float y luego a centavos
    amount = float(clean_str)
    multiplier = 10 ** decimals
    return int(amount * multiplier)


# ============================================================================
# VALIDACIONES
# ============================================================================

def validate_project_amounts(project: ProjectState) -> bool:
    """
    Valida que los montos de un proyecto sean consistentes
    
    Args:
        project: Proyecto a validar
    
    Returns:
        True si es válido, False si no
    """
    # El monto total debe ser igual a payment_amount × total_payments
    expected_total = project.payment_amount * project.total_payments
    if project.stage_amount != expected_total:
        return False
    
    # Los pagos recibidos no pueden exceder el total
    if project.payments_received > project.total_payments:
        return False
    
    # El monto fondeado no puede exceder el stage_amount
    if project.amount_funded > project.stage_amount:
        return False
    
    return True


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    # Pruebas básicas de los modelos
    print("Ejecutando pruebas de modelos...\n")
    
    # Test 1: Crear un proyecto válido
    project = ProjectState(
        project_id="test_001",
        user_id="user_001",
        stage_amount=100000,
        payment_amount=10000,
        total_payments=10,
        user_qualifies_for_bnpl=True
    )
    
    print("✅ Proyecto creado:")
    print(f"   ID: {project.project_id}")
    print(f"   Monto total: {format_amount(project.stage_amount)} MXN")
    print(f"   Por pago: {format_amount(project.payment_amount)} MXN")
    
    # Test 2: Validar montos
    is_valid = validate_project_amounts(project)
    print(f"\n✅ Validación de montos: {'Válido' if is_valid else 'Inválido'}")
    
    # Test 3: Crear request
    request = StartFundingRequest(
        project_id="test_002",
        user_id="user_002",
        stage_amount=100000,
        payment_amount=10000,
        total_payments=10,
        user_qualifies_for_bnpl=False
    )
    
    print(f"\n✅ Request creado: {request.model_dump_json(indent=2)}")
    
    # Test 4: Parse/format amounts
    amount_str = "$1,250.50"
    amount_cents = parse_amount(amount_str)
    formatted = format_amount(amount_cents)
    print(f"\n✅ Conversión de montos:")
    print(f"   String: {amount_str}")
    print(f"   Centavos: {amount_cents}")
    print(f"   Formateado: {formatted}")
    
    print("\n✅ Todas las pruebas pasaron correctamente")
