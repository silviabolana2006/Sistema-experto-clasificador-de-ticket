from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response
from pydantic import BaseModel
from typing import Optional
import json
import os
import sqlite3
from datetime import datetime
import io
import csv
# 1. IMPORTACIÓN: Importar la Base de Conocimiento
from experto_general.base_conocimiento import REGLAS_CLASIFICACION, MAPEO_TECNICOS 
from experto_general.acciones import motor_inferencia, sugerir_tecnico, obtener_solucion_sugerida
from experto_general.acciones import motor_inferencia, sugerir_tecnico, obtener_solucion_sugerida, motor_inferencia_iterativo, obtener_soluciones_sugeridas
from typing import Optional, List

app = FastAPI()

# CORS - CRÍTICO para conectar el frontend
# CORS: para desarrollo local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8001", "http://localhost:8001", "*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo de datos que recibe el frontend (¡Mantenemos el mismo, perfecto!)
class TicketFacts(BaseModel):
    pc_no_enciende: bool = False
    periferico_roto: bool = False
    tarjeta_video_falla: bool = False
    ram_falla: bool = False
    disco_falla: bool = False
    monitor_sin_senal: bool = False
    psu_falla: bool = False
    sobrecalentamiento: bool = False
    no_puede_conectar_wifi: bool = False
    sin_acceso_internet: bool = False
    programa_se_cierra: bool = False
    lentitud_sistema: bool = False
    actualizaciones_fallidas: bool = False
    incompatibilidad_software: bool = False
    acceso_denegado: bool = False
    no_puede_instalar: bool = False
    email_sospechoso: bool = False
    software_corporativo_falla: bool = False
    malware_detectado: bool = False
    # Nueva bandera para indicar que la causa es otra y requiere técnico en línea
    otra_causa: bool = False
    # Descripción opcional cuando la causa es 'otra'
    otra_descripcion: str | None = None

class NuevoSintomaInput(BaseModel):
    texto: str
    categoria_predicha: Optional[str] = None
    sintoma: Optional[str] = None
    otra_descripcion: Optional[str] = None


class ClasificarIterativoInput(BaseModel):
    facts: TicketFacts
    historial: Optional[List[str]] = None

@app.get("/")
async def root():
    return {"message": "Sistema Experto IT funcionando correctamente"}

@app.post("/clasificar_ticket/")
async def clasificar_ticket(facts: TicketFacts):
    # Convertir el objeto Pydantic a diccionario para ser evaluado por las lambdas
    # Pydantic v2: use model_dump() instead of deprecated dict()
    facts_dict = facts.model_dump()
    
    # 2. INFERENCIA: usar motor_inferencia (encadenamiento hacia adelante)
    # Determinar sintoma activo (diseño del frontend: solo uno debe ser True)
    sintoma_activo = None
    sintomas_ignorar = {"otra_causa", "otra_descripcion"}
    for k, v in facts_dict.items():
        if k in sintomas_ignorar:
            continue
        if isinstance(v, bool) and v:
            sintoma_activo = k
            break

    if not sintoma_activo:
        clasificacion_final = "Sin clasificar (General)"
        regla_usada = None
    else:
        clasificacion_final, regla_usada = motor_inferencia(facts_dict, REGLAS_CLASIFICACION)

    # 3. ASIGNACIÓN: Usar el mapeo para determinar el técnico responsable
    # Nueva lógica: sólo priorizar "Otra causa" si no hubo coincidencia de regla/síntoma
    # para evitar que una marca accidental de la casilla opaque una clasificación válida.
    # Priorizar siempre 'Otra causa' si el usuario lo marcó explícitamente
    if facts_dict.get("otra_causa"):
        tecnico_sugerido = "Técnico en línea (Soporte Remoto)"
        clasificacion_final = "Otra causa"
    else:
        tecnico_sugerido = sugerir_tecnico(clasificacion_final)

    response = {
        "categoria": clasificacion_final,
        "tecnico_responsable": tecnico_sugerido,
        "sintoma": sintoma_activo if sintoma_activo else "Ninguno"
    }

    # Incluir la descripción si fue enviada
    if facts_dict.get("otra_descripcion"):
        response["otra_descripcion"] = facts_dict.get("otra_descripcion")

    # Añadir explicación (metadatos legibles de la regla usada)
    if regla_usada:
        response["explicacion"] = {
            "id": regla_usada.get("id"),
            "titulo": regla_usada.get("titulo"),
            "descripcion": regla_usada.get("descripcion"),
            "solucion_regla": regla_usada.get("solucion"),
        }
    else:
        response["explicacion"] = {"id": None, "titulo": None, "descripcion": "Ninguna regla coincidió", "solucion_regla": None}

    regla_id_for_suggestion = None
    try:
        regla_id_for_suggestion = (response.get("explicacion") or {}).get("id")
    except Exception:
        regla_id_for_suggestion = None
    # Dos sugerencias (y compatibilidad con campo anterior)
    soluciones_sug = obtener_soluciones_sugeridas(response.get("categoria"), regla_id_for_suggestion) if response.get("categoria") else []
    response["soluciones_sugeridas"] = soluciones_sug
    response["solucion_sugerida"] = soluciones_sug[0] if soluciones_sug else None

    # Registrar consulta realizada para retroalimentación futura
    try:
        consulta_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "facts": facts_dict,
            "resultado": {
                "categoria": response.get("categoria"),
                "tecnico_responsable": response.get("tecnico_responsable"),
                "sintoma": response.get("sintoma"),
                "regla_id": (response.get("explicacion") or {}).get("id"),
            },
        }
        consultas_path = get_consultas_file_today()
        with open(consultas_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(consulta_record, ensure_ascii=False) + "\n")
    except Exception:
        # No interrumpir el flujo principal si falla el guardado
        pass

    return response


