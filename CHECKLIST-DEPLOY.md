# Checklist de Despliegue a Producción — Mercado Libre Research Suite
> **Estándar de Seguridad**: OWASP Top 10:2025  
> **Plataformas Homologadas**: Docker Compose + Nginx • Cloudflare Tunnel Zero Trust • VPS (Coolify/Hetzner/DigitalOcean) • Railway

Este documento es la lista de verificación obligatoria antes, durante y después del despliegue de la suite de investigación algorítmica.

---

## 1. Variables de Entorno de Producción (`.env`)

Copia la plantilla `.env.example` hacia `.env` en tu servidor o plataforma de hosting:

```bash
cp .env.example .env
```

| Variable | Tipo | Descripción | Recomendación |
| :--- | :--- | :--- | :--- |
| `POSTGRES_PASSWORD` | **Secret** | Contraseña de PostgreSQL | Generar con `openssl rand -hex 16` |
| `SECRET_KEY` | **Secret** | Clave para firma criptográfica HMAC-SHA256 | Generar con `openssl rand -hex 32` |
| `ADMIN_USERNAME` | Config | Nombre del usuario administrador | `admin` o personalizado |
| `ADMIN_PASSWORD` | **Secret** | Contraseña maestra inicial de acceso | Mínimo 14 caracteres con símbolos |
| `ML_CLIENT_ID` | Secret | ID de la App en Mercado Libre Developers | Obtenido de `developers.mercadolibre.com.mx` |
| `ML_CLIENT_SECRET` | **Secret** | Clave secreta de la App en Mercado Libre | Obtenido de `developers.mercadolibre.com.mx` |
| `ML_ACCESS_TOKEN` | Token | Token inicial de Mercado Libre | Generado en el flujo OAuth |
| `ML_REFRESH_TOKEN`| Token | Token para refresco automático cada 6h | Generado en el flujo OAuth |
| `AUTH_ENABLED` | Boolean | Activa el bloqueo perimetral estricto | `true` en Producción |

---

## 2. Métodos de Despliegue

### Opción A: Despliegue con Cloudflare Tunnel (Recomendado — Zero Trust)
*Ideal para hospedar en tu propio servidor local o VPS sin abrir puertos en el router, protegido por la red global de Cloudflare.*

1. **Instalar `cloudflared`**:
   ```bash
   brew install cloudflared  # en macOS
   # o en Linux: sudo apt-get install cloudflared
   ```
2. **Autenticar y Crear el Túnel**:
   ```bash
   cloudflared tunnel login
   cloudflared tunnel create ml-research
   ```
3. **Configurar el Enrutamiento (`~/.cloudflared/config.yml`)**:
   ```yaml
   tunnel: <TUNNEL_ID>
   credentials-file: /root/.cloudflared/<TUNNEL_ID>.json
   ingress:
     - hostname: research.tudominio.com
       service: http://localhost:80
     - service: http_status:404
   ```
4. **Vincular el DNS**:
   ```bash
   cloudflared tunnel route dns ml-research research.tudominio.com
   ```
5. **Iniciar los Contenedores y el Túnel**:
   ```bash
   docker compose -f docker-compose.prod.yml up -d --build
   cloudflared tunnel run ml-research
   ```

---

### Opción B: Despliegue en VPS Autónomo (Docker + Nginx)

1. **Clonar el Repositorio en el Servidor**:
   ```bash
   git clone <URL_REPOSITORIO> /opt/mercado-libre-research
   cd /opt/mercado-libre-research
   ```
2. **Crear archivo `.env` de Producción**:
   ```bash
   nano .env
   ```
3. **Compilar e Iniciar la Pila en Modo Producción**:
   ```bash
   docker compose -f docker-compose.prod.yml up -d --build
   ```
4. **Ejecutar Migraciones de Base de Datos**:
   ```bash
   docker compose -f docker-compose.prod.yml exec backend alembic upgrade head
   ```
5. **Verificar Estado de los Servicios**:
   ```bash
   docker compose -f docker-compose.prod.yml ps
   ```

---

### Opción C: Despliegue en PaaS (Railway / Coolify)

1. Conecta el repositorio de GitHub a tu proyecto en Railway o Coolify.
2. Añade un servicio de **PostgreSQL 16** y un servicio de **Redis 7**.
3. Despliega el backend apuntando al `Dockerfile` en `backend/` con las variables de entorno inyectadas en el dashboard.
4. Despliega el frontend configurando `VITE_API_URL` apuntando al backend.

---

## 3. Verificaciones de Seguridad Post-Deploy

- [ ] **Acceso Forzado Denegado**: Entra en modo incógnito a `https://tu-dominio.com/` y comprueba que redirige automáticamente a `/login`.
- [ ] **Protección contra Fuerza Bruta**: Ingresa 5 contraseñas erróneas intencionales; verifica que en el 5º intento el sistema responde `429 Too Many Requests` y bloquea la interfaz durante 60 segundos.
- [ ] **Validación de Cabeceras HTTP**:
  ```bash
  curl -I https://tu-dominio.com/health
  ```
  Comprueba la presencia de:
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: SAMEORIGIN`
  - `Server: Flamante-Engine`
- [ ] **Token Refresh de Mercado Libre**: Verifica en `docker logs <backend_container>` que el adaptador renueva el access token automáticamente usando `ML_CLIENT_ID` y `ML_CLIENT_SECRET`.
