# Constructoken - BNPL para Construcción

Prototipo de Buy Now Pay Later (BNPL) para proyectos de construcción utilizando Rafiki/Interledger para pagos recurrentes condicionales.

## 🎯 Concepto

Constructoken permite a migrantes financiar proyectos de construcción en México mediante pagos recurrentes en USD, con activación automática de BNPL al alcanzar el 80% del financiamiento.

### Flujo de Negocio

1. Usuario se compromete a 10 pagos de $100 MXN ($1,000 total)
2. Realiza 8 pagos exitosos ($800 fondeados)
3. **Trigger BNPL**: El marketplace financia los $200 restantes
4. Proyecto queda 100% fondeado inmediatamente
5. Usuario paga los $200 al marketplace en 2 cuotas posteriores

## 🏗️ Arquitectura

### Componentes

- **Backend (FastAPI)**: Orquestador de pagos con lógica BNPL
- **Rafiki**: Infraestructura de pagos Interledger
  - Admin API para gestión de wallets y quotes
  - Open Payments para ejecución de transacciones
  - GNAP Auth Server para autorización
  - TigerBeetle para contabilidad de alto rendimiento

### Actores

1. **Pagador** (Migrante): Realiza pagos en USD
2. **Receptor** (FINSUS/Proyecto): Recibe fondos en MXN
3. **Capital** (Marketplace): Financia el BNPL

## 🚀 Setup

### Prerequisitos

- Python 3.9+
- Docker (para Rafiki)
- Node.js 20+ y pnpm (para Rafiki)

### Instalación

```bash
# 1. Clonar repositorio
git clone https://github.com/Carlosfintech/fintechhacks.constructoken.git
cd fintechhacks.constructoken

# 2. Iniciar Rafiki localenv
cd rafiki
pnpm i
pnpm localenv:compose up -d
cd ..

# 3. Configurar backend
cd backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt

# 4. Configurar environment
cp env.example .env
# Editar .env con las credenciales de Rafiki

# 5. Iniciar servidor
python main.py
```

### Ejecución del Demo

```bash
cd backend
python demo.py
```

Esto ejecutará el flujo completo:
- Creación de proyecto
- 8 pagos del usuario
- Activación automática de BNPL
- Financiamiento desde Capital

## 📡 API Endpoints

- `POST /start-project-funding` - Iniciar financiamiento de proyecto
- `POST /execute-payment/{project_id}` - Ejecutar pago individual
- `POST /rafiki-webhook` - Recibir eventos de Rafiki (lógica BNPL)
- `GET /project-status/{project_id}` - Consultar estado del proyecto
- `GET /projects` - Listar todos los proyectos

## 🔑 Características Clave

- **Pagos Cross-Currency**: USD → MXN automático vía Interledger
- **Lógica Condicional**: BNPL se activa solo después del 8º pago
- **Webhooks**: Procesamiento asíncrono de eventos de pago
- **Estado Persistente**: Tracking completo del progreso de cada proyecto

## 📚 Documentación

Ver [CLAUDE.md](./CLAUDE.md) para detalles de arquitectura y desarrollo.

## 🛠️ Stack Tecnológico

- **Backend**: FastAPI, Pydantic, httpx
- **Payments**: Rafiki (Interledger), GraphQL
- **Auth**: GNAP (Grant Negotiation and Authorization Protocol)
- **Accounting**: TigerBeetle
- **Database**: PostgreSQL (Rafiki), SQLite (Backend prototype)

## 📄 Licencia

Apache-2.0 (Rafiki)

---

**Hackathon**: Interledger Foundation
**Fecha**: Noviembre 2025
**Autor**: Carlos Landaverde
