# Sistema Académico Integral

## Tecnologías

- **Frontend:** React + Vite
- **Backend:** Python + Flask
- **Base de datos:** la que se configure en `DATABASE_URL`

## Requisitos previos

Antes de ejecutar el proyecto en otra computadora necesitas:

- **Python 3.10 o superior**
- **Node.js 18 o superior**
- **Git**
- **Una base de datos disponible** o una cadena de conexión válida en `DATABASE_URL`

Puedes verificar las versiones con:

```bash
python --version
node --version
npm --version
```

## Clonar el proyecto

```bash
git clone <URL-del-repositorio>
cd Evaluacion_Final_Sistema_Academico
```

## Configurar el backend

El backend está en la carpeta `Backend`.

1. Entra al backend:

```bash
cd Backend
```

2. Crea y activa un entorno virtual:

```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Si usas PowerShell y aparece el error de ejecución de scripts, ejecuta una sola vez:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

3. Instala las dependencias:

```bash
pip install -r requirements.txt
```

4. Crea un archivo `.env` dentro de `Backend` con al menos estas variables:

```env
DATABASE_URL=tu_cadena_de_conexion
JWT_SECRET_KEY=tu_clave_secreta
```

5. Si quieres levantar la base de datos desde cero y cargar datos de prueba, ejecuta:

```bash
python fresh.py
```

Este paso borra y recrea la base de datos, así que úsalo solo cuando quieras empezar limpio.

6. Para iniciar el servidor backend:

```bash
python run.py
```

El backend queda disponible en `http://127.0.0.1:5000`.

## Configurar el frontend

En otra terminal, dejando el backend corriendo:

```bash
cd Frontend
npm install
npm run dev
```

El frontend queda disponible en `http://localhost:5173`.

## Orden recomendado de ejecución

1. Configurar `.env` en `Backend`.
2. Instalar dependencias del backend con `pip install -r requirements.txt`.
3. Ejecutar `python fresh.py` si necesitas base nueva y datos semilla.
4. Ejecutar `python run.py` para levantar Flask.
5. Instalar dependencias del frontend con `npm install`.
6. Ejecutar `npm run dev` en `Frontend`.

## Equipo

- Coca Huari Mario
- Huaynate Achachau José Luis
- Ricardo Alexander Llanos Lozano
