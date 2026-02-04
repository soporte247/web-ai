# DataShark

DataShark es una plataforma para crear juegos 3D completos desde texto, usando Unity como motor principal y un backend de IA local para generar mundos, misiones y assets.

## Objetivo
- Crear juegos 3D para escritorio (Windows, Mac, Linux) y móvil (Android/iOS).
- Generar mundos, niveles, misiones, NPCs y assets con IA.
- Soporte opcional para AR/VR y multiplayer competitivo/cooperativo.

## Estructura
- DataShark_unity_project: proyecto Unity (carpetas base).
- backend: servicio FastAPI para orquestación IA.

## Backend (FastAPI)
1. Configura variables en .env (usa .env.example como guía).
2. Instala dependencias.
3. Inicia el servidor en el directorio backend.

### Endpoint de ejemplo
- GET /sample entrega un ejemplo de request/response para Unity.

## Frontend Web (Next.js + Three.js)
1. Entra a DataShark_unity_project.
2. Instala dependencias y ejecuta el frontend.
3. Abre la app en el navegador.

### Autenticación y biblioteca
- Registro e login en /auth
- Biblioteca de mundos guardados en /library
- Los mundos se guardan por usuario en la BD

### Variables de entorno web
- Usa DataShark_unity_project/.env.example como guía para NEXT_PUBLIC_API_BASE.

### Vista 3D
- La vista 3D se renderiza con Three.js y @react-three/fiber.
- El flujo de prompts y respuestas se hace desde la web.

## Notas
- Las integraciones reales con GPT, DALL·E, TTS y CLIP son stubs y deben conectarse a APIs reales.
- Este repositorio es un scaffold inicial para ampliar módulos, UI y pipeline de builds.
