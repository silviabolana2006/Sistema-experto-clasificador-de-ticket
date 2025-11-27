

# Importamos las reglas y el mapeo Contiene el motor de inferencia (la lógica de clasificación) y la asignación del técnico.
from .base_conocimiento import REGLAS_CLASIFICACION, MAPEO_TECNICOS 
from typing import List, Optional

def motor_inferencia(hechos: dict, reglas: list):
    """
    Ejecuta el motor de inferencia para encontrar una categoría.
    Devuelve una tupla: (categoria, regla_encontrada) donde regla_encontrada es el dict de la regla
    que coincidió o None si no hubo coincidencia.
    """
    for regla in reglas:
        try:
            if regla["condicion"](hechos):
                return regla["resultado"], regla
        except KeyError:
            continue
    return "Sin clasificar (General)", None


def sugerir_tecnico(categoria: str) -> str:
    """
    Busca al técnico responsable sugerido para una categoría de ticket.
    """
    return MAPEO_TECNICOS.get(categoria, "Coordinador de Soporte")
def obtener_solucion_sugerida(categoria: str, regla_id: str | None = None) -> str:
    """
    Proporciona una solución sugerida basada en la categoría del ticket, y cuando
    sea posible, más específica por regla.
    """
    # Sugerencias específicas por regla
    soluciones_por_regla = {
        # Hardware
        "R-HW-01": "Probar con otra toma/cable, revisar PSU y placa base con tester; si no enciende, escalar a diagnóstico de HW.",
        "R-HW-02": "Probar periférico en otro puerto/equipo; si falla, reemplazo. Actualizar/instalar drivers genéricos si aplica.",
        "R-HW-VID-01": "Reinstalar drivers con DDU, verificar alimentación PCIe y temperaturas; si persisten artefactos/pantallazos, evaluar reemplazo de GPU.",
        "R-HW-RAM-01": "Ejecutar MemTest, probar módulos individualmente y reemplazar el módulo defectuoso si falla.",
        "R-HW-DISK-01": "Respaldar datos, revisar SMART/diagnóstico del fabricante; reemplazar unidad si persisten errores.",
        "R-HW-MON-01": "Verificar alimentación y entrada de video; probar con otro cable/monitor para descartar.",
        # Red
        "R-RED-01": "Olvidar/redescubrir red, renovar IP (DHCP), reiniciar router/switch; validar DNS/puerta de enlace.",
        # Software
        "R-SW-01": "Actualizar app/SO, revisar logs del visor de eventos, ejecutar en modo seguro/limpio; reinstalar si persiste.",
        "R-SW-CORP-01": "Revisar logs/dependencias, ejecutar reparación; restaurar backup validado y coordinar con equipo de la aplicación.",
        # Permisos
        "R-PM-01": "Solicitar elevación o permisos necesarios; validar políticas (GPO/AppLocker) y listas de control de acceso.",
        # Seguridad
        "R-SEC-01": "No abrir enlaces/adjuntos, reportar a seguridad, aislar equipo y ejecutar escaneo avanzado (EDR/AV).",
    }

    if regla_id and regla_id in soluciones_por_regla:
        return soluciones_por_regla[regla_id]

    # Fallback por categoría
    soluciones_por_categoria = {
        "Red": "Verificar conectividad física/lógica, renovar IP y reiniciar equipos de red.",
        "Hardware": "Ejecutar diagnóstico de hardware, revisar conexiones y reemplazar el componente defectuoso.",
        "Software": "Actualizar o reinstalar software; revisar compatibilidad y dependencias.",
        "Seguridad": "Realizar análisis completo, cambiar credenciales y aplicar políticas de hardening.",
        "Permisos": "Revisar pertenencia a grupos/roles y políticas de instalación/acceso.",
        "Sin clasificar (General)": "Revisar detalles y solicitar información adicional al usuario.",
        "Otra causa": "Derivar a soporte remoto para triage y diagnóstico guiado."
    }
    return soluciones_por_categoria.get(categoria, "No hay una solución sugerida disponible.")


