from .modelos import TicketSoporte, RespuestaClasificacion
from .acciones import motor_inferencia, sugerir_tecnico, obtener_solucion_sugerida
from .base_conocimiento import REGLAS_CLASIFICACION, MAPEO_TECNICOS

__all__ = [
	"TicketSoporte",
	"RespuestaClasificacion",
	"motor_inferencia",
	"sugerir_tecnico",
	"obtener_solucion_sugerida",
	"REGLAS_CLASIFICACION",
	"MAPEO_TECNICOS",
]

