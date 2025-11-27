from pydantic import BaseModel, Field

# --- MODELO DE ENTRADA (HECHOS) ---

# Define la estructura de datos que recibe la API. 
class TicketSoporte(BaseModel):
    # Palabras clave de Hardware
    pc_no_enciende: bool = False
    periferico_roto: bool = False
    
    # Palabras clave de Red
    no_puede_conectar_wifi: bool = False
    sin_acceso_internet: bool = False
    
    # Palabras clave de Software/Sistema Operativo
    programa_se_cierra: bool = False
    lentitud_sistema: bool = False
    
    # Palabras clave de Permisos
    acceso_denegado: bool = False
    no_puede_instalar: bool = False
    
    # Palabras clave de Seguridad
    email_sospechoso: bool = False

# --- MODELO DE SALIDA (RESPUESTA) ---

# Define la estructura de la respuesta que devuelve la API.
class RespuestaClasificacion(BaseModel):
    categoria: str
    tecnico_responsable: str
    mensaje: str = "Ticket clasificado exitosamente."
    detalles: dict = Field(default_factory=dict)
    