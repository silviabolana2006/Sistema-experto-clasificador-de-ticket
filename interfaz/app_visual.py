from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os

app = FastAPI()

# Montar estáticos y templates
static_dir = os.path.join(os.path.dirname(__file__), 'static')
templates_dir = os.path.join(os.path.dirname(__file__), 'templates')

app.mount('/static', StaticFiles(directory=static_dir), name='static')
templates = Jinja2Templates(directory=templates_dir)


@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    """Página simple que puede cargar el frontend o redirigir al SPA."""
    return templates.TemplateResponse('index.html', {'request': request})


@app.get('/debug', response_class=HTMLResponse)
async def debug(request: Request):
    """Ruta mínima para comprobar que la app está sirviendo HTML correctamente."""
    html = """
    <!doctype html>
    <html lang="es">
      <head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Debug</title></head>
      <body><h1>Debug OK</h1><p>Si ves esto, la app responde.</p></body>
    </html>
    """
    return HTMLResponse(content=html)


@app.get('/raw_index', response_class=HTMLResponse)
async def raw_index(request: Request):
    """Devuelve el contenido bruto del template `index.html` para comparar con lo servido."""
    tpl_path = os.path.join(templates_dir, 'index.html')
    try:
        with open(tpl_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        content = f'Error leyendo template: {e}'
    return HTMLResponse(content=content)

# Nota: Este archivo es un entrypoint ligero para integrar la UI con el backend.
# Puedes ejecutar con: python -m uvicorn interfaz.app_visual:app --reload