@app.post("/clasificar_ticket_iterativo/")
async def clasificar_ticket_iterativo(payload: ClasificarIterativoInput):
    """
    Endpoint iterativo: devuelve múltiples soluciones y sugerencias futuras, evitando repetir reglas ya vistas.

    Cuerpo esperado:
    {
      "facts": { ... TicketFacts ... },
      "historial": ["R-XYZ-01", ...]
    }
    """
    facts_dict = payload.facts.model_dump()
    historial = payload.historial or []

    # Determinar síntoma activo (primera bandera True distinta de 'otra_causa'/'otra_descripcion')
    sintoma_activo = None
    for k, v in facts_dict.items():
        if k in {"otra_causa", "otra_descripcion"}:
            continue
        if isinstance(v, bool) and v:
            sintoma_activo = k
            break

    res = motor_inferencia_iterativo(facts_dict, REGLAS_CLASIFICACION, historial)

    categoria = res.get("categoria") or "Sin clasificar (General)"
    # Priorizar asignación especial si es 'otra causa'
    if facts_dict.get("otra_causa"):
        categoria = "Otra causa"
        tecnico = "Técnico en línea (Soporte Remoto)"
    else:
        tecnico = sugerir_tecnico(categoria)

    response = {
        "categoria": categoria,
        "tecnico_responsable": tecnico,
        "sintoma": sintoma_activo or "Ninguno",
        "regla_id": res.get("regla_id"),
        "explicacion": {
            "id": res.get("regla_id"),
            "titulo": res.get("titulo"),
            "descripcion": res.get("descripcion"),
        },
        "soluciones": res.get("soluciones", []),
        "sugerencias_futuras": res.get("sugerencias_futuras", []),
    }

    # Registrar consulta iterativa
    try:
        consulta_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "facts": facts_dict,
            "iterativo": True,
            "historial": historial,
            "resultado": {
                "categoria": response.get("categoria"),
                "tecnico_responsable": response.get("tecnico_responsable"),
                "sintoma": response.get("sintoma"),
                "regla_id": response.get("regla_id"),
            },
        }
        consultas_path = get_consultas_file_today()
        with open(consultas_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(consulta_record, ensure_ascii=False) + "\n")
    except Exception:
        pass

    return response

# --- Endpoints de salud y retroalimentación ---

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


# --- Paths de datos persistentes (centralizados en ./data) ---
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

FEEDBACK_FILE = os.path.join(DATA_DIR, "feedback.jsonl")
DB_FILE = os.path.join(DATA_DIR, "data.db")

