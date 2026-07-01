# Sistema Académico Integral

**Desarrollo de Aplicaciones Web** — Facultad de Ingeniería de Sistemas, UNCP.

## Tecnologias

- **Frontend:** React + Vite
- **Backend:** Python + Flask
- **Base de datos:**  (pendiente)

## Requisitos previos

Antes de ejecutar el proyecto:

- **Python 3.10 o superior** → verificar con `python --version`
- **Node.js 18 o superior** (incluye npm) → verificar con `node --version` y `npm --version`
- **Git**

## Cómo clonar el proyecto

```bash
git clone <URL-del-repositorio>
cd Evaluacion_Final_Sistema_Academico
```

## Cómo correr el Backend (Flask)

```bash
cd Backend

# Crear el entorno virtual (solo la primera vez)
python -m venv venv

# Activar el entorno virtual
# En Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# En Mac/Linux:
source venv/bin/activate

# Instalar las dependencias
pip install -r requirements.txt

# Correr el servidor
python app.py
```


```
* Running on http://127.0.0.1:5000
```

Abre `http://localhost:5000` en el navegador :

> **Nota (Windows):** si `.\venv\Scripts\Activate.ps1` da un error de "ejecución de
> scripts deshabilitada", correr una sola vez:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```
> y responder `S` cuando pregunte.

## Cómo ejecutar el Frontend (React + Vite)

En otra terminal (dejando el backend corriendo en la primera):

```bash
cd Frontend
npm install
npm run dev
```

Abre `http://localhost:5173` en el navegador para ver el frontend.

## Equipo

- Coca Huari Mario
- Huaynate Achachau José Luis
- Ricardo Alexander Llanos Lozano
