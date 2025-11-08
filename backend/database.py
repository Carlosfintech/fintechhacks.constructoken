"""
Base de Datos Simulada para el Prototipo
En producción, reemplazar con PostgreSQL + SQLAlchemy
"""

from typing import Dict, List, Optional
from datetime import datetime
from models import ProjectState

# ============================================================================
# ALMACENAMIENTO EN MEMORIA (PROTOTIPO)
# ============================================================================

# Simulación simple con diccionario en memoria
# En producción, usar PostgreSQL con SQLAlchemy
projects_db: Dict[str, ProjectState] = {}

# ============================================================================
# OPERACIONES CRUD
# ============================================================================

def save_project(project: ProjectState) -> ProjectState:
    """
    Guarda o actualiza un proyecto
    
    Args:
        project: Estado del proyecto a guardar
    
    Returns:
        El proyecto guardado
    """
    project.updated_at = datetime.now()
    projects_db[project.project_id] = project
    return project


def get_project(project_id: str) -> Optional[ProjectState]:
    """
    Obtiene un proyecto por ID
    
    Args:
        project_id: ID del proyecto a buscar
    
    Returns:
        El proyecto si existe, None si no
    """
    return projects_db.get(project_id)


def get_all_projects() -> List[ProjectState]:
    """
    Obtiene todos los proyectos
    
    Returns:
        Lista de todos los proyectos
    """
    return list(projects_db.values())


def delete_project(project_id: str) -> bool:
    """
    Elimina un proyecto
    
    Args:
        project_id: ID del proyecto a eliminar
    
    Returns:
        True si se eliminó, False si no existía
    """
    if project_id in projects_db:
        del projects_db[project_id]
        return True
    return False


# ============================================================================
# OPERACIONES DE NEGOCIO
# ============================================================================

def update_project_payment(project_id: str, payment_amount: int) -> Optional[ProjectState]:
    """
    Actualiza el contador de pagos de un proyecto
    
    Args:
        project_id: ID del proyecto
        payment_amount: Monto del pago recibido
    
    Returns:
        El proyecto actualizado, o None si no existe
    """
    project = get_project(project_id)
    if project:
        project.payments_received += 1
        project.amount_funded += payment_amount
        project.updated_at = datetime.now()
        
        # Actualizar status si se completaron todos los pagos
        if project.payments_received >= project.total_payments:
            project.status = "completed"
        
        save_project(project)
    
    return project


def mark_bnpl_triggered(project_id: str, bnpl_grant_id: str) -> Optional[ProjectState]:
    """
    Marca que el BNPL fue activado para un proyecto
    
    Args:
        project_id: ID del proyecto
        bnpl_grant_id: ID del grant de recuperación BNPL
    
    Returns:
        El proyecto actualizado, o None si no existe
    """
    project = get_project(project_id)
    if project:
        project.bnpl_triggered = True
        project.bnpl_grant_id = bnpl_grant_id
        project.status = "bnpl_activated"
        project.updated_at = datetime.now()
        save_project(project)
    
    return project


def find_project_by_incoming_payment(incoming_payment_id: str) -> Optional[ProjectState]:
    """
    Busca un proyecto por su incoming_payment_id
    
    Args:
        incoming_payment_id: ID del incoming payment a buscar
    
    Returns:
        El proyecto asociado, o None si no se encuentra
    """
    for project in projects_db.values():
        if project.incoming_payment_id == incoming_payment_id:
            return project
    return None


def get_projects_by_user(user_id: str) -> List[ProjectState]:
    """
    Obtiene todos los proyectos de un usuario
    
    Args:
        user_id: ID del usuario
    
    Returns:
        Lista de proyectos del usuario
    """
    return [
        project for project in projects_db.values()
        if project.user_id == user_id
    ]


def get_projects_by_status(status: str) -> List[ProjectState]:
    """
    Obtiene todos los proyectos con un status específico
    
    Args:
        status: Status a filtrar (pending, funding, completed, bnpl_activated)
    
    Returns:
        Lista de proyectos con ese status
    """
    return [
        project for project in projects_db.values()
        if project.status == status
    ]


