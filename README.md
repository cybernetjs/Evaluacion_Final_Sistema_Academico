# Sistema Académico Integral

Sistema Académico

Universidad Nacional del Centro del Perú, Facultad de Ingeniería de Sistemas.

## Equipo

- Coca Huari Mario
- Huaynate Achachau José Luis
- Ricardo Alexander Llanos Lozano

## Tecnologías

**Frontend**
- React 19 + Vite
- React Router DOM (enrutamiento)
- Recharts (gráficos y dashboards)

**Backend**
- Python + Flask
- SQLAlchemy (ORM) + Flask-Migrate (migraciones de base de datos)
- Flask-JWT-Extended (autenticación por token)
- Flask-Bcrypt (hash de contraseñas)
- ReportLab + qrcode (generación de fichas y certificados en PDF con código QR)

**Base de datos**
- MySQL (la cadena de conexión se configura en `DATABASE_URL`)

---

## Arquitectura del sistema

El sistema sigue una arquitectura general de cliente-servidor .


- La comunicación entre frontend y backend se hace exclusivamente vía **HTTP + JSON**.
- La sesión del usuario se maneja con **JWT** (JSON Web Token).
- El backend valida cada endpoint protegido según el **rol** del usuario contenido en el token.
- CORS está configurado en el backend para aceptar peticiones únicamente desde los orígenes del frontend (desarrollo y producción).

### Arquitectura interna del backend (por capas)

Usa la aruitectura por capas modular con algunos elementos de la hexagonal

El backend separa responsabilidades en tres capas dentro de cada módulo de negocio.

```
app/
├── dominio/modelos/        → Modelos ORM: representan las tablas de la base de datos
├── modulos/<modulo>/
│   ├── aplicacion/
│   │   └── servicios.py    → Lógica de negocio (reglas, validaciones, uso del ORM)
│   └── presentacion/
│       ├── controladores.py→ Recibe la petición HTTP y arma la respuesta JSON
│       └── rutas.py        → Define los endpoints (Blueprint de Flask)
├── compartido/
│   └── middlewares/        → Ej: control de acceso por rol (rol_requerido)
└── seeders/                → Datos de prueba para poblar la base de datos
```

Recorrido de endpoint : **ruta → controlador → servicio → modelo (ORM) → base de datos**, y 
la respuesta regresa por el mismo camino en sentido inverso, como JSON.

### Estructura del frontend

```
Frontend/src/
├── modulos/
│   ├── autenticacion/
│   ├── matricula/
│   ├── cursos/
│   ├── notas/
│   ├── record-academico/
│   ├── certificados/
│   └── administracion/
│       └── <cada módulo tiene>: paginas/  componentes/  servicios/  rutas.jsx
├── nucleo/
│   ├── contexto/AuthContext.jsx   → guarda el usuario y el token de sesión
│   ├── servicios/api.js           → función centralizada para llamar al backend
│   ├── componentes/comunes/       → Navbar, RutaProtegida, etc.
│   └── hooks/
└── enrutador/index.jsx            → une las rutas de todos los módulos
```

Cada módulo del frontend es independiente y expone sus propias rutas, que luego se combinan en `enrutador/index.jsx`. 
El acceso a cada ruta está protegido por rol mediante el componente `RutaProtegida`, y el menú de navegación se arma 
dinámicamente según el rol , y use arquitectura modular basada en funcionalidades. 

### Módulos implementados

| Módulo | Descripción | Roles que interactúan |
|---|---|---|
| Autenticación | Login, registro y sesión con JWT | Todos |
| Matrícula | Solicitud, validación, pagos y ficha oficial | Estudiante, Administrador, Dirección |
| Cursos y Docentes | Asignación de cursos, horarios y sílabos | Docente, Administrador, Dirección |
| Notas | Registro y consulta de notas parciales/finales | Docente, Estudiante, Administrador, Dirección |
| Récord Académico | Historial académico y reportes | Estudiante, Administrador, Dirección |
| Certificados y Documentos | Solicitud, aprobación y firma digital con QR | Estudiante, Administrador, Dirección |
| Administración y Seguridad | Usuarios, roles, permisos y auditorías | Administrador, Dirección |

### Seguridad y control de acceso por roles

El sistema define 4 roles: **estudiante**, **docente**, **administrador** y **dirección**. Cada endpoint del backend está protegido con un middleware (`rol_requerido`) que:

1. Verifica que el token JWT sea válido.
2. Comprueba que el rol del usuario esté autorizado para ese endpoint, ya sea por rol fijo o contra una **matriz de permisos** configurable (tabla de permisos por rol y recurso, editable desde el módulo de Administración).

En el frontend, esto se refuerza con rutas protegidas: un usuario no puede navegar a una pantalla que no le corresponde, y el menú solo muestra las opciones habilitadas para su rol.

---

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
DATABASE_URL=mysql+pymysql://USUARIO:CONTRASEÑA@HOST/NOMBRE_BASE_DE_DATOS
```

5. Si quieres levantar la base de datos desde cero y cargar datos de prueba, ejecuta:

```bash
python fresh.py
```

Este paso borra y recrea la base de datos.

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

---

## Credenciales de prueba

Al ejecutar `python fresh.py`, el seeder de usuarios (`app/seeders/identidad/usuario_seeder.py`) crea automáticamente los siguientes usuarios de prueba, uno por cada rol del sistema. Todos usan la misma contraseña: **`123456`**.

| Rol | Usuario | Contraseña |
|---|---|---|
| Estudiante | `estudiante_prueba` | `123456` |
| Estudiante | `estudiante_prueba2` | `123456` |
| Estudiante | `estudiante_prueba3` | `123456` |
| Estudiante | `estudiante_prueba4` | `123456` |
| Docente | `docente_prueba` | `123456` |
| Docente | `docente_prueba2` | `123456` |
| Docente | `docente_prueba3` | `123456` |
| Docente | `docente_prueba4` | `123456` |
| Administrador | `admin_prueba` | `123456` |
| Dirección | `direccion_prueba` | `123456` |

