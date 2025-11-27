

#  Clasificador IT: Sistema Experto de Tickets

## Descripción del Proyecto

Este proyecto es un **Sistema Experto** que utiliza lógica y una base de conocimiento para analizar la descripción o el síntoma principal de un ticket de soporte de TI y luego:

1.  **Clasificar** el ticket en una **Categoría** (por ejemplo: Software, Hardware, Redes).
2.  **Sugerir** el **Técnico** o el equipo más adecuado para resolverlo.

El objetivo es automatizar la asignación de tickets, mejorando los tiempos de respuesta y la eficiencia del soporte.

-----

## 🧭 Cómo funciona (paso a paso)

1) Interfaz web (frontend)

- Archivo: `interfaz/templates/index.html`.
- El usuario elige categoría (Hardware/Software) y selecciona un síntoma.
- La vista muestra una previsualización inmediata de Categoría, Técnico, Regla y una solución base.
- Al pulsar "Enviar":
  - Para 4 síntomas específicos se activa el Asistente de 3 pasos (Sí/No).
  - Para el resto, se usa el flujo clásico (clasificación directa) contra la API.
  - Resiliencia de UI: si el endpoint iterativo no está disponible, la UI hace fallback automático al flujo clásico sin mostrar popups de error.

2) API (backend)

- Archivo: `main.py` (FastAPI).
- Endpoints principales:
  - POST `/clasificar_ticket/`: flujo clásico (categoría + técnico + explicación + sugerencias).
  - POST `/clasificar_ticket_iterativo/`: flujo iterativo (devuelve regla + múltiples soluciones y sugerencias futuras).
- La base de conocimiento (`experto_general/base_conocimiento.py`) define reglas y técnicos por categoría.
- Los motores de inferencia están en `experto_general/acciones.py`.

3) Resultado mostrado en la UI

- Categoría asignada y Técnico sugerido.
- Regla aplicada y una solución de la regla.
- Sugerencias adicionales (hasta 2) para el flujo clásico.

---

## ✅ Asistente de 3 pasos (Sí / No)

- Activo solo para estos síntomas:
  - Software: `aplicacion_crash`, `lentitud_sistema` (ambos usan R-SW-01 con 3 soluciones).
  - Hardware: `memoria_ram_defectuosa` (R-HW-RAM-01), `monitor_no_enciende` (R-HW-MON-01).
- Funcionamiento:
  1. La UI llama a `/clasificar_ticket_iterativo/` y toma la primera regla aplicable.
  2. Muestra hasta 3 soluciones (máximo) de esa regla, una por vez.
  3. Si el usuario marca "No" en las 3, se deriva automáticamente a "Técnico en línea" (marca "Otra causa" y ejecuta el flujo clásico una vez para registrar).
  4. Si marca "Sí, funcionó" en cualquier paso, el asistente se cierra y queda marcada la solución en pantalla.

Notas de implementación:

- En el frontend, `MAX_STEPS = 3` y las soluciones se recortan con `slice(0, 3)`.
- No se cambia de regla ni se usa `historial` en la UI; se trabaja solo con la primera regla candidata.
- Si el servicio iterativo no responde, se oculta el asistente y se ejecuta el flujo clásico como alternativa silenciosa.

---

## 🔌 Endpoints disponibles

- POST `/clasificar_ticket/`
  - Entrada: `TicketFacts` (ver sección siguiente).
  - Salida: `categoria`, `tecnico_responsable`, `sintoma`, `explicacion` (id/titulo/descripcion/solucion_regla), `soluciones_sugeridas` (0-2), `solucion_sugerida` (compatibilidad).

- POST `/clasificar_ticket_iterativo/`
  - Entrada: `{ "facts": TicketFacts, "historial": ["R-XYZ-01", ...] }`.
  - Salida: `categoria`, `tecnico_responsable`, `sintoma`, `regla_id`, `explicacion` (id/titulo/descripcion), `soluciones` (lista), `sugerencias_futuras`.

- Salud y utilidades:
  - GET `/healthz`
  - POST `/feedback`, GET `/feedback/metrics`
  - POST/GET `/nuevos_sintomas`, GET `/nuevos_sintomas/export/html`
  - GET `/consultas`, `/consultas/metrics`, `/consultas/export/html`, `/consultas/export/csv`
    - Parámetros opcionales: `?date=YYYY-MM-DD` o `?all=true` para leer un día específico o agregar todos los archivos rotados.
    - Nuevos auxiliares: `GET /consultas/files` (lista archivos) y `POST /consultas/purge?date=YYYY-MM-DD` o `?all=true`.

