"""
Backend FastAPI para Constructoken - Prototipo Hackathon Interledger
Orquestador de pagos recurrentes condicionales con BNPL usando Rafiki
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.responses import JSONResponse
import uvicorn
from datetime import datetime
import logging

from models import (
    StartFundingRequest,
    StartFundingResponse,
    WebhookEvent,
    ProjectState
)
from rafiki_client import RafikiClient
from database import (
    save_project,
    get_project,
    update_project_payment,
    mark_bnpl_triggered
)
from config import (
    RAFIKI_CONFIG,
    PAYMENT_AMOUNT,
    TOTAL_PAYMENTS,
    BNPL_TRIGGER_PAYMENT,
    BNPL_AMOUNT
)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicializar FastAPI
app = FastAPI(
    title="Constructoken Backend",
    description="Orquestador de pagos para el prototipo de Interledger Hackathon",
    version="1.0.0"
)

# Inicializar cliente de Rafiki
rafiki = RafikiClient()

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Endpoint raíz con información del servicio"""
    return {
        "service": "Constructoken Backend",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "start_funding": "POST /start-project-funding",
            "webhook": "POST /rafiki-webhook",
            "status": "GET /project-status/{project_id}"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/start-project-funding", response_model=StartFundingResponse)
async def start_project_funding(request: StartFundingRequest):
    """
    Endpoint 1: Iniciar el financiamiento de un proyecto
    
    Este endpoint:
    1. Crea un IncomingPayment en la WalletAddress del Receptor (FINSUS)
    2. Crea un Grant de pagos recurrentes en la WalletAddress del Pagador
    3. Guarda el estado del proyecto en nuestra BD
    
    Args:
        request: Datos del proyecto y parámetros de pago
    
    Returns:
        StartFundingResponse con IDs del grant e incoming payment
    """
    logger.info(f"🚀 Iniciando financiamiento del proyecto {request.project_id}")
    
    try:
        # 1. Obtener las WalletAddress desde la config
        receptor_wallet = RAFIKI_CONFIG["wallets"]["receptor"]
        pagador_wallet = RAFIKI_CONFIG["wallets"]["pagador"]
        
        logger.info(f"   💰 Receptor: {receptor_wallet['url']}")
        logger.info(f"   💳 Pagador: {pagador_wallet['url']}")
        
        # 2. Crear IncomingPayment en la cuenta del Receptor (FINSUS)
        # Este es el "destino" al que llegarán los pagos
        logger.info("   📥 Creando IncomingPayment en Receptor...")
        
        incoming_payment = await rafiki.create_incoming_payment(
            wallet_address_id=receptor_wallet["id"],
            amount_value=request.stage_amount,  # $1000 MXN total
            asset_code="MXN",
            asset_scale=2,
            description=f"Financiamiento Proyecto {request.project_id}"
        )
        
        logger.info(f"   ✅ IncomingPayment creado: {incoming_payment['id']}")
        
        # 3. SIMULACIÓN: En un flujo real con consentimiento del usuario,
        # aquí redigiríamos al usuario a una página de autorización.
        # Para el prototipo, asumimos que el usuario ya autorizó.
        
        # 4. Crear Grant de pagos recurrentes
        # Este grant autoriza al backend a instruir pagos periódicos
        logger.info("   🔑 Creando Grant de pagos recurrentes...")
        
        # NOTA: En Rafiki, la creación de grants típicamente pasa por el
        # Auth Server con consentimiento explícito del usuario. Para el
        # prototipo, usamos la API Admin directamente.
        
        # Por ahora, guardamos la referencia al incoming payment
        # Los pagos recurrentes en Rafiki se pueden configurar de varias formas:
        # - Como un Grant con límites de tiempo/cantidad
        # - Como múltiples OutgoingPayments programados
        # - Usando la spec de Open Payments con GNAP
        
        # Para simplificar el prototipo, vamos a usar un enfoque donde
        # nuestro backend es responsable de "disparar" cada pago cuando
        # corresponda, usando el incoming payment como destino.
        
        grant_id = f"grant_{request.project_id}"  # Simulado por ahora
        
        logger.info(f"   ✅ Grant configurado: {grant_id}")
        
        # 5. Guardar el estado del proyecto
        project = ProjectState(
            project_id=request.project_id,
            user_id=request.user_id,
            stage_amount=request.stage_amount,
            payment_amount=request.payment_amount,
            total_payments=request.total_payments,
            grant_id=grant_id,
            incoming_payment_id=incoming_payment["id"],
            user_qualifies_for_bnpl=request.user_qualifies_for_bnpl,
            status="funding"
        )
        
        save_project(project)
        
        logger.info(f"✅ Proyecto {request.project_id} iniciado correctamente")
        
        return StartFundingResponse(
            success=True,
            message="Financiamiento iniciado correctamente",
            project_id=request.project_id,
            grant_id=grant_id,
            incoming_payment_id=incoming_payment["id"]
        )
    
    except Exception as e:
        logger.error(f"❌ Error al iniciar financiamiento: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/execute-payment/{project_id}")
async def execute_payment(project_id: str):
    """
    Endpoint auxiliar: Ejecutar un pago individual
    
    En un sistema real con pagos recurrentes automáticos, este endpoint
    no sería necesario. Rafiki se encargaría de ejecutar los pagos según
    el calendario. Para el prototipo, lo usamos para simular manualmente
    cada pago.
    
    Args:
        project_id: ID del proyecto
    
    Returns:
        Estado del pago ejecutado
    """
    logger.info(f"💸 Ejecutando pago para proyecto {project_id}")
    
    try:
        # 1. Obtener el estado del proyecto
        project = get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Proyecto no encontrado")
        
        # 2. Verificar si ya se completaron todos los pagos
        if project.payments_received >= project.total_payments:
            return {
                "success": False,
                "message": "Todos los pagos ya fueron ejecutados"
            }
        
        # 3. Obtener wallets
        pagador_wallet = RAFIKI_CONFIG["wallets"]["pagador"]
        receptor_wallet = RAFIKI_CONFIG["wallets"]["receptor"]
        
        # 4. Crear Quote (cotización) para el pago
        # La quote calcula el exchange rate USD -> MXN si es necesario
        logger.info("   💱 Creando Quote...")
        
        quote = await rafiki.create_quote(
            wallet_address_id=pagador_wallet["id"],
            receiver=project.incoming_payment_id,  # URL del incoming payment
            send_amount_value=project.payment_amount,  # $100 MXN
            send_asset_code="USD",  # El pagador paga en USD
            send_asset_scale=2
        )
        
        logger.info(f"   ✅ Quote creado: {quote['id']}")
        logger.info(f"      Send: ${quote['sendAmount']['value']/100} USD")
        logger.info(f"      Receive: ${quote['receiveAmount']['value']/100} MXN")
        
        # 5. Ejecutar el OutgoingPayment
        logger.info("   💳 Ejecutando OutgoingPayment...")
        
        payment = await rafiki.create_outgoing_payment(
            wallet_address_id=pagador_wallet["id"],
            quote_id=quote["id"],
            description=f"Pago {project.payments_received + 1}/{project.total_payments}"
        )
        
        logger.info(f"   ✅ Pago ejecutado: {payment['id']}")
        
        # 6. Actualizar el estado del proyecto
        # NOTA: En un sistema real, esto lo haría el webhook al recibir
        # la confirmación del pago. Aquí lo hacemos directamente.
        update_project_payment(project_id, project.payment_amount)
        
        project = get_project(project_id)
        
        logger.info(f"   📊 Estado: {project.payments_received}/{project.total_payments} pagos")
        logger.info(f"   💰 Fondeado: ${project.amount_funded/100} MXN")
        
        return {
            "success": True,
            "payment_id": payment["id"],
            "payments_received": project.payments_received,
            "total_payments": project.total_payments,
            "amount_funded": project.amount_funded,
            "message": f"Pago {project.payments_received} ejecutado exitosamente"
        }
    
    except Exception as e:
        logger.error(f"❌ Error al ejecutar pago: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/rafiki-webhook")
async def rafiki_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Endpoint 2: Webhook de Rafiki (EL MÁS IMPORTANTE)
    
    Este endpoint recibe notificaciones de Rafiki cuando ocurren eventos
    de pago. Aquí implementamos la lógica condicional del BNPL.
    
    Eventos que manejamos:
    - incoming_payment.completed: Un pago llegó al Receptor
    - outgoing_payment.completed: Un pago salió del Pagador
    
    Args:
        request: Request HTTP con el payload del webhook
        background_tasks: Para procesar en background si es necesario
    
    Returns:
        Confirmación de recepción del webhook
    """
    # 1. Parsear el webhook
    try:
        payload = await request.json()
        logger.info(f"🔔 Webhook recibido: {payload.get('type', 'unknown')}")
        
        event = WebhookEvent(**payload)
    except Exception as e:
        logger.error(f"❌ Error parseando webhook: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid webhook payload")
    
    # 2. Procesar según el tipo de evento
    if event.type == "incoming_payment.completed":
        await handle_payment_completed(event)
    elif event.type == "outgoing_payment.completed":
        logger.info(f"   ℹ️  Pago saliente completado: {event.id}")
    else:
        logger.info(f"   ℹ️  Evento ignorado: {event.type}")
    
    # 3. Responder a Rafiki que recibimos el webhook
    return {"status": "received", "event_id": event.id}


async def handle_payment_completed(event: WebhookEvent):
    """
    Maneja el evento de pago completado
    
    LÓGICA CLAVE DEL BNPL:
    - Si es el 8º pago y el usuario califica para BNPL:
      1. Revocar el grant original
      2. Financiar los $200 restantes desde Capital
      3. Crear nuevo grant para recuperación
    """
    logger.info("   💰 Procesando pago completado...")
    
    # 1. Extraer datos del evento
    payment_data = event.data
    incoming_payment_id = payment_data.get("id")
    amount = payment_data.get("incomingAmount", {}).get("value", 0)
    
    logger.info(f"      ID: {incoming_payment_id}")
    logger.info(f"      Monto: ${int(amount)/100} MXN")
    
    # 2. Buscar el proyecto asociado a este incoming payment
    project = None
    for proj in get_all_projects():
        if proj.incoming_payment_id == incoming_payment_id:
            project = proj
            break
    
    if not project:
        logger.warning(f"   ⚠️  No se encontró proyecto para payment {incoming_payment_id}")
        return
    
    logger.info(f"   📋 Proyecto: {project.project_id}")
    
    # 3. Actualizar el contador de pagos
    update_project_payment(project.project_id, int(amount))
    project = get_project(project.project_id)
    
    logger.info(f"   📊 Progreso: {project.payments_received}/{project.total_payments} pagos")
    logger.info(f"   💵 Total fondeado: ${project.amount_funded/100} MXN")
    
    # 4. 🎯 LÓGICA CONDICIONAL DEL BNPL
    if (project.payments_received == BNPL_TRIGGER_PAYMENT and 
        project.user_qualifies_for_bnpl and 
        not project.bnpl_triggered):
        
        logger.info("   🚨 ¡TRIGGER DE BNPL ACTIVADO!")
        logger.info("      El usuario ha realizado 8 pagos y califica para BNPL")
        
        # Ejecutar la lógica de BNPL en background
        await execute_bnpl_logic(project)


async def execute_bnpl_logic(project: ProjectState):
    """
    Ejecuta la lógica de BNPL (El núcleo del prototipo)
    
    Pasos:
    1. Revocar el grant original (para detener pagos 9 y 10 a FINSUS)
    2. Financiar los $200 restantes desde Capital → Receptor
    3. Crear nuevo incoming payment en Capital
    4. Crear nuevo grant para que Usuario pague a Capital
    """
    logger.info("   🏦 Ejecutando lógica BNPL...")
    
    try:
        # PASO 4.1: Revocar el Grant Original
        logger.info("      4.1 Revocando grant original...")
        
        if project.grant_id:
            success = await rafiki.revoke_grant(project.grant_id)
            if success:
                logger.info("      ✅ Grant original revocado")
            else:
                logger.error("      ❌ Error revocando grant")
        
        # PASO 4.2: Financiar desde Capital → Receptor
        logger.info("      4.2 Financiando $200 MXN desde Capital...")
        
        capital_wallet = RAFIKI_CONFIG["wallets"]["capital"]
        receptor_wallet = RAFIKI_CONFIG["wallets"]["receptor"]
        
        # Crear incoming payment en el receptor para estos $200
        bnpl_incoming = await rafiki.create_incoming_payment(
            wallet_address_id=receptor_wallet["id"],
            amount_value=BNPL_AMOUNT,  # $200 MXN
            asset_code="MXN",
            asset_scale=2,
            description=f"Financiamiento BNPL - Proyecto {project.project_id}"
        )
        
        logger.info(f"      ✅ IncomingPayment BNPL creado: {bnpl_incoming['id']}")
        
        # Crear quote para el pago desde Capital
        bnpl_quote = await rafiki.create_quote(
            wallet_address_id=capital_wallet["id"],
            receiver=bnpl_incoming["id"],
            send_amount_value=BNPL_AMOUNT,
            send_asset_code="MXN",
            send_asset_scale=2
        )
        
        logger.info(f"      ✅ Quote BNPL creado: {bnpl_quote['id']}")
        
        # Ejecutar el pago
        bnpl_payment = await rafiki.create_outgoing_payment(
            wallet_address_id=capital_wallet["id"],
            quote_id=bnpl_quote["id"],
            description=f"BNPL: Capital → Proyecto {project.project_id}"
        )
        
        logger.info(f"      ✅ Pago BNPL ejecutado: {bnpl_payment['id']}")
        logger.info(f"      💰 Proyecto fondeado al 100%!")
        
        # PASO 4.3: Crear nuevo IncomingPayment en Capital para recuperación
        logger.info("      4.3 Creando nuevo IncomingPayment en Capital...")
        
        recovery_incoming = await rafiki.create_incoming_payment(
            wallet_address_id=capital_wallet["id"],
            amount_value=BNPL_AMOUNT,  # $200 MXN a recuperar
            asset_code="MXN",
            asset_scale=2,
            description=f"Recuperación BNPL - Proyecto {project.project_id}"
        )
        
        logger.info(f"      ✅ IncomingPayment de recuperación creado: {recovery_incoming['id']}")
        
        # PASO 4.4: Crear nuevo Grant para Usuario → Capital
        # (En realidad requiere consentimiento del usuario nuevamente)
        logger.info("      4.4 Configurando nuevo Grant para recuperación...")
        
        recovery_grant_id = f"recovery_grant_{project.project_id}"
        
        logger.info(f"      ✅ Grant de recuperación configurado: {recovery_grant_id}")
        logger.info("      ℹ️  El usuario deberá autorizar 2 pagos de $100 a Marketplace")
        
        # Actualizar el estado del proyecto
        mark_bnpl_triggered(project.project_id, recovery_grant_id)
        
        logger.info("   ✅ BNPL ejecutado exitosamente!")
        logger.info("   📊 Resumen:")
        logger.info(f"      • Usuario pagó: ${project.amount_funded/100} MXN (8 pagos)")
        logger.info(f"      • Marketplace financió: ${BNPL_AMOUNT/100} MXN")
        logger.info(f"      • Proyecto 100% fondeado: ${(project.amount_funded + BNPL_AMOUNT)/100} MXN")
        logger.info(f"      • Usuario debe: ${BNPL_AMOUNT/100} MXN al Marketplace (2 pagos)")
    
    except Exception as e:
        logger.error(f"   ❌ Error en lógica BNPL: {str(e)}")
        raise


@app.get("/project-status/{project_id}")
async def get_project_status(project_id: str):
    """
    Obtiene el estado actual de un proyecto
    
    Args:
        project_id: ID del proyecto
    
    Returns:
        Estado detallado del proyecto
    """
    project = get_project(project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    
    return {
        "project_id": project.project_id,
        "user_id": project.user_id,
        "status": project.status,
        "payments_received": project.payments_received,
        "total_payments": project.total_payments,
        "amount_funded": project.amount_funded,
        "stage_amount": project.stage_amount,
        "funding_percentage": (project.amount_funded / project.stage_amount) * 100,
        "bnpl_triggered": project.bnpl_triggered,
        "user_qualifies_for_bnpl": project.user_qualifies_for_bnpl,
        "created_at": project.created_at.isoformat(),
        "updated_at": project.updated_at.isoformat()
    }


@app.get("/projects")
async def list_projects():
    """Lista todos los proyectos"""
    projects = get_all_projects()
    return {
        "total": len(projects),
        "projects": [
            {
                "project_id": p.project_id,
                "status": p.status,
                "payments_received": p.payments_received,
                "total_payments": p.total_payments,
                "bnpl_triggered": p.bnpl_triggered
            }
            for p in projects
        ]
    }


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def get_all_projects():
    """Obtiene todos los proyectos de la BD simulada"""
    from database import projects_db
    return list(projects_db.values())


@app.on_event("shutdown")
async def shutdown_event():
    """Cierra conexiones al apagar el servidor"""
    await rafiki.close()
    logger.info("🛑 Servidor apagado correctamente")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    logger.info("🚀 Iniciando Constructoken Backend...")
    logger.info(f"   📡 Rafiki Admin API: {RAFIKI_CONFIG}")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
