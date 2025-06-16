# 🐳 Instrucciones de Docker - ETCAR Sistema de Automatización

Este documento contiene los comandos básicos para gestionar el contenedor Docker del sistema ETCAR.

## 📋 Requisitos Previos
- Docker instalado en el sistema
- Terminal/PowerShell con permisos de administrador

---

## 🚀 Comandos Básicos

### 1. Construir la Imagen
```bash
docker build . -t excel
```
**Descripción**: Construye la imagen Docker usando el Dockerfile del directorio actual y la etiqueta como "excel".

### 2. Ejecutar el Contenedor
```bash
docker run --name excel-container -p 8000:8000 excel
```
**Descripción**: Crea y ejecuta un contenedor llamado "excel-container" mapeando el puerto 8000 del host al puerto 8000 del contenedor.

---

## 🔄 Gestión del Contenedor

### Parar el Contenedor
```bash
docker stop excel-container
```

### Iniciar el Contenedor (después de haberlo parado)
```bash
docker start excel-container
```

### Reiniciar el Contenedor
```bash
docker restart excel-container
```

### Ver el Estado del Contenedor
```bash
docker ps -a
```

---

## 🔧 Actualización del Contenedor

### Opción 1: Actualizar con Rebuild Completo
```bash
# 1. Parar el contenedor actual
docker stop excel-container

# 2. Eliminar el contenedor
docker rm excel-container

# 3. Construir nueva imagen
docker build . -t excel

# 4. Ejecutar nuevo contenedor
docker run --name excel-container -p 8000:8000 excel
```

### Opción 2: Script de Actualización Rápida
```bash
# Comando único para parar, eliminar, reconstruir y ejecutar linux/mac
docker stop excel-container && docker rm excel-container && docker build . -t excel && docker run --name excel-container -p 8000:8000 excel
```
``` powershell
# Comando único para parar, eliminar, reconstruir y ejecutar Windows
docker stop excel-container; docker rm excel-container; docker build . -t excel; docker run --name excel-container -p 8000:8000 excel
```

---

## 🧹 Limpieza (Opcional)

### Eliminar Contenedor
```bash
docker rm excel-container
```

### Eliminar Imagen
```bash
docker rmi excel
```

### Limpiar Imágenes No Utilizadas
```bash
docker image prune
```

### Limpiar Todo el Sistema Docker
```bash
docker system prune -a
```

---

## 📝 Comandos Útiles

### Ver Logs del Contenedor
```bash
docker logs excel-container
```

### Ver Logs en Tiempo Real
```bash
docker logs -f excel-container
```

### Ver Información del Contenedor
```bash
docker inspect excel-container
```

---

## 🌐 Acceso a la Aplicación

Una vez que el contenedor esté ejecutándose, puedes acceder a la aplicación en:
- **URL**: http://localhost:8000
- **Puerto**: 8000


---

## 📚 Referencias
- [Documentación oficial de Docker](https://docs.docker.com/)
- [Docker Compose (para proyectos más complejos)](https://docs.docker.com/compose/)

---