# Rotación diaria para consultas: consultas-YYYY-MM-DD.jsonl
def _today_str():
    try:
        # Preferir fecha UTC para consistencia
        return datetime.utcnow().strftime("%Y-%m-%d")
    except Exception:
        from datetime import date
        return date.today().strftime("%Y-%m-%d")

def consultas_file_for_date(date_str: str) -> str:
    safe = (date_str or _today_str()).strip()
    return os.path.join(DATA_DIR, f"consultas-{safe}.jsonl")

def get_consultas_file_today() -> str:
    return consultas_file_for_date(_today_str())

def list_consultas_files() -> list[str]:
    try:
        return sorted(
            [
                os.path.join(DATA_DIR, f)
                for f in os.listdir(DATA_DIR)
                if f.startswith("consultas-") and f.endswith(".jsonl")
            ]
        )
    except Exception:
        return []

def _ensure_data_files():
    # Crea archivos si no existen, sin truncar si existen
    try:
        # feedback.jsonl
        for p in (FEEDBACK_FILE, get_consultas_file_today()):
            try:
                with open(p, "a", encoding="utf-8"):
                    pass
            except Exception:
                pass
        # Limpieza de legado: eliminar archivo antiguo no rotado si existe (consultas.jsonl)
        try:
            legacy = os.path.join(DATA_DIR, "consultas.jsonl")
            if os.path.exists(legacy):
                os.remove(legacy)
        except Exception:
            # No bloquear si no se puede eliminar
            pass
    except Exception:
        pass

def _init_db():
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS nuevos_sintomas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                texto TEXT NOT NULL,
                categoria_predicha TEXT,
                sintoma TEXT,
                otra_descripcion TEXT,
                user_agent TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()
    finally:
        try:
            conn.close()
        except Exception:
            pass

_init_db()
_ensure_data_files()

@app.post("/feedback")
async def post_feedback(req: Request):
    """
    Guarda feedback del usuario para retroalimentar el sistema.
    Cuerpo esperado (ejemplo):
    {
      "categoria_predicha": "Hardware",
      "categoria_correcta": "Hardware" | "...",
      "sintoma": "pc_no_enciende",
      "observacion": "texto opcional"
    }
    """
    data = await req.json()
    # Normalizar y anexar metadatos mínimos
    record = {
        **data,
        "_source": "ui",
    }
    try:
        with open(FEEDBACK_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception as e:
        return {"saved": False, "error": str(e)}
    return {"saved": True}


@app.get("/feedback/metrics")
async def feedback_metrics():
    """Devuelve conteos agregados de coincidencia vs. no coincidencia."""
    total = 0
    matches = 0
    mismatches = 0
    try:
        if os.path.exists(FEEDBACK_FILE):
            with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    total += 1
                    try:
                        rec = json.loads(line)
                        if rec.get("categoria_predicha") == rec.get("categoria_correcta"):
                            matches += 1
                        else:
                            mismatches += 1
                    except Exception:
                        continue
    except Exception as e:
        return {"error": str(e)}
    return {"total": total, "matches": matches, "mismatches": mismatches}

# --- Nuevos síntomas: guardar y exportar ---

@app.post("/nuevos_sintomas")
async def guardar_nuevo_sintoma(payload: NuevoSintomaInput, request: Request):
    ua = request.headers.get("user-agent", "")
    now = datetime.utcnow().isoformat()
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO nuevos_sintomas (texto, categoria_predicha, sintoma, otra_descripcion, user_agent, created_at) VALUES (?,?,?,?,?,?)",
            (
                payload.texto.strip(),
                payload.categoria_predicha,
                payload.sintoma,
                payload.otra_descripcion,
                ua,
                now,
            ),
        )
        conn.commit()
        new_id = cur.lastrowid
        return {"saved": True, "id": new_id}
    except Exception as e:
        return {"saved": False, "error": str(e)}
    finally:
        try:
            conn.close()
        except Exception:
            pass


