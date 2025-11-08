#!/usr/bin/env python3
"""
Script de Demostración Completo - Constructoken Hackathon
Simula el flujo completo de pagos recurrentes con BNPL
"""

import requests
import json
import time
from typing import Dict, Any

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

BACKEND_URL = "http://localhost:8000"
RAFIKI_ADMIN_URL = "http://localhost:3001/graphql"

# Colores para output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text: str):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_success(text: str):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_info(text: str):
    print(f"{Colors.OKBLUE}ℹ️  {text}{Colors.ENDC}")

def print_warning(text: str):
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

def print_error(text: str):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def print_step(step: int, text: str):
    print(f"\n{Colors.OKCYAN}{Colors.BOLD}PASO {step}: {text}{Colors.ENDC}")

# ============================================================================
# FUNCIONES DE DEMO
# ============================================================================

def check_services():
    """Verifica que todos los servicios estén corriendo"""
    print_header("VERIFICANDO SERVICIOS")
    
    services = {
        "Backend FastAPI": BACKEND_URL,
        "Rafiki Admin API": RAFIKI_ADMIN_URL
    }
    
    all_ok = True
    
    for name, url in services.items():
        try:
            if "graphql" in url:
                response = requests.post(
                    url,
                    json={"query": "{ __typename }"},
                    timeout=5
                )
            else:
                response = requests.get(f"{url}/health", timeout=5)
            
            if response.status_code == 200:
                print_success(f"{name}: OK")
            else:
                print_error(f"{name}: Responde pero con error")
                all_ok = False
        except requests.exceptions.RequestException:
            print_error(f"{name}: NO RESPONDE")
            all_ok = False
    
    if not all_ok:
        print_error("\n⚠️  Algunos servicios no están disponibles")
        print_info("Asegúrate de que:")
        print_info("  1. Rafiki esté corriendo: docker ps")
        print_info("  2. FastAPI esté corriendo: python main.py")
        return False
    
    print_success("\n✅ Todos los servicios están operativos")
    return True