def obtener_soluciones_sugeridas(categoria: str, regla_id: str | None = None) -> List[str]:
    """
    Devuelve hasta 2 sugerencias para presentar al usuario. Usa mapeo específico por regla y
    un fallback por categoría.
    """
    por_regla: dict[str, List[str]] = {
        # Hardware
        "R-HW-01": [
            "Revisar/medir PSU y conexiones internas.",
            "Probar fuera del gabinete con configuración mínima (placa+CPU+1 RAM).",
        ],
        "R-HW-02": [
            "Probar en otro equipo/puerto y reinstalar drivers.",
            "Reemplazar periférico si falla en pruebas cruzadas.",
        ],
        "R-HW-VID-01": [
            "Reinstalar drivers con DDU en modo seguro.",
            "Verificar alimentación PCIe/temperaturas y probar otro cable/monitor.",
        ],
        "R-HW-RAM-01": [
            "Ejecutar MemTest/Diagnóstico de memoria.",
            "Probar módulos individualmente y reemplazar el defectuoso.",
        ],
        "R-HW-DISK-01": [
            "Respaldar datos y revisar SMART/diagnóstico del fabricante.",
            "Cambiar cable/puerto y reemplazar unidad si persisten errores.",
        ],
        "R-HW-MON-01": [
            "Verificar entrada seleccionada y probar otro cable/monitor.",
            "Actualizar/reinstalar drivers de video.",
        ],
        "R-HW-PSU-01": [
            "Probar PSU con tester o reemplazo temporal.",
            "Verificar cables del panel frontal y corto en periféricos.",
        ],
        "R-HW-THERM-01": [
            "Limpiar ventiladores/disipadores y renovar pasta térmica.",
            "Revisar flujo de aire y perfiles de ventilación en BIOS/OS.",
        ],
        # Red
        "R-RED-01": [
            "Olvidar y reconectar a la red; renovar IP/DNS.",
            "Reiniciar router/AP o probar por cable.",
        ],
        # Software
        "R-SW-01": [
            "Actualizar app/SO y revisar conflictos en inicio limpio.",
            "Reinstalar o reparar la aplicación.",
        ],
        "R-SW-UPD-01": [
            "Limpiar caché de actualizaciones y reiniciar servicios.",
            "Aplicar manualmente el parche/installer oficial.",
        ],
        "R-SW-COMP-01": [
            "Ejecutar en compatibilidad o usar versión soportada.",
            "Revisar dependencias/SDK y documentación del proveedor.",
        ],
        "R-SW-CORP-01": [
            "Revisar logs y dependencias; ejecutar reparación.",
            "Coordinar restauración de backup validado.",
        ],
        # Permisos
        "R-PM-01": [
            "Validar rol/grupos y solicitar elevación controlada.",
            "Revisar GPO/AppLocker y política de instalación.",
        ],
        # Seguridad
        "R-SEC-01": [
            "No interactuar; reportar y aislar equipo.",
            "Ejecutar escaneo EDR/AV y cambio de credenciales.",
        ],
        "R-SEC-MAL-01": [
            "Aislar el equipo y ejecutar escaneo completo.",
            "Restaurar sistema/archivos desde respaldo confiable.",
        ],
    }

    por_categoria: dict[str, List[str]] = {
        "Hardware": [
            "Revisar conexiones/diagnóstico del componente.",
            "Probar reemplazo temporal o escalar a laboratorio.",
        ],
        "Red": [
            "Renovar IP/DNS y revisar credenciales.",
            "Reiniciar equipo de red o escalar a NOC.",
        ],
        "Software": [
            "Actualizar/reparar aplicación y dependencias.",
            "Reinstalar o usar versión soportada.",
        ],
        "Permisos": [
            "Solicitar elevación controlada.",
            "Ajustar rol/grupos y políticas.",
        ],
        "Seguridad": [
            "Aislar equipo y escanear con EDR/AV.",
            "Cambiar credenciales y revisar indicadores.",
        ],
        "Sin clasificar (General)": [
            "Solicitar más detalle del síntoma.",
            "Registrar nuevo síntoma para mejorar el sistema.",
        ],
        "Otra causa": [
            "Derivar a soporte remoto para triage.",
            "Solicitar captura/logs para análisis.",
        ],
    }

    if regla_id and regla_id in por_regla:
        return por_regla[regla_id][:2]
    return por_categoria.get(categoria, ["No hay sugerencias", "—"])[:2]


def motor_inferencia_iterativo(hechos: dict, reglas: list, historial_ids: Optional[List[str]] = None) -> dict:
    """
    Motor iterativo: devuelve soluciones múltiples y sugerencias futuras, evitando reglas ya sugeridas.

    Entrada:
    - hechos: dict de banderas/síntomas
    - reglas: lista de reglas con claves: id, titulo, descripcion, condicion, resultado, soluciones?, sugerencias_futuras?
    - historial_ids: lista de ids de reglas ya ofrecidas para no repetir

    Salida: dict con
    - categoria
    - regla_id, titulo, descripcion
    - soluciones (lista)
    - sugerencias_futuras (lista)
    """
    vistos = set(historial_ids or [])
    for regla in reglas:
        if regla.get("id") in vistos:
            continue
        try:
            if regla["condicion"](hechos):
                soluciones = list(regla.get("soluciones", []))
                sugerencias = list(regla.get("sugerencias_futuras", []))
                return {
                    "categoria": regla.get("resultado", "Sin clasificar (General)"),
                    "regla_id": regla.get("id"),
                    "titulo": regla.get("titulo"),
                    "descripcion": regla.get("descripcion"),
                    "soluciones": soluciones,
                    "sugerencias_futuras": sugerencias,
                }
        except Exception:
            # Cualquier error en la evaluación de la condición, continuamos con la siguiente regla
            continue

    # Sin coincidencias o reglas ya agotadas
    return {
        "categoria": "Sin clasificar (General)",
        "regla_id": None,
        "titulo": None,
        "descripcion": "No se encontró coincidencia con las reglas actuales o ya se agotaron.",
        "soluciones": [],
        "sugerencias_futuras": [
            "Describa un nuevo síntoma o causa en texto libre.",
            "Puede registrar el nuevo síntoma desde el menú de 'Sugerencias' para mejorar el sistema.",
        ],
    }

