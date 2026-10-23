# Política y Manual de Seguridad — Mercado Libre Research Suite
> **Estándar**: OWASP Top 10:2025  
> **Arquitectura**: FastAPI + PostgreSQL 16 + Redis + React 19 + Nginx

Este repositorio implementa un modelo de defensa en profundidad perimetral y perfiles criptográficos robustos para proteger la propiedad intelectual, cuotas de APIs externas y el acceso a la base de datos de análisis.

---

## 1. Contacto de Seguridad y Divulgación Responsable
Si descubres una vulnerabilidad de seguridad en esta plataforma o en sus APIs, por favor repórtala de inmediato a:
- **Correo**: `seguridad@flamante.lab` (o `admin@flamante.lab`)
- **Respuesta estimada**: Menos de 24 horas hábiles.
- Por favor, no reveles públicamente ninguna vulnerabilidad antes de que haya sido mitigada.

---

## 2. Arquitectura de Seguridad Implementada

### FASE 1 — Secretos y Aislamiento de Credenciales ✅
- **Exclusión en Git**: Se configuró `.gitignore` para bloquear `.env`, `.env.*`, archivos de claves privadas (`*.key`, `*.pem`), certificados y bases de datos locales.
- **Plantilla Segura (`.env.example`)**: Documentación exhaustiva de variables obligatorias (`SECRET_KEY`, `ADMIN_PASSWORD`, `DATABASE_URL`, `ML_CLIENT_ID`, `ML_CLIENT_SECRET`) sin exponer valores reales.
- **Fail-Safe de Tokens ML**: Rotación automática y fallback algorítmico paramétrico en caso de vencimiento del token de Mercado Libre (6 horas).

---

### FASE 2 — Autenticación Robusta y Gestión de Sesiones ✅
- **Hashing Criptográfico Estándar NIST (PBKDF2-HMAC-SHA256)**:
  - En `backend/app/security.py`, las contraseñas se hashean utilizando PBKDF2 con **100,000 iteraciones** y un salt criptográfico aleatorio único de 16 bytes (`secrets.token_hex(16)`).
  - Nunca se almacenan contraseñas en texto plano ni se utilizan algoritmos deprecados como MD5 o SHA-1.
- **Tokens de Acceso a Prueba de Manipulación (HMAC-SHA256)**:
  - Tokens firmados criptográficamente con tiempo de expiración estricto (`exp`) de **8 horas**.
  - Identificador único de sesión (`jti` vía `secrets.token_urlsafe(16)`) para prevenir replay attacks.
  - Verificación en tiempo constante (`secrets.compare_digest`) para prevenir ataques de canal lateral (*timing attacks*).
- **Protección contra Enumeración de Usuarios**:
  - Tanto si el usuario no existe como si la contraseña es errónea, el sistema responde siempre con el mensaje neutral:
    `"Credenciales no válidas. Verifica tus datos de acceso."` (código HTTP `401 Unauthorized`).

---

### FASE 3 — Protección contra Fuerza Bruta y Trampas Anti-Bot ✅
- **Bloqueo Progresivo contra Ataques de Diccionario (`app/security_middleware.py`)**:
  - Límite estricto de **5 intentos fallidos consecutivos** por dirección IP / usuario.
  - Al 5º intento fallido, el sistema activa un **bloqueo temporal de 60 segundos** (`429 Too Many Requests`).
  - Cabecera estándar de respuesta: `Retry-After: 60`.
  - La interfaz de usuario muestra un temporizador reactivo bloqueando el botón de envío hasta que se cumpla el período.
- **Trampas Honeypot Invisibles contra Rastreadores**:
  - El formulario de login incluye un campo trampa oculto (`honeypot`). Si un bot automatizado o scraper lo llena al rastrear el DOM, la solicitud es rechazada de inmediato (`400 Bad Request`) sin consultar la base de datos ni revelar detalles internos.

---

### FASE 4 — Cabeceras de Seguridad HTTP y Blindaje Perimetral ✅
El middleware perimetral (`SecurityHeadersMiddleware`) inyecta en cada respuesta HTTP:
- `X-Content-Type-Options: nosniff`: Previene ataques de confusión MIME.
- `X-Frame-Options: SAMEORIGIN`: Protege contra incrustación en iframes maliciosos y Clickjacking.
- `X-XSS-Protection: 1; mode=block`: Activa el filtro contra Cross-Site Scripting reflejado.
- `Referrer-Policy: strict-origin-when-cross-origin`: Oculta parámetros de URL interna al salir a enlaces externos de Mercado Libre.
- `Permissions-Policy: camera=(), microphone=(), geolocation=()`: Deshabilita hardware no requerido.
- `Server: Flamante-Engine`: Enmascara las firmas de servidor (Uvicorn / Python) para dificultar el reconocimiento pasivo.

---

### FASE 5 — Control Perimetral en Frontend (Protected Routes) ✅
- En `frontend/src/components/ProtectedRoute.jsx`, toda ruta de la suite (`/`, `/product/:id`, `/compare`, `/reports`) está protegida.
- Si el usuario no tiene una sesión válida y verificada, es redirigido inmediatamente a `/login`.
- Al recibir cualquier código `401 Unauthorized` desde la API, el cliente purga automáticamente las credenciales locales y redirige a la pantalla de acceso.