---

## 🧱 Modelo de entrada: TicketFacts

Flags principales (booleanas) más campos de “otra causa”:

- Hardware: `pc_no_enciende`, `periferico_roto`, `tarjeta_video_falla`, `ram_falla`, `disco_falla`, `monitor_sin_senal`, `psu_falla`, `sobrecalentamiento`.
- Red: `no_puede_conectar_wifi`, `sin_acceso_internet`.
- Software: `programa_se_cierra`, `lentitud_sistema`, `actualizaciones_fallidas`, `incompatibilidad_software`, `software_corporativo_falla`.
- Permisos: `acceso_denegado`, `no_puede_instalar`.
- Seguridad: `email_sospechoso`, `malware_detectado`.
- Especial: `otra_causa` (bool), `otra_descripcion` (str | null).

Contrato de uso:
- La UI envía solo un síntoma activo (un flag True) por vez. Si `otra_causa=True`, se prioriza “Técnico en línea”.

---

## 🧪 Pruebas

Ejecuta los tests con pytest (opcional):

```powershell
python -m pytest -q
```

---

## 🛟 Problemas comunes

- Backend no disponible: la UI ya no muestra popups intrusivos. Verás un mensaje inline en el panel de resultado indicando “Sin conexión (backend no disponible)”.
  - Asegúrate de tener la API arriba en `http://127.0.0.1:8000`.
  - Si abriste la UI como archivo (`file://`), algunos navegadores bloquean fetch; usa el servidor local (`http://127.0.0.1:8001`).

- El botón “Enviar” vuelve a la pantalla anterior.
  - Todos los botones tienen `type="button"` y los handlers usan `preventDefault()`; haz un hard refresh (Ctrl+F5) para tomar el JS actualizado.

---

## 🧹 Limpieza y artefactos locales

- No se versionan: `venv/`, caches (`__pycache__/`, `.pytest_cache/`), y la carpeta `data/` (excepto `data/data.db`).
- Excepción en `.gitignore`: `!data/data.db` para que la base SQLite sea visible/versionable.
- La aplicación crea `./data/` automáticamente y genera ahí los archivos cuando la API corre.
- Rotación de consultas: los logs se guardan como `data/consultas-YYYY-MM-DD.jsonl`. Los endpoints aceptan `date` o `all` para seleccionar archivos.
- Limpieza de legado: si existe `data/consultas.jsonl`, se elimina automáticamente al iniciar (el log activo es el rotado por fecha).

---

## 📦 Cómo ejecutar (resumen)

1) API (puerto 8000):

```powershell
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

2) UI opcional (servidor en 8001):

```powershell
python -m uvicorn interfaz.app_visual:app --reload --host 127.0.0.1 --port 8001
```

3) O abrir la UI directamente (requiere la API arriba):

```powershell
start .\interfaz\templates\index.html
```


## ✨ Características Principales

  * **Clasificación Lógica:** El sistema aplica un conjunto de reglas (la "Base de Conocimiento") para determinar la categoría del ticket.
  * **Sugerencia de Experto:** Asigna el ticket al técnico o especialista responsable según la categoría clasificada.
  * **Interfaz Web Simple:** Permite a los usuarios o a otros sistemas ingresar el síntoma y obtener la clasificación al instante.
  * **Diseño Modular:** El código está organizado en módulos claros para la lógica (`experto_general`), los modelos de datos y la interfaz.

-----

## 🛠️ Estructura del Proyecto

Tu estructura es clara y funcional. Aquí se explica el rol de cada componente principal:

```
├── experto_general/              # Lógica del Sistema Experto (reglas e inferencia)
│   ├── acciones.py               # Motores de inferencia y utilidades
│   ├── base_conocimiento.py      # Reglas (con 3 soluciones para algunos síntomas)
│   └── modelos.py                # Modelos/datatypes
├── interfaz/
│   ├── app_visual.py             # ASGI para servir la UI estática (opcional)
│   └── templates/
│       └── index.html            # Interfaz web del clasificador
├── tests/
│   └── test_acciones.py          # Pruebas básicas
├── main.py                       # FastAPI app (endpoints)
├── requirements.txt              # Dependencias
└── README.md
```

-----

## 🚀 Cómo Ponerlo en Marcha

### Prerequisitos

  * **Python 3.x**
  * (Opcional, pero recomendado) Un entorno virtual (`venv`)

### Instalación

1.  **Clonar el repositorio:**
    ```bash
    git clone <URL-del-repositorio>
    cd nombre-del-proyecto
    ```
2.  **Crear y activar el entorno virtual:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```
3.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

### Uso

Para ejecución local, sigue la sección "Cómo ejecutar localmente (API + UI)" más abajo (usa Uvicorn para levantar la API y, opcionalmente, servir la UI). 


## ▶️ Cómo ejecutar localmente (API + UI)

Este proyecto usa FastAPI para el backend y una entrada ligera para servir la SPA desde `interfaz/`.

1) Iniciar la API (puerto 8000):

```powershell
# desde la raíz del proyecto
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

2) Iniciar la UI (servidor para la plantilla estática, puerto 8001):

```powershell
# desde la raíz del proyecto
python -m uvicorn interfaz.app_visual:app --reload --host 127.0.0.1 --port 8001
```

3) Abrir en el navegador:

- UI: http://127.0.0.1:8001/
- API (ejemplo de salud): http://127.0.0.1:8000/

### Alternativa rápida en Windows: abrir la UI con start index.html

Si no deseas levantar el servidor de UI, puedes abrir la página directamente en el navegador y se conectará a la API en `http://127.0.0.1:8000`:

```powershell
# Desde la raíz del proyecto, abre la UI directamente
start .\interfaz\templates\index.html
```

Notas:

- Asegúrate de tener la API corriendo en `http://127.0.0.1:8000` antes de abrir el HTML, de lo contrario verás el mensaje "No se pudo conectar con el servicio de clasificación".
- Si tu navegador bloquea solicitudes desde `file://`, usa la opción recomendada con servidor de UI en `http://127.0.0.1:8001`.

## 🔁 Nota sobre Pydantic

Se actualizó el proyecto para evitar la advertencia de deprecación de Pydantic v2: llamadas a `BaseModel.dict()` fueron migradas a `BaseModel.model_dump()` donde correspondía (por ejemplo en `main.py`). Los tests pasan y no se esperan cambios de comportamiento.

-----

## 🧩 Clasificación iterativa con múltiples soluciones

Además del endpoint clásico `/clasificar_ticket/`, el sistema incluye un flujo iterativo que devuelve múltiples pasos de solución y recomendaciones futuras, evitando repetir reglas ya sugeridas.

Endpoint:

- POST `/clasificar_ticket_iterativo/`

Cuerpo (JSON):

```json
{
  "facts": {
    "pc_no_enciende": false,
    "periferico_roto": false,
    "tarjeta_video_falla": false,
    "no_puede_conectar_wifi": true,
    "sin_acceso_internet": false,
    "programa_se_cierra": false,
    "lentitud_sistema": false,
    "acceso_denegado": false,
    "no_puede_instalar": false,
    "email_sospechoso": false,
    "otra_causa": false,
    "otra_descripcion": null
  },
  "historial": ["R-RED-01"]
}
```

Respuesta (ejemplo):

```json
{
  "categoria": "Red",
  "tecnico_responsable": "Técnica María (Especialista en Redes/Conectividad)",
  "sintoma": "no_puede_conectar_wifi",
  "regla_id": "R-RED-01",
  "explicacion": {
    "id": "R-RED-01",
    "titulo": "Problema de conexión WiFi / Internet",
    "descripcion": "Si no puede conectar al WiFi o no tiene acceso a Internet, clasificar como Red."
  },
  "soluciones": [
    "Comprobar que el SSID y la contraseña sean correctos.",
    "Olvidar y volver a conectarse a la red.",
    "Renovar IP (DHCP) y limpiar DNS.",
    "Reiniciar router/switch y verificar luz de enlace.",
    "Probar conectividad por cable para aislar WiFi."
  ],
  "sugerencias_futuras": [
    "Escalar a NOC si hay caída general.",
    "Registrar el incidente con hora y ubicación para correlación."
  ]
}
```

Notas:

- La UI actual no usa `historial` ni cambia de regla: el asistente muestra hasta 3 opciones de la primera regla aplicable y, si ninguna funciona, deriva automáticamente al técnico en línea.
- El registro automático de nuevos síntomas desde la UI está desactivado; los endpoints relacionados (`/nuevos_sintomas`) permanecen disponibles para uso manual o integraciones futuras.

-----