def demo_case_a_bnpl():
    """
    CASO A: Usuario calificado para BNPL
    Simula el flujo completo donde el BNPL se activa en el 8º pago
    """
    print_header("CASO A: FLUJO CON BNPL (Usuario Calificado)")
    
    project_id = "proyecto_001"
    user_id = "usuario_migrante_001"
    
    # PASO 1: Iniciar financiamiento
    print_step(1, "Iniciar Financiamiento del Proyecto")
    print_info(f"Proyecto ID: {project_id}")
    print_info(f"Usuario ID: {user_id}")
    print_info("Monto total: $1,000 MXN")
    print_info("Pagos: 10 × $100 MXN")
    print_info("Usuario: CALIFICA para BNPL ✓")
    
    response = requests.post(
        f"{BACKEND_URL}/start-project-funding",
        json={
            "project_id": project_id,
            "user_id": user_id,
            "stage_amount": 100000,  # $1000 MXN en centavos
            "payment_amount": 10000,  # $100 MXN en centavos
            "total_payments": 10,
            "user_qualifies_for_bnpl": True  # ← CLAVE: Usuario califica
        }
    )
    
    if response.status_code != 200:
        print_error(f"Error al iniciar financiamiento: {response.text}")
        return
    
    data = response.json()
    print_success("Financiamiento iniciado")
    print_info(f"Grant ID: {data['grant_id']}")
    print_info(f"Incoming Payment ID: {data['incoming_payment_id']}")
    
    time.sleep(2)
    
    # PASO 2: Ejecutar pagos 1-7 (normales)
    print_step(2, "Ejecutando Pagos 1-7 (Normales)")
    
    for i in range(1, 8):
        print(f"\n💳 Ejecutando Pago {i}/10...")
        
        response = requests.post(
            f"{BACKEND_URL}/execute-payment/{project_id}"
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Pago {i} completado")
            print_info(f"Progreso: {data['payments_received']}/{data['total_payments']}")
            print_info(f"Fondeado: ${data['amount_funded']/100:.2f} MXN")
        else:
            print_error(f"Error en pago {i}: {response.text}")
            return
        
        time.sleep(1)  # Pausa para simular tiempo entre pagos
    
    # PASO 3: Ejecutar pago 8 - ¡TRIGGER DE BNPL!
    print_step(3, "Ejecutando Pago 8 - ¡ACTIVACIÓN DE BNPL!")
    print_warning("⚡ Este pago debería disparar la lógica de BNPL")
    
    response = requests.post(
        f"{BACKEND_URL}/execute-payment/{project_id}"
    )
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Pago 8 completado")
        print_info(f"Progreso: {data['payments_received']}/{data['total_payments']}")
        print_info(f"Fondeado: ${data['amount_funded']/100:.2f} MXN")
    else:
        print_error(f"Error en pago 8: {response.text}")
        return
    
    time.sleep(2)  # Dar tiempo a que el webhook procese
    
    # PASO 4: Verificar que el BNPL se activó
    print_step(4, "Verificar Estado del Proyecto")
    
    response = requests.get(f"{BACKEND_URL}/project-status/{project_id}")
    
    if response.status_code == 200:
        project = response.json()
        
        print_success("Estado del proyecto obtenido")
        print("\n" + "="*60)
        print(f"📊 ESTADO DEL PROYECTO {project_id}")
        print("="*60)
        print(f"Status: {project['status']}")
        print(f"Pagos recibidos: {project['payments_received']}/{project['total_payments']}")
        print(f"Monto fondeado: ${project['amount_funded']/100:.2f} MXN")
        print(f"Porcentaje: {project['funding_percentage']:.1f}%")
        print(f"BNPL activado: {'✅ SÍ' if project['bnpl_triggered'] else '❌ NO'}")
        print("="*60 + "\n")
        
        if project['bnpl_triggered']:
            print_success("🎉 ¡BNPL ACTIVADO EXITOSAMENTE!")
            print_info("El marketplace financió los $200 MXN restantes")
            print_info("El proyecto está ahora 100% fondeado")
            print_info("Los pagos 9 y 10 irán al marketplace para recuperación")
        else:
            print_warning("BNPL NO se activó (revisar logs)")
    else:
        print_error(f"Error al obtener estado: {response.text}")
    
    # PASO 5: Resumen final
    print_step(5, "Resumen de la Demostración")
    
    print("\n" + "="*60)
    print(f"{Colors.BOLD}RESUMEN DEL FLUJO BNPL{Colors.ENDC}")
    print("="*60)
    print(f"1. Usuario realizó: 8 pagos × $100 = $800 MXN")
    print(f"2. Marketplace financió: $200 MXN (BNPL)")
    print(f"3. Proyecto fondeado: $1,000 MXN (100%)")
    print(f"4. Grant original: REVOCADO ✓")
    print(f"5. Nuevo grant: Usuario → Marketplace (2 pagos pendientes)")
    print("="*60 + "\n")
    
    print_success("✅ Demo Caso A completada exitosamente!")


def demo_case_b_no_bnpl():
    """
    CASO B: Usuario NO calificado para BNPL
    Simula el flujo normal donde todos los 10 pagos van al receptor
    """
    print_header("CASO B: FLUJO SIN BNPL (Usuario No Calificado)")
    
    project_id = "proyecto_002"
    user_id = "usuario_migrante_002"
    
    # PASO 1: Iniciar financiamiento
    print_step(1, "Iniciar Financiamiento del Proyecto")
    print_info(f"Proyecto ID: {project_id}")
    print_info(f"Usuario ID: {user_id}")
    print_info("Monto total: $1,000 MXN")
    print_info("Pagos: 10 × $100 MXN")
    print_warning("Usuario: NO califica para BNPL ✗")
    
    response = requests.post(
        f"{BACKEND_URL}/start-project-funding",
        json={
            "project_id": project_id,
            "user_id": user_id,
            "stage_amount": 100000,
            "payment_amount": 10000,
            "total_payments": 10,
            "user_qualifies_for_bnpl": False  # ← CLAVE: Usuario NO califica
        }
    )
    
    if response.status_code != 200:
        print_error(f"Error al iniciar financiamiento: {response.text}")
        return
    
    data = response.json()
    print_success("Financiamiento iniciado")
    print_info(f"Grant ID: {data['grant_id']}")
    
    time.sleep(2)
    
    # PASO 2: Ejecutar todos los pagos (1-10)
    print_step(2, "Ejecutando Pagos 1-10 (Flujo Normal)")
    
    for i in range(1, 11):
        print(f"\n💳 Ejecutando Pago {i}/10...")
        
        response = requests.post(
            f"{BACKEND_URL}/execute-payment/{project_id}"
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Pago {i} completado")
            print_info(f"Progreso: {data['payments_received']}/{data['total_payments']}")
            print_info(f"Fondeado: ${data['amount_funded']/100:.2f} MXN")
        else:
            print_error(f"Error en pago {i}: {response.text}")
            return
        
        # En el pago 8, verificar que NO se active BNPL
        if i == 8:
            print_info("⏸️  Verificando que BNPL NO se active...")
            time.sleep(1)
        
        time.sleep(1)
    
    # PASO 3: Verificar estado final
    print_step(3, "Verificar Estado Final del Proyecto")
    
    response = requests.get(f"{BACKEND_URL}/project-status/{project_id}")
    
    if response.status_code == 200:
        project = response.json()
        
        print_success("Estado del proyecto obtenido")
        print("\n" + "="*60)
        print(f"📊 ESTADO DEL PROYECTO {project_id}")
        print("="*60)
        print(f"Status: {project['status']}")
        print(f"Pagos recibidos: {project['payments_received']}/{project['total_payments']}")
        print(f"Monto fondeado: ${project['amount_funded']/100:.2f} MXN")
        print(f"Porcentaje: {project['funding_percentage']:.1f}%")
        print(f"BNPL activado: {'✅ SÍ' if project['bnpl_triggered'] else '❌ NO'}")
        print("="*60 + "\n")
        
        if not project['bnpl_triggered']:
            print_success("✓ Flujo normal ejecutado correctamente")
            print_info("Todos los pagos fueron al receptor (FINSUS)")
            print_info("No se activó BNPL como era esperado")
        else:
            print_warning("⚠️  BNPL se activó cuando NO debería (error)")
    else:
        print_error(f"Error al obtener estado: {response.text}")
    
    # PASO 4: Resumen final
    print_step(4, "Resumen de la Demostración")
    
    print("\n" + "="*60)
    print(f"{Colors.BOLD}RESUMEN DEL FLUJO NORMAL{Colors.ENDC}")
    print("="*60)
    print(f"1. Usuario realizó: 10 pagos × $100 = $1,000 MXN")
    print(f"2. Todos los pagos fueron a: Receptor (FINSUS)")
    print(f"3. Proyecto fondeado: $1,000 MXN (100%)")
    print(f"4. BNPL: NO ACTIVADO (correcto)")
    print("="*60 + "\n")
    
    print_success("✅ Demo Caso B completada exitosamente!")


def list_all_projects():
    """Lista todos los proyectos creados"""
    print_header("LISTADO DE PROYECTOS")
    
    response = requests.get(f"{BACKEND_URL}/projects")
    
    if response.status_code == 200:
        data = response.json()
        
        print(f"\n📋 Total de proyectos: {data['total']}\n")
        
        if data['total'] == 0:
            print_info("No hay proyectos creados aún")
            return
        
        for proj in data['projects']:
            status_emoji = "🟢" if proj['status'] == "completed" else "🔵"
            bnpl_emoji = "💰" if proj['bnpl_triggered'] else "📊"
            
            print(f"{status_emoji} {proj['project_id']}")
            print(f"   Status: {proj['status']}")
            print(f"   Pagos: {proj['payments_received']}/{proj['total_payments']}")
            print(f"   BNPL: {bnpl_emoji} {'Activado' if proj['bnpl_triggered'] else 'No activado'}")
            print()
    else:
        print_error(f"Error al listar proyectos: {response.text}")


# ============================================================================
# MENÚ PRINCIPAL
# ============================================================================

def show_menu():
    """Muestra el menú principal"""
    print("\n" + "="*60)
    print(f"{Colors.BOLD}DEMOSTRACIÓN CONSTRUCTOKEN - HACKATHON INTERLEDGER{Colors.ENDC}")
    print("="*60)
    print("\nSelecciona una opción:\n")
    print("1. Verificar servicios")
    print("2. Demo Caso A: Flujo con BNPL (Usuario calificado)")
    print("3. Demo Caso B: Flujo sin BNPL (Usuario no calificado)")
    print("4. Demo Completo (Ambos casos)")
    print("5. Listar todos los proyectos")
    print("0. Salir")
    print("\n" + "="*60)


def main():
    """Función principal"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║                                                            ║")
    print("║          CONSTRUCTOKEN - PROTOTIPO HACKATHON              ║")
    print("║         Pagos Recurrentes Condicionales con BNPL          ║")
    print("║                                                            ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}\n")
    
    while True:
        show_menu()
        
        try:
            choice = input(f"\n{Colors.OKCYAN}Ingresa tu opción: {Colors.ENDC}")
            
            if choice == "0":
                print(f"\n{Colors.OKGREEN}👋 ¡Hasta luego!{Colors.ENDC}\n")
                break
            elif choice == "1":
                check_services()
            elif choice == "2":
                if check_services():
                    demo_case_a_bnpl()
            elif choice == "3":
                if check_services():
                    demo_case_b_no_bnpl()
            elif choice == "4":
                if check_services():
                    demo_case_a_bnpl()
                    input(f"\n{Colors.OKCYAN}Presiona Enter para continuar con Caso B...{Colors.ENDC}")
                    demo_case_b_no_bnpl()
            elif choice == "5":
                list_all_projects()
            else:
                print_warning("Opción no válida")
        
        except KeyboardInterrupt:
            print(f"\n\n{Colors.OKGREEN}👋 ¡Hasta luego!{Colors.ENDC}\n")
            break
        except Exception as e:
            print_error(f"Error: {str(e)}")
        
        input(f"\n{Colors.OKCYAN}Presiona Enter para continuar...{Colors.ENDC}")


if __name__ == "__main__":
    main()
