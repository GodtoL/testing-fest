# Servidor de Chat - Suite de Pruebas

## Descripción del Proyecto
Implementación de un servidor de chat con pruebas exhaustivas usando programación de sockets en Python y el framework pytest. La suite de pruebas valida diversos aspectos de la funcionalidad del servidor de chat.

## Características
- Servidor de chat basado en sockets
- Soporte para múltiples conexiones de clientes
- Difusión de mensajes
- Manejo de errores y gestión de conexiones

## Requisitos Previos
- Python 3.8+
- pytest
- Biblioteca socket

## Instalación
1. Clonar el repositorio
2. Instalar dependencias:
   ```bash
   pip install pytest
   ```

## Suite de Pruebas

### Escenarios de Prueba
La suite cubre los siguientes escenarios:

1. **Pruebas de Conexión de Clientes**
   - Conexión exitosa al host y puerto correctos
   - Manejo de conexiones con host/puerto incorrectos

2. **Difusión de Mensajes**
   - Envío de mensajes a múltiples clientes

3. **Pruebas de Conexión Múltiple**
   - Conexión simultánea de varios clientes
   - Verificación de la estabilidad del servidor

4. **Pruebas de Desconexión**
   - Manejo de desconexiones abruptas
   - Capacidad de reconexión del servidor

## Ejecución de Pruebas
Para ejecutar las pruebas, use:
```bash
pytest test_chat_server.py
```

## Estructura del Proyecto
- `chatserver.py`: Implementación del servidor de chat
- `test_chat_server.py`: Pruebas unitarias y de integración
