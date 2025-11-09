# 🎨 Guía del Frontend MVP - Constructoken

## ✅ Lo Que Se Implementó

### Archivos Creados:
1. **`frontend/api/openpayments.ts`** - Funciones API para ambos casos
2. **`frontend/pages/payments.vue`** - Landing page 
3. **`frontend/pages/caso1.vue`** - Remesas (USD → MXN)
4. **`frontend/pages/caso2.vue`** - Compras (MXN → MXN)
5. **`frontend/pages/fulfil/migrante/[transaction_id].vue`** - Callback Caso 1 (automático)
6. **`frontend/pages/fulfil/purchase/[transaction_id].vue`** - Callback Caso 2 (automático)

---

## 🚀 Cómo Iniciar el Frontend

### 1. Ir a la carpeta frontend:
```bash
cd frontend
```

### 2. Instalar dependencias (si no lo has hecho):
```bash
yarn install
# o
npm install
```

### 3. Iniciar el servidor de desarrollo:
```bash
yarn dev
# o
npm run dev
```

El frontend estará disponible en: **http://localhost:3000**

---

## 📱 Páginas Disponibles

### Landing Page: `/payments`
- Vista general con ambos casos
- Botones para ir a Caso 1 o Caso 2

### Caso 1 - Remesas: `/caso1`
- Form para ingresar monto en MXN
- Botón "Enviar Remesa"
- Flujo: MIGRANTE (USD) → FINSUS (MXN)

### Caso 2 - Compras: `/caso2`
- Form para ingresar monto en MXN
- Botón "Pagar Materiales"
- Flujo: FINSUS (MXN) → MERCHANT (MXN)

---

## 🔄 Flujo Completamente Automatizado

### Antes (Manual):
1. Llamar a `/start` desde terminal
2. Copiar redirect_url
3. Abrir en navegador
4. Autorizar
5. Copiar URL del callback
6. Pegar en terminal para ejecutar

### Ahora (Automático):
1. ✅ Usuario hace clic en "Enviar Remesa" o "Pagar Materiales"
2. ✅ Frontend llama automáticamente a `/start`
3. ✅ Redirige a Interledger
4. ✅ Usuario autoriza
5. ✅ Interledger redirige a `/fulfil/{tipo}/{transaction_id}`
6. ✅ Página de fulfil automáticamente llama al `/callback`
7. ✅ Muestra resultado (success/error)

**🎉 ¡Todo automático! No más copiar/pegar URLs**

---

## 🧪 Cómo Probar

### Paso 1: Iniciar Backend (si no está corriendo)
```bash
# En la raíz del proyecto
docker-compose up
```

### Paso 2: Iniciar Frontend
```bash
cd frontend
yarn dev
```

### Paso 3: Probar Caso 1
1. Ir a http://localhost:3000/payments
2. Clic en "Enviar Remesa"
3. Ingresar monto (ej: 15.00 MXN)
4. Clic en "Enviar Remesa"
5. Autorizar con cuenta **PANCHO** (USD) en Interledger
6. ✨ El sistema completa automáticamente el pago
7. Ver resultado en pantalla

### Paso 4: Probar Caso 2
1. Ir a http://localhost:3000/payments
2. Clic en "Pagar Materiales"
3. Ingresar monto (ej: 15.00 MXN)
4. Clic en "Pagar Materiales"
5. Autorizar con cuenta **DESTINATARIO** (MXN) en Interledger
6. ✨ El sistema completa automáticamente el pago
7. Ver resultado en pantalla

---

## 🎨 Características del UI

### Diseño Moderno:
- ✅ Tailwind CSS
- ✅ Gradientes de colores
- ✅ Animaciones de loading
- ✅ Estados de éxito/error
- ✅ Responsive design
- ✅ Iconos emoji para mejor UX

### Estados Visuales:
- **Loading:** Spinner animado
- **Success:** Check verde con detalles
- **Error:** X roja con mensaje

### Información Clara:
- Conversión de moneda visible
- Cuentas origen/destino
- Transaction IDs
- Status del pago

---

## 🔧 Configuración Importante

### Backend URL
El frontend llama al backend en `http://localhost/v1/payments/...`

Si tu backend está en otro puerto, edita:
```typescript
// frontend/api/core.ts
// Busca la función url() y actualiza la URL base
```

### Rutas de Fulfil
Las rutas de callback deben coincidir con el backend:
- Backend: `redirect_uri=http://localhost:3000/fulfil/migrante/`
- Frontend: `/fulfil/migrante/[transaction_id].vue` ✅

---

## 📊 Estructura del Proyecto

```
frontend/
├── api/
│   └── openpayments.ts         # Funciones API nuevas
├── pages/
│   ├── payments.vue            # Landing page
│   ├── caso1.vue               # Remesas
│   ├── caso2.vue               # Compras
│   └── fulfil/
│       ├── migrante/
│       │   └── [transaction_id].vue   # Callback automático Caso 1
│       └── purchase/
│           └── [transaction_id].vue   # Callback automático Caso 2
```

---

## 🐛 Troubleshooting

### Error: "Cannot find module..."
```bash
cd frontend
yarn install
```

### Error: "ECONNREFUSED"
- Verifica que el backend esté corriendo: `docker-compose ps`
- Verifica la URL del backend en `frontend/api/core.ts`

### Error en callback: "Faltan parámetros"
- Verifica que la URL de redirect_uri en el backend sea correcta
- Debe ser: `http://localhost:3000/fulfil/migrante/` o `/purchase/`

### Pago se queda en "Processing..."
- Abre la consola del navegador (F12)
- Revisa errores de red
- Verifica los logs del backend

---

## 🎯 Para la Demo del Hackathon

### Preparación:
1. Tener backend corriendo: `docker-compose up`
2. Tener frontend corriendo: `cd frontend && yarn dev`
3. Tener ambas cuentas de Interledger abiertas en tabs separados:
   - PANCHO (para Caso 1)
   - DESTINATARIO (para Caso 2)

### Flow de Demo:
1. Mostrar landing page `/payments`
2. **Demo Caso 1:**
   - Explicar: "Envío de remesas USD → MXN"
   - Hacer pago de ejemplo
   - Mostrar autorización en Interledger
   - Mostrar completion automático
3. **Demo Caso 2:**
   - Explicar: "Pago de materiales MXN → MXN"
   - Hacer pago de ejemplo
   - Mostrar resultado

### Puntos a Destacar:
- ✅ Conversión automática de moneda
- ✅ Integración con Open Payments
- ✅ UX fluida sin copiar/pegar
- ✅ Feedback visual claro
- ✅ Manejo de errores

---

## 🚀 Mejoras Futuras (Opcional)

Si tienes tiempo extra:
- [ ] Historial de transacciones
- [ ] QR codes para pagos
- [ ] Notificaciones en tiempo real
- [ ] Multi-idioma (ES/EN)
- [ ] Dark mode
- [ ] Gráficas de conversión de moneda

---

## ✅ Checklist Pre-Demo

- [ ] Backend corriendo y respondiendo
- [ ] Frontend corriendo en localhost:3000
- [ ] Ambos casos probados y funcionando
- [ ] Cuentas de Interledger configuradas
- [ ] Internet estable
- [ ] Pantalla limpia para compartir

---

**¡Todo listo para el hackathon!** 🎉