def get_active_bnpl_projects() -> List[ProjectState]:
    """
    Obtiene todos los proyectos con BNPL activado
    
    Returns:
        Lista de proyectos con BNPL
    """
    return [
        project for project in projects_db.values()
        if project.bnpl_triggered
    ]


# ============================================================================
# ESTADÍSTICAS
# ============================================================================

def get_stats() -> dict:
    """
    Obtiene estadísticas generales de los proyectos
    
    Returns:
        Diccionario con estadísticas
    """
    projects = get_all_projects()
    
    total_amount_funded = sum(p.amount_funded for p in projects)
    total_bnpl_amount = sum(
        20000 for p in projects if p.bnpl_triggered  # $200 MXN en centavos
    )
    
    return {
        "total_projects": len(projects),
        "active_projects": len([p for p in projects if p.status in ["funding", "bnpl_activated"]]),
        "completed_projects": len([p for p in projects if p.status == "completed"]),
        "bnpl_projects": len([p for p in projects if p.bnpl_triggered]),
        "total_amount_funded": total_amount_funded,
        "total_bnpl_amount": total_bnpl_amount,
        "average_payments_per_project": (
            sum(p.payments_received for p in projects) / len(projects)
            if projects else 0
        )
    }


# ============================================================================
# UTILIDADES DE DEBUG
# ============================================================================

def print_all_projects():
    """Imprime todos los proyectos (para debug)"""
    projects = get_all_projects()
    
    if not projects:
        print("No hay proyectos en la base de datos")
        return
    
    print(f"\n{'='*80}")
    print(f"PROYECTOS EN LA BASE DE DATOS ({len(projects)} total)")
    print(f"{'='*80}\n")
    
    for project in projects:
        print(f"📋 {project.project_id}")
        print(f"   Usuario: {project.user_id}")
        print(f"   Status: {project.status}")
        print(f"   Pagos: {project.payments_received}/{project.total_payments}")
        print(f"   Fondeado: ${project.amount_funded/100:.2f} MXN / ${project.stage_amount/100:.2f} MXN")
        print(f"   BNPL: {'✅ Activado' if project.bnpl_triggered else '❌ No activado'}")
        print(f"   Creado: {project.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Actualizado: {project.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print()


def clear_database():
    """Limpia toda la base de datos (para testing)"""
    global projects_db
    projects_db = {}
    print("✅ Base de datos limpiada")


# ============================================================================
# INICIALIZACIÓN
# ============================================================================

def init_database():
    """
    Inicializa la base de datos
    
    En un sistema real, esto ejecutaría las migraciones de Alembic
    y verificaría la conexión a PostgreSQL
    """
    global projects_db
    projects_db = {}
    print("✅ Base de datos inicializada (modo en memoria)")


# Auto-inicializar al importar
if __name__ != "__main__":
    init_database()


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    # Pruebas básicas
    print("Ejecutando pruebas de la base de datos...\n")
    
    from models import ProjectState
    
    # Crear proyecto de prueba
    project = ProjectState(
        project_id="test_001",
        user_id="user_001",
        stage_amount=100000,
        payment_amount=10000,
        total_payments=10,
        user_qualifies_for_bnpl=True
    )
    
    save_project(project)
    print(f"✅ Proyecto creado: {project.project_id}")
    
    # Simular pagos
    for i in range(8):
        update_project_payment("test_001", 10000)
        print(f"✅ Pago {i+1} registrado")
    
    # Activar BNPL
    mark_bnpl_triggered("test_001", "grant_recovery_001")
    print("✅ BNPL activado")
    
    # Mostrar estadísticas
    stats = get_stats()
    print("\n📊 Estadísticas:")
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Mostrar todos los proyectos
    print_all_projects()
    
    # Limpiar
    clear_database()
    
    print("\n✅ Todas las pruebas pasaron correctamente")