@app.get("/nuevos_sintomas")
async def listar_nuevos_sintomas(limit: int = 50):
    items = []
    total = 0
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        # total count
        try:
            cur.execute("SELECT COUNT(1) FROM nuevos_sintomas")
            row = cur.fetchone()
            total = int(row[0]) if row and row[0] is not None else 0
        except Exception:
            total = 0
        cur.execute(
            "SELECT id, texto, categoria_predicha, sintoma, otra_descripcion, user_agent, created_at FROM nuevos_sintomas ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        for row in cur.fetchall():
            items.append(
                {
                    "id": row[0],
                    "texto": row[1],
                    "categoria_predicha": row[2],
                    "sintoma": row[3],
                    "otra_descripcion": row[4],
                    "user_agent": row[5],
                    "created_at": row[6],
                }
            )
    except Exception as e:
        return {"error": str(e)}
    finally:
        try:
            conn.close()
        except Exception:
            pass
    return {"items": items, "total": total}


@app.get("/nuevos_sintomas/export/html", response_class=HTMLResponse)
async def exportar_nuevos_sintomas_html():
    # Export simple en HTML para poder "Imprimir como PDF" desde el navegador sin dependencias extra
    res = await listar_nuevos_sintomas(limit=1000)
    if isinstance(res, dict) and res.get("error"):
        return HTMLResponse(content=f"<html><body><h1>Error</h1><pre>{res['error']}</pre></body></html>")
    items = res.get("items", [])
    rows = []
    for it in items:
        rows.append(
            f"<tr><td>{it['id']}</td><td>{(it['texto'] or '').replace('<','&lt;')}</td><td>{it.get('categoria_predicha') or ''}</td><td>{it.get('sintoma') or ''}</td><td>{(it.get('otra_descripcion') or '').replace('<','&lt;')}</td><td>{it.get('created_at') or ''}</td></tr>"
        )
    html = f"""
    <!doctype html>
    <html lang=es>
      <head>
        <meta charset=utf-8 />
        <title>Nuevos Síntomas</title>
        <style>
          body {{ font-family: Arial, sans-serif; margin: 24px; }}
          table {{ border-collapse: collapse; width: 100%; }}
          th, td {{ border: 1px solid #ddd; padding: 8px; font-size: 12px; }}
          th {{ background: #f3f4f6; text-align: left; }}
        </style>
      </head>
      <body>
        <h1>Nuevos Síntomas</h1>
        <table>
          <thead><tr><th>ID</th><th>Texto</th><th>Categoría predicha</th><th>Síntoma</th><th>Otra descripción</th><th>Creado</th></tr></thead>
          <tbody>{''.join(rows)}</tbody>
        </table>
      </body>
    </html>
    """
    return HTMLResponse(content=html)

# --- Consultas: listar y métricas ---

def _select_consulta_files(date: Optional[str] = None, all: bool = False) -> list[str]:
    if all:
        files = list_consultas_files()
        return files
    if date:
        return [consultas_file_for_date(date)]
    return [get_consultas_file_today()]


@app.get("/consultas")
async def listar_consultas(limit: int = 100, date: Optional[str] = None, all: bool = False):
    items = []
    total = 0
    try:
        files = _select_consulta_files(date=date, all=all)
        all_lines: list[str] = []
        for path in files:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    total += len(lines)
                    all_lines.extend(lines)
        # Tomar los últimos 'limit' globalmente
        for line in all_lines[-limit:]:
            try:
                rec = json.loads(line)
                items.append(
                    {
                        "timestamp": rec.get("timestamp"),
                        "categoria": (rec.get("resultado") or {}).get("categoria"),
                        "sintoma": (rec.get("resultado") or {}).get("sintoma"),
                        "regla_id": (rec.get("resultado") or {}).get("regla_id"),
                    }
                )
            except Exception:
                continue
    except Exception as e:
        return {"error": str(e)}
    return {"items": items[::-1], "total": total}


@app.get("/consultas/metrics")
async def consultas_metrics(date: Optional[str] = None, all: bool = False):
    por_categoria: dict[str, int] = {}
    por_sintoma: dict[str, int] = {}
    total = 0
    try:
        files = _select_consulta_files(date=date, all=all)
        for path in files:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    for line in f:
                        try:
                            rec = json.loads(line)
                            total += 1
                            cat = (rec.get("resultado") or {}).get("categoria") or "(desconocida)"
                            por_categoria[cat] = por_categoria.get(cat, 0) + 1
                            sint = (rec.get("resultado") or {}).get("sintoma") or "(ninguno)"
                            por_sintoma[sint] = por_sintoma.get(sint, 0) + 1
                        except Exception:
                            continue
    except Exception as e:
        return {"error": str(e)}
    return {"total": total, "por_categoria": por_categoria, "por_sintoma": por_sintoma}


@app.get("/consultas/export/html", response_class=HTMLResponse)
async def exportar_consultas_html(limit: int = 1000, date: Optional[str] = None, all: bool = False):
    try:
        items_resp = await listar_consultas(limit=limit, date=date, all=all)
        if isinstance(items_resp, dict) and items_resp.get("error"):
            return HTMLResponse(content=f"<html><body><h1>Error</h1><pre>{items_resp['error']}</pre></body></html>")
        items = items_resp.get("items", []) if isinstance(items_resp, dict) else []
        rows = []
        for it in items:
            rows.append(
                f"<tr><td>{(it.get('timestamp') or '')}</td><td>{(it.get('categoria') or '')}</td><td>{(it.get('sintoma') or '')}</td><td>{(it.get('regla_id') or '')}</td></tr>"
            )
        html = f"""
        <!doctype html>
        <html lang=es>
            <head>
                <meta charset=utf-8 />
                <title>Consultas realizadas</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 24px; }}
                    table {{ border-collapse: collapse; width: 100%; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; font-size: 12px; }}
                    th {{ background: #f3f4f6; text-align: left; }}
                </style>
            </head>
            <body>
                <h1>Consultas realizadas</h1>
                <table>
                    <thead><tr><th>Fecha (UTC)</th><th>Categoría</th><th>Síntoma</th><th>Regla</th></tr></thead>
                    <tbody>{''.join(rows)}</tbody>
                </table>
            </body>
        </html>
        """
        return HTMLResponse(content=html)
    except Exception as e:
        return HTMLResponse(content=f"<html><body><h1>Error</h1><pre>{str(e)}</pre></body></html>")


@app.get("/consultas/export/csv")
async def exportar_consultas_csv(limit: int = 1000, date: Optional[str] = None, all: bool = False):
    try:
        items_resp = await listar_consultas(limit=limit, date=date, all=all)
        if isinstance(items_resp, dict) and items_resp.get("error"):
            return Response(content=f"error,{items_resp['error']}", media_type="text/plain; charset=utf-8")
        items = items_resp.get("items", []) if isinstance(items_resp, dict) else []
        sio = io.StringIO()
        writer = csv.writer(sio)
        writer.writerow(["timestamp", "categoria", "sintoma", "regla_id"])
        for it in items:
            writer.writerow([
                (it.get('timestamp') or ''),
                (it.get('categoria') or ''),
                (it.get('sintoma') or ''),
                (it.get('regla_id') or ''),
            ])
        data = sio.getvalue()
        return Response(
            content=data,
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": "attachment; filename=consultas.csv"},
        )
    except Exception as e:
        return Response(content=f"error,{str(e)}", media_type="text/plain; charset=utf-8")

# Listar archivos de consultas disponibles
@app.get("/consultas/files")
async def consultas_files():
    files = list_consultas_files()
    return {"files": [os.path.basename(p) for p in files]}

# Purgar archivos de consultas: ?date=YYYY-MM-DD o ?all=true
@app.post("/consultas/purge")
async def consultas_purge(date: Optional[str] = None, all: bool = False):
    targets = _select_consulta_files(date=date, all=all)
    deleted = 0
    for path in targets:
        try:
            if os.path.exists(path):
                os.remove(path)
                deleted += 1
        except Exception:
            continue
    return {"deleted": deleted}

# Si estás ejecutando esto como un módulo (ej. 'uvicorn main:app --reload'), la importación anterior
# debería funcionar. Si tienes problemas de importación (ej. ModuleNotFoundError), intenta la
# importación relativa: `from experto_general.base_conocimiento import ...`