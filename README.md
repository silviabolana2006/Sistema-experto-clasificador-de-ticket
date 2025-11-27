


# Clasificador IT: Sistema Experto de Tickets

## Descripción

Este proyecto es un sistema experto para la clasificación automática de tickets de soporte IT. Analiza el síntoma principal de cada ticket y:

1. Clasifica el ticket en una categoría (por ejemplo: Software, Hardware, Redes).
2. Sugiere el técnico o equipo más adecuado para resolverlo.

El objetivo es mejorar la eficiencia y los tiempos de respuesta del soporte técnico.

---

## Cómo funciona

### Interfaz web

- Ubicada en `interfaz/templates/index.html`.
- El usuario selecciona la categoría y el síntoma.
- La interfaz muestra una previsualización de la categoría, técnico sugerido, regla aplicada y solución base.
- Al enviar, para ciertos síntomas se activa un asistente paso a paso; para el resto, se usa el flujo clásico.

### API (backend)

- Implementada en `main.py` usando FastAPI.
- Endpoints principales:
  - `/clasificar_ticket/`: clasificación clásica.
  - `/clasificar_ticket_iterativo/`: asistente iterativo con varias soluciones.
- La lógica de reglas y técnicos está en `experto_general/base_conocimiento.py`.
- Los motores de inferencia están en `experto_general/acciones.py`.

### Resultado

- Se muestra la categoría, técnico sugerido, regla aplicada y solución.
- Para el flujo clásico, se pueden mostrar hasta dos sugerencias adicionales.

---

## Asistente paso a paso

- Activo solo para síntomas específicos (por ejemplo: aplicación se cierra, lentitud, memoria RAM defectuosa, monitor no enciende).
- Muestra hasta tres soluciones posibles, una por vez.
- Si ninguna funciona, deriva automáticamente al técnico en línea.
- Si alguna funciona, el asistente finaliza y muestra la solución.

---

## Endpoints principales

- `/clasificar_ticket/`: recibe los datos del ticket y devuelve la clasificación y sugerencias.
- `/clasificar_ticket_iterativo/`: recibe los datos y el historial, devuelve la regla, soluciones y sugerencias futuras.
- Otros endpoints: `/healthz`, `/feedback`, `/nuevos_sintomas`, `/consultas` y utilidades para métricas y exportación.

---

## Modelo de entrada

El sistema espera un objeto con flags booleanos para cada síntoma relevante, por ejemplo:

- Hardware: `pc_no_enciende`, `ram_falla`, `monitor_sin_senal`, etc.
- Red: `no_puede_conectar_wifi`, `sin_acceso_internet`.
- Software: `programa_se_cierra`, `lentitud_sistema`, etc.
- Permisos y seguridad: `acceso_denegado`, `malware_detectado`.
- Especial: `otra_causa` y `otra_descripcion`.

Solo un síntoma debe estar activo por vez.

---

## Pruebas

Para ejecutar las pruebas automáticas:

```powershell
python -m pytest -q
```

---

## Problemas comunes

- Si el backend no está disponible, la interfaz muestra un mensaje de error y hace fallback automático.
- Si el botón "Enviar" no responde, refrescar la página y asegurarse de que la API esté corriendo.

---

## Limpieza y archivos ignorados

- No se versionan carpetas de entorno virtual, cachés ni archivos temporales.
- La carpeta `data/` solo versiona la base de datos principal y los logs relevantes.
- La aplicación crea y rota los archivos de datos automáticamente.

---

## Ejecución rápida

1. Instalar dependencias:
   ```powershell
   pip install -r requirements.txt
   ```

2. Iniciar la API:
   ```powershell
   python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
   ```

3. (Opcional) Iniciar el servidor de la interfaz:
   ```powershell
   python -m uvicorn interfaz.app_visual:app --reload --host 127.0.0.1 --port 8001
   ```

4. Abrir la interfaz web en el navegador:
   - Si usás el servidor: http://127.0.0.1:8001/
   - O abrir directamente el archivo `index.html` si la API está corriendo.

---

## Estructura del proyecto

```
experto_general/        # Lógica y reglas del sistema experto
interfaz/               # Interfaz web y servidor opcional
tests/                  # Pruebas automáticas
main.py                 # API principal (FastAPI)
requirements.txt        # Dependencias
README.md               # Documentación
```

---

## Requisitos

- Python 3.x
- (Opcional) Entorno virtual

---

## Instalación

1. Clonar el repositorio:
   ```powershell
   git clone <URL-del-repositorio>
   cd <nombre-del-proyecto>
   ```

2. Crear y activar el entorno virtual (opcional):
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate
   ```

3. Instalar dependencias:
   ```powershell
   pip install -r requirements.txt
   ```

---

## Contacto y soporte

Para dudas, sugerencias o reportes de errores, podés abrir un issue en el repositorio o contactar al mantenedor.


