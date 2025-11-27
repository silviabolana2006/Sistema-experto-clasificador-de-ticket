# experto_general/base_conocimiento.py

# --- Base de Conocimiento (Reglas de Clasificación) ---

REGLAS_CLASIFICACION = [
    # Reglas de Hardware
    {
        "id": "R-HW-PSU-01",
        "titulo": "Fuente de poder falla",
        "descripcion": "Si hay síntomas de falla de PSU (apagones, no arranca, clicks), clasificar como Hardware.",
        "condicion": lambda h: h.get("psu_falla", False),
        "resultado": "Hardware",
        "solucion": "Probar con PSU conocida o tester, revisar cables del panel frontal y cortos.",
        "soluciones": [
            "Probar con otra PSU o medir voltajes con tester.",
            "Revisar conectores ATX/EPS/PCIe y panel frontal.",
            "Descartar corto desconectando periféricos."
        ],
        "sugerencias_futuras": [
            "Si falla bajo carga, reemplazar PSU por modelo certificado.",
            "Registrar lote/modelo por trazabilidad."
        ]
    },
    {
        "id": "R-HW-THERM-01",
        "titulo": "Sobrecalentamiento",
        "descripcion": "Si hay temperaturas elevadas o thermal throttling, clasificar como Hardware.",
        "condicion": lambda h: h.get("sobrecalentamiento", False),
        "resultado": "Hardware",
        "solucion": "Limpiar ventiladores/disipadores, renovar pasta térmica y mejorar flujo de aire.",
        "soluciones": [
            "Limpiar polvo y renovar pasta térmica.",
            "Revisar flujo/curvas de ventilación y filtros.",
            "Verificar montaje del disipador y espacios del gabinete."
        ],
        "sugerencias_futuras": [
            "Evaluar ventiladores adicionales o mejor disipador.",
            "Monitorear temperaturas con herramienta dedicada."
        ]
    },
    {
        "id": "R-HW-RAM-01",
        "titulo": "Memoria RAM defectuosa",
        "descripcion": "Si hay síntomas de RAM defectuosa (pitidos al arrancar, pantallazos aleatorios, pruebas fallidas), clasificar como Hardware.",
        "condicion": lambda h: h.get("ram_falla", False),
        "resultado": "Hardware",
        "solucion": "Probar módulos de RAM individualmente y con MemTest; limpiar contactos y revisar compatibilidad.",
        "soluciones": [
            "Ejecutar MemTest/Windows Memory Diagnostic.",
            "Probar módulos de RAM de a uno y en distintos slots.",
            "Limpiar contactos y revisar que estén bien asentados."
        ],
        "sugerencias_futuras": [
            "Escalar a laboratorio si las pruebas son inconclusas.",
            "Registrar lote/modelo para análisis de fallas."
        ]
    },
    {
        "id": "R-HW-DISK-01",
        "titulo": "Disco/almacenamiento con errores",
        "descripcion": "Si hay sectores reasignados, ruidos extraños o errores de lectura/escritura, clasificar como Hardware.",
        "condicion": lambda h: h.get("disco_falla", False),
        "resultado": "Hardware",
        "solucion": "Respaldar datos, verificar SMART, ejecutar diagnóstico del fabricante y considerar reemplazo.",
        "soluciones": [
            "Respaldar información crítica inmediatamente.",
            "Revisar SMART (CrystalDiskInfo, smartctl).",
            "Ejecutar diagnóstico oficial del fabricante.",
            "Cambiar cable SATA/puerto si aplica.",
            "Reemplazar unidad si persisten errores."
        ],
        "sugerencias_futuras": [
            "Programar migración a SSD si es disco mecánico antiguo.",
            "Registrar el incidente para mantenimiento preventivo."
        ]
    },
    {
        "id": "R-HW-MON-01",
        "titulo": "Monitor sin señal",
        "descripcion": "Si el monitor no enciende o no recibe señal, clasificar como Hardware.",
        "condicion": lambda h: h.get("monitor_sin_senal", False),
        "resultado": "Hardware",
        "solucion": "Verificar alimentación, cable y entrada de video seleccionada; probar con otro cable/monitor.",
        "soluciones": [
            "Comprobar que el monitor esté encendido y con brillo adecuado.",
            "Verificar cable y puerto (HDMI/DP/VGA) y entrada seleccionada.",
            "Probar con otro cable/monitor o equipo."
        ],
        "sugerencias_futuras": [
            "Evaluar reemplazo si el panel no enciende.",
            "Documentar el modelo/serie y síntoma."
        ]
    },
    {
        "id": "R-HW-01",
        "titulo": "PC no enciende",
        "descripcion": "Si la PC no enciende, clasificar como Hardware (posible fallo físico).",
        "condicion": lambda h: h.get("pc_no_enciende", False),
        "resultado": "Hardware",
        "solucion": "Revisar fuente de alimentación, conexiones y realizar diagnóstico de hardware.",
        # Nuevo: múltiples soluciones y sugerencias futuras
        "soluciones": [
            "Verificar cable de alimentación y regleta.",
            "Probar con otra toma de corriente o cable.",
            "Comprobar interruptor de la fuente de poder (PSU).",
            "Retirar y volver a asentar RAM/CPU/cables del panel frontal.",
            "Probar con fuente de poder conocida o tester."
        ],
        "sugerencias_futuras": [
            "Derivar a soporte avanzado/garantía si no enciende tras pruebas.",
            "Registrar el incidente para análisis de patrones de fallas."
        ]
    },
    {
        "id": "R-HW-02",
        "titulo": "Periférico roto",
        "descripcion": "Si un periférico crítico está roto (ratón/teclado), clasificar como Hardware.",
        "condicion": lambda h: h.get("periferico_roto", False),
        "resultado": "Hardware",
        "solucion": "Sustituir o reparar el periférico. Probar con otro puerto/maquina.",
        "soluciones": [
            "Probar el periférico en otro puerto USB/equipo.",
            "Actualizar/reinstalar drivers del fabricante.",
            "Verificar cableado o receptor inalámbrico.",
            "Reemplazar el periférico si persiste la falla."
        ],
        "sugerencias_futuras": [
            "Escalar a inventario para reposición.",
            "Registrar el incidente para control de stock."
        ]
    },
    {
        "id": "R-HW-VID-01",
        "titulo": "Tarjeta de video falla",
        "descripcion": "Si hay indicios de fallo de GPU (sin video, artefactos, cuelgues al iniciar gráficos), clasificar como Hardware.",
        "condicion": lambda h: h.get("tarjeta_video_falla", False),
        "resultado": "Hardware",
        "solucion": "Actualizar/reinstalar drivers de video (DDU en modo seguro), verificar cables/puertos y alimentación PCIe, revisar temperaturas/ventiladores y probar la tarjeta en otro equipo. Si persisten artefactos o pantallazos, considerar reemplazo.",
        "soluciones": [
            "Reinstalar drivers con DDU en modo seguro y luego instalar el último driver estable.",
            "Verificar alimentación PCIe/cables y que el GPU esté bien asentado.",
            "Revisar temperaturas con herramientas (HWInfo/MSI Afterburner).",
            "Probar en otro puerto/monitor/cable.",
            "Probar la tarjeta en otro equipo para descartar la placa."
        ],
        "sugerencias_futuras": [
            "Si persisten artefactos/pantallazos, evaluar reemplazo de GPU.",
            "Escalar a laboratorio para diagnóstico de hardware de video."
        ]
    },

    # Reglas de Red
    {
        "id": "R-RED-01",
        "titulo": "Problema de conexión WiFi / Internet",
        "descripcion": "Si no puede conectar al WiFi o no tiene acceso a Internet, clasificar como Red.",
        "condicion": lambda h: h.get("no_puede_conectar_wifi", False) or h.get("sin_acceso_internet", False),
        "resultado": "Red",
        "solucion": "Verificar SSID, credenciales, DHCP, y estado del router/switch.",
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
    },

    # Reglas de Software
    {
        "id": "R-SW-UPD-01",
        "titulo": "Actualizaciones fallidas",
        "descripcion": "Si las actualizaciones de sistema/app fallan, clasificar como Software.",
        "condicion": lambda h: h.get("actualizaciones_fallidas", False),
        "resultado": "Software",
        "solucion": "Limpiar cachés/servicios de actualización y aplicar parche manual si es necesario.",
        "soluciones": [
            "Reiniciar servicios y limpiar caché de actualizaciones.",
            "Aplicar el instalador/patch manual oficial."
        ],
        "sugerencias_futuras": [
            "Revisar espacio, políticas y conectividad a repositorios.",
            "Programar ventana de mantenimiento para reintentos."
        ]
    },
    {
        "id": "R-SW-COMP-01",
        "titulo": "Incompatibilidad de software",
        "descripcion": "Si el software no es compatible con el SO/arquitectura, clasificar como Software.",
        "condicion": lambda h: h.get("incompatibilidad_software", False),
        "resultado": "Software",
        "solucion": "Usar versión compatible, modo compatibilidad o dependencias requeridas.",
        "soluciones": [
            "Ejecutar en modo compatibilidad o versión soportada.",
            "Instalar dependencias/SDK necesarios."
        ],
        "sugerencias_futuras": [
            "Consultar soporte del proveedor y matriz de compatibilidad.",
            "Valorar alternativa certificada por TI."
        ]
    },
    {
        "id": "R-SW-CORP-01",
        "titulo": "Aplicación corporativa falla/BD corrupta",
        "descripcion": "Si falla una aplicación corporativa o su BD presenta corrupción, clasificar como Software.",
        "condicion": lambda h: h.get("software_corporativo_falla", False),
        "resultado": "Software",
        "solucion": "Revisar logs de la app/servidor, restaurar backup y coordinar con el equipo de la aplicación.",
        "soluciones": [
            "Revisar logs y visor de eventos de la aplicación/BD.",
            "Validar versiones/compatibilidad y dependencias.",
            "Ejecutar scripts de reparación/consistencia si existen.",
            "Restaurar respaldo validado (previo análisis).",
            "Coordinar con equipo de la app para plan de recuperación."
        ],
        "sugerencias_futuras": [
            "Implementar validaciones y backups verificados.",
            "Agregar monitoreo de salud y alertas."
        ]
    },
    {
        "id": "R-SW-01",
        "titulo": "Programa se cierra / Lentitud",
        "descripcion": "Si un programa se cierra inesperadamente o el sistema está muy lento, clasificar como Software.",
        "condicion": lambda h: h.get("programa_se_cierra", False) or h.get("lentitud_sistema", False),
        "resultado": "Software",
        "solucion": "Revisar logs de la aplicación, actualizar/reinstalar el software o verificar recursos del sistema.",
        "soluciones": [
            "Revisar Visor de eventos/logs de la aplicación.",
            "Actualizar la aplicación y el sistema operativo.",
            "Ejecutar en inicio limpio/modo seguro para descartar conflictos."
        ],
        "sugerencias_futuras": [
            "Escalar al equipo de la aplicación con los logs adjuntos.",
            "Documentar el escenario y versión para reproducibilidad."
        ]
    },

    # Reglas de Permisos
    {
        "id": "R-PM-01",
        "titulo": "Problema de permisos / instalación",
        "descripcion": "Si hay acceso denegado o no puede instalar software, clasificar como Permisos.",
        "condicion": lambda h: h.get("acceso_denegado", False) or h.get("no_puede_instalar", False),
        "resultado": "Permisos",
        "solucion": "Revisar permisos del usuario y las políticas de control de aplicaciones.",
        "soluciones": [
            "Validar rol/pertenencia a grupos y ACLs.",
            "Solicitar elevación temporal si procede.",
            "Revisar GPO/AppLocker/Software Restriction Policies.",
            "Intentar instalación desde cuenta administrativa controlada."
        ],
        "sugerencias_futuras": [
            "Abrir ticket con seguridad/infra para permisos permanentes.",
            "Auditar intentos fallidos para mejorar políticas."
        ]
    },

    # Reglas de Seguridad
    {
        "id": "R-SEC-01",
        "titulo": "Email sospechoso",
        "descripcion": "Si se detecta un email sospechoso (posible phishing), clasificar como Seguridad.",
        "condicion": lambda h: h.get("email_sospechoso", False),
        "resultado": "Seguridad",
        "solucion": "Aislar el equipo, ejecutar análisis de seguridad y seguir protocolo de incidentes.",
        "soluciones": [
            "No abrir enlaces ni adjuntos; reportar inmediatamente.",
            "Aislar el equipo de la red si hubo interacción.",
            "Ejecutar escaneo con AV/EDR y cambiar credenciales.",
            "Seguir el playbook de respuesta a incidentes."
        ],
        "sugerencias_futuras": [
            "Capacitación anti-phishing al usuario/área.",
            "Revisión de reglas de correo y listas de bloqueo."
        ]
    },
    {
        "id": "R-SEC-MAL-01",
        "titulo": "Malware detectado",
        "descripcion": "Si hay infección o señales de malware, clasificar como Seguridad.",
        "condicion": lambda h: h.get("malware_detectado", False),
        "resultado": "Seguridad",
        "solucion": "Aislar equipo, escanear con EDR/AV y restaurar desde respaldo si es necesario.",
        "soluciones": [
            "Aislar equipo y ejecutar escaneo completo.",
            "Eliminar/quarantena; restaurar desde backup verificado."
        ],
        "sugerencias_futuras": [
            "Cambiar credenciales y revisar persistencia.",
            "Actualizar políticas y parches de seguridad."
        ]
    },
]

# --- Lógica del Técnico Responsable Sugerido (Datos) ---

MAPEO_TECNICOS = {
    "Hardware": "Técnico Juan (Especialista en HW/Periféricos)",
    "Red": "Técnica María (Especialista en Redes/Conectividad)",
    "Software": "Técnico Pedro (Especialista en Apps/Sistema Operativo)",
    "Permisos": "Técnica Ana (Administradora de Accesos)",
    "Seguridad": "Técnico Luis (Especialista en Ciberseguridad)",
    "Sin clasificar (General)": "Coordinador de Soporte"
}