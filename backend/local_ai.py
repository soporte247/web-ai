"""
Sistema de IA local basado en patrones y base de conocimiento
No requiere APIs externas
"""

import re
from typing import Dict, List, Any, Optional
import random


class LocalAI:
    """IA local con base de conocimiento predefinida"""
    
    def __init__(self):
        self.knowledge_base = self._init_knowledge_base()
        self.conversation_context = []
        
    def _init_knowledge_base(self) -> Dict[str, Any]:
        """Base de conocimiento con patrones y respuestas"""
        return {
            "saludos": {
                "patterns": [
                    r"\b(hola|hey|buenas|saludos|que tal|como estas)\b",
                ],
                "responses": [
                    "¡Hola! Soy tu asistente de DataShark. ¿En qué puedo ayudarte hoy?",
                    "¡Saludos! Estoy aquí para ayudarte con la creación de mundos 3D.",
                    "¡Hola aventurero! ¿Listo para crear mundos increíbles?"
                ]
            },
            "crear_mundo": {
                "patterns": [
                    r"\b(crear|generar|hacer|construir).*(mundo|juego|nivel|escenario)\b",
                    r"\b(como|quiero|puedo).*(crear|hacer).*(mundo|juego)\b"
                ],
                "responses": [
                    "Para crear un mundo: 1) Escribe una descripción en el campo 'Prompt' (ej: 'Ciudad cyberpunk con lluvia neon'). 2) Selecciona plataformas. 3) Haz clic en 'Generar mundo'. ¡Así de simple!",
                    "¡Crear mundos es fácil! Solo describe lo que imaginas en el campo de texto arriba y presiona 'Generar mundo'. Por ejemplo: 'Bosque místico con elfos y dragones'.",
                    "Te guío: Describe tu mundo (ej: 'Estación espacial abandonada'), elige configuraciones y genera. El sistema creará biomas, NPCs, enemigos y misiones automáticamente."
                ]
            },
            "guardar": {
                "patterns": [
                    r"\b(como|donde|puedo).*(guardar|salvar|save)\b",
                    r"\b(guardar|salvar).*(partida|juego|progreso)\b"
                ],
                "responses": [
                    "Para guardar tu progreso: Ve al panel lateral → 'Guardado rápido' → Botón 'Guardar partida'. O accede a Biblioteca → Tab '💾 Partidas guardadas' para gestionar 10 slots.",
                    "Tienes 10 slots de guardado. Haz clic en 'Guardar partida' en el sidebar o ve a la biblioteca para ver todas tus partidas guardadas.",
                    "Guardado automático disponible. Usa el botón de guardado rápido o ve a 'Partidas guardadas' en la biblioteca para gestionar tus saves."
                ]
            },
            "logros": {
                "patterns": [
                    r"\b(logros|achievements|desbloquear|trofeos)\b",
                    r"\b(como|ver|obtener).*(logros|achievements)\b"
                ],
                "responses": [
                    "¡Tenemos 10 logros! Accede desde Biblioteca → Tab '🏆 Logros'. Algunos: Crear tu primer mundo (10 pts), Subir un asset (30 pts), Jugar en VR (50 pts). ¡Desbloquéalos todos!",
                    "Los logros se desbloquean automáticamente al cumplir acciones. Ve a la pestaña de logros para ver tu progreso y cuántos puntos llevas.",
                    "Sistema de logros activo con 10 achievements. Desde crear mundos hasta jugar en VR. Revisa la biblioteca para ver cuáles te faltan."
                ]
            },
            "assets": {
                "patterns": [
                    r"\b(subir|upload|cargar).*(asset|modelo|textura)\b",
                    r"\b(custom|personalizado).*(asset|modelo)\b"
                ],
                "responses": [
                    "Sube tus propios assets: Biblioteca → Tab '⚙️ Custom Assets' → Completa el formulario con nombre, tipo (modelo/textura/audio), archivo y descripción. ¡Comparte con la comunidad!",
                    "Puedes subir modelos 3D (.glb), texturas (.png) o audio (.mp3). Ve a Custom Assets, llena el formulario y marca 'Hacer público' si quieres compartir.",
                    "Sistema de modding activo. Sube assets personalizados y explora los de otros usuarios. Todo en la pestaña 'Custom Assets'."
                ]
            },
            "combate": {
                "patterns": [
                    r"\b(combate|pelea|lucha|batalla|atacar)\b",
                    r"\b(skills|habilidades|combos)\b"
                ],
                "responses": [
                    "Sistema de combate disponible: Light Attack (10 dmg), Heavy Attack (25 dmg), Block (50% reducción), Dodge. Combos: Quick Strike, Power Slam, Counter. ¡Abre el panel de combate!",
                    "Árbol de habilidades con 3 clases: Warrior (fuerza), Mage (magia), Rogue (sigilo). Cada una con 3 skills mejorables hasta nivel 5. Usa puntos de habilidad para mejorar.",
                    "Combate en tiempo real con combos. Light + Light = Quick Strike (+5 dmg). Heavy + Light = Power Slam (+15 dmg). Block + Heavy = Counter (+20 dmg)."
                ]
            },
            "inventario": {
                "patterns": [
                    r"\b(inventario|items|objetos|pociones)\b",
                    r"\b(como|usar).*(items|pociones|inventario)\b"
                ],
                "responses": [
                    "Inventario visual disponible. Abre el panel de combate para ver tus items. Click en cualquier item para usarlo. Las pociones restauran 30 HP instantáneamente.",
                    "Tu inventario inicial incluye: Espada básica, Armadura de cuero, 3 pociones de vida. Recoge más items explorando el mundo. Cada uno tiene su función.",
                    "Sistema de inventario interactivo. Click en items para usar. Las pociones se consumen automáticamente y restauran salud. Encuentra más explorando."
                ]
            },
            "vr_ar": {
                "patterns": [
                    r"\b(vr|realidad virtual|oculus|quest)\b",
                    r"\b(ar|realidad aumentada)\b"
                ],
                "responses": [
                    "Modo VR/AR compatible con WebXR. Necesitas un headset VR (Oculus Quest, Valve Index, etc). Haz clic en '🥽 Modo VR' en el sidebar para activarlo.",
                    "Soporte WebXR activado: Hand tracking, spatial audio, teleportation. Conecta tu headset VR y presiona el botón VR. ¡Desbloquea el logro 'VR Pioneer'!",
                    "AR disponible en dispositivos compatibles. El sistema detecta automáticamente si tu navegador soporta WebXR. Prueba ambos modos desde el panel."
                ]
            },
            "explorar": {
                "patterns": [
                    r"\b(explorar|ver|buscar).*(mundos|comunidad|publicos)\b",
                    r"\b(mundos|worlds).*(publicos|otros|comunidad)\b"
                ],
                "responses": [
                    "Explora mundos de otros usuarios: Biblioteca → Tab '🌍 Explorar comunidad'. Ordena por populares, recientes o más gustados. Dale like y juega mundos públicos.",
                    "La comunidad ha creado mundos increíbles. Ve a 'Explorar comunidad' para verlos, jugarlos y dar likes. También puedes publicar los tuyos.",
                    "Sistema social activo. Publica tus mundos (botón Publicar), explora los de otros, da likes, compite en leaderboards. ¡Construye tu reputación!"
                ]
            },
            "fisica": {
                "patterns": [
                    r"\b(fisica|colisiones|gravedad|destruir)\b",
                    r"\b(objetos|destructibles|romper)\b"
                ],
                "responses": [
                    "Motor de física Cannon.js integrado. Gravedad: -9.81, colisiones realistas, objetos destructibles activados. Algunos obstáculos se pueden romper.",
                    "Física avanzada: Ragdoll para enemigos, colisiones continuas, objetos destructibles marcados con brillo rojo. Rompe cajas y paredes para encontrar secretos.",
                    "Sistema de física completo. Los enemigos caen con ragdoll, los objetos rebotan, las explosiones afectan el entorno. Todo calculado en tiempo real."
                ]
            },
            "leaderboard": {
                "patterns": [
                    r"\b(leaderboard|ranking|tabla|puntaje|score)\b",
                    r"\b(competir|mejor|puntuacion)\b"
                ],
                "responses": [
                    "Cada mundo tiene su leaderboard. Juega mundos públicos, completa misiones, acumula puntos y envía tu score. Compite con otros jugadores globalmente.",
                    "Sistema de rankings por mundo. Tus mejores scores se guardan automáticamente. Ve el leaderboard con el botón '🏆' en cada mundo público.",
                    "Puntuación basada en: misiones completadas, tiempo de juego, enemigos derrotados, items recolectados. ¡Sé el número 1!"
                ]
            },
            "ayuda_general": {
                "patterns": [
                    r"\b(ayuda|help|auxilio|no se|no entiendo)\b",
                    r"\b(que|como).*(hacer|funciona|usar)\b"
                ],
                "responses": [
                    "Aquí está la guía rápida:\n\n1. CREAR: Describe tu mundo y genera\n2. GUARDAR: Usa el botón de guardado rápido\n3. EXPLORAR: Ve a la biblioteca para ver mundos\n4. LOGROS: Desbloquea achievements jugando\n5. ASSETS: Sube contenido personalizado\n\n¿Qué te gustaría hacer primero?",
                    "Funciones principales disponibles:\n• Generar mundos 3D con IA\n• Sistema de guardado (10 slots)\n• Logros y achievements\n• Custom assets y modding\n• Combate con skills\n• Modo VR/AR\n• Comunidad y leaderboards\n\nPregúntame sobre cualquiera.",
                    "DataShark te permite crear juegos 3D completos solo con texto. Genera mundos, guarda progreso, desbloquea logros, sube assets personalizados, juega en VR y compite con la comunidad. ¿Por dónde empezamos?"
                ]
            },
            "despedida": {
                "patterns": [
                    r"\b(adios|chao|hasta luego|bye|nos vemos)\b",
                ],
                "responses": [
                    "¡Hasta pronto! Sigue creando mundos increíbles. 🦈",
                    "¡Nos vemos! No olvides guardar tu progreso. 👋",
                    "¡Adiós aventurero! Vuelve cuando quieras crear más mundos. 🎮"
                ]
            },
            "agradecimiento": {
                "patterns": [
                    r"\b(gracias|thanks|muchas gracias|te lo agradezco)\b",
                ],
                "responses": [
                    "¡De nada! Estoy aquí para ayudarte siempre. 😊",
                    "¡Un placer ayudarte! Pregúntame lo que necesites. 🦈",
                    "¡Para eso estoy! Disfruta creando mundos. 🎮"
                ]
            },
            "temas": {
                "patterns": [
                    r"\b(que|cuales).*(temas|themes|estilos)\b",
                    r"\b(temas|themes).*(disponibles|hay|puedo|usar)\b"
                ],
                "responses": [
                    "Puedes usar cualquier tema: ciencia ficción, fantasía, terror, medieval, cyberpunk, steampunk, apocalíptico, espacial, submarino, etc. ¡Tu imaginación es el límite!",
                    "Temas populares: 🔮 Fantasía épica, 🚀 Ciencia ficción, 👻 Terror survival, ⚔️ Medieval, 🤖 Cyberpunk, ⚙️ Steampunk, 🧟 Post-apocalíptico. Describe lo que quieras crear.",
                    "DataShark soporta todos los temas. Escribe en el campo 'Tema': fantasía, sci-fi, horror, western, etc. El sistema generará biomas, NPCs y enemigos acordes."
                ]
            },
            "plataformas": {
                "patterns": [
                    r"\b(plataformas|platforms|donde).*(jugar|ejecutar|funciona)\b",
                    r"\b(windows|mac|linux|android|ios|web)\b"
                ],
                "responses": [
                    "DataShark genera mundos para múltiples plataformas: 💻 Windows, 🍎 Mac, 🐧 Linux, 📱 Android, 📲 iOS. Selecciona las que quieras al generar.",
                    "Exporta para todas las plataformas: PC (Windows/Mac/Linux), móviles (Android/iOS) y web. El sistema optimiza automáticamente para cada una.",
                    "Compatible con: Desktop (Win/Mac/Linux), Mobile (Android/iOS), Web (navegadores modernos). Marca las plataformas deseadas antes de generar."
                ]
            },
            "exportar": {
                "patterns": [
                    r"\b(exportar|export|descargar|download).*(json|gltf|archivo|file)\b",
                    r"\b(como).*(exportar|descargar)\b"
                ],
                "responses": [
                    "Para exportar: Ve al panel lateral → Panel 'Herramientas' → 'Exportación'. Opciones: JSON (datos del mundo) o glTF (modelo 3D). Descarga y úsalo donde quieras.",
                    "Formatos de exportación:\n📦 JSON - Estructura completa del mundo\n🎨 glTF - Modelo 3D para Unity/Unreal/Blender\n\nEncuéntralos en el panel de Herramientas del sidebar.",
                    "Exporta tu mundo fácilmente. Abre el acordeón 'Herramientas' en el sidebar y elige: JSON (para guardar/compartir datos) o glTF (para importar en motores 3D)."
                ]
            },
            "multiplayer": {
                "patterns": [
                    r"\b(multiplayer|multijugador|cooperativo|competitivo|jugar).*(amigos|online|otros)\b",
                    r"\b(co-op|pvp|coop)\b"
                ],
                "responses": [
                    "Modo multiplayer disponible:\n🤝 Cooperativo - Juega con amigos contra enemigos\n⚔️ Competitivo - PvP y leaderboards\n\nSelecciona el modo antes de generar el mundo.",
                    "DataShark soporta multijugador. Elige modo cooperativo (co-op) o competitivo (PvP) en el selector de 'Modo multiplayer' antes de generar.",
                    "Juega con amigos: Configura modo multiplayer → Elige cooperativo/competitivo → Genera mundo. Comparte el mundo desde la biblioteca para jugar juntos."
                ]
            },
            "nivel_habilidad": {
                "patterns": [
                    r"\b(dificultad|difficulty|nivel).*(jugador|player|skill)\b",
                    r"\b(principiante|intermedio|avanzado|beginner|advanced)\b"
                ],
                "responses": [
                    "Niveles de jugador:\n🌱 Principiante - Mundos simples y tutoriales\n⚡ Intermedio - Desafío balanceado (default)\n🔥 Avanzado - Mundos complejos y difíciles\n\nCámbialo en el selector antes de generar.",
                    "La IA ajusta la complejidad según tu nivel:\n• Principiante: Enemigos débiles, misiones guiadas\n• Intermedio: Balance entre desafío y diversión\n• Avanzado: Bosses difíciles, misiones complejas",
                    "Configura tu nivel de habilidad en el selector. Principiante = más ayuda y enemigos fáciles. Avanzado = mundos complejos con desafíos extremos."
                ]
            },
            "biomas": {
                "patterns": [
                    r"\b(biomas|biomes|zonas|areas|regiones)\b",
                    r"\b(que|cuantos).*(biomas|zonas|areas)\b"
                ],
                "responses": [
                    "Cada mundo tiene 5 biomas únicos generados por IA:\n🌲 Bosques, 🏜️ Desiertos, 🏔️ Montañas, 🌊 Costas, 🏙️ Ciudades, etc.\n\nDependiendo del tema elegido, con NPCs, enemigos y misiones específicas por zona.",
                    "Sistema de biomas dinámico: 5 zonas por mundo. Ejemplo tema fantasía: Bosque Encantado, Pantano Maldito, Montaña Helada, Volcán Activo, Ciudad de Cristal.",
                    "Cada mundo genera 5 biomas únicos con:\n• Clima y terreno específico\n• NPCs con roles locales\n• Enemigos del bioma\n• Misiones contextuales\n• Buildings arquitectónicos"
                ]
            },
            "npc": {
                "patterns": [
                    r"\b(npc|npcs|personajes|characters).*(hablar|interactuar|que hacen)\b",
                    r"\b(que|quien).*(npc|personajes)\b"
                ],
                "responses": [
                    "NPCs inteligentes por bioma:\n👨‍🌾 Vendors - Venden items\n🧙 Quest Givers - Dan misiones\n👮 Guards - Protegen zonas\n🧝 Lore Masters - Cuentan historias\n\nCada uno con diálogos contextuales.",
                    "Los NPCs varían por zona y tema. Tienen roles: comerciantes, maestros de misiones, guardias, etc. Interactúa con ellos para obtener items, quests y lore.",
                    "Sistema de NPCs dinámico:\n• Generados según el tema del mundo\n• Roles específicos por bioma\n• Diálogos contextuales\n• Algunos hostiles, otros amigables\n• Esenciales para misiones"
                ]
            },
            "enemigos": {
                "patterns": [
                    r"\b(enemigos|enemies|mobs|monstruos).*(hay|tipos|cuantos)\b",
                    r"\b(combatir|luchar|pelear).*(contra|enemigos)\b"
                ],
                "responses": [
                    "Sistema de enemigos por tiers:\n🟢 Tier 1 - Comunes (fáciles)\n🟡 Tier 2 - Élite (medianos)\n🔴 Tier 3 - Jefes (difíciles)\n\nCada bioma tiene enemigos únicos del tema elegido.",
                    "Enemigos adaptativos: La IA genera monstruos según tu tema. Ej: Fantasía = goblins, orcos, dragones. Sci-fi = robots, aliens, drones. Con stats balanceados.",
                    "Combate enemigos de 3 tiers en cada bioma. Derrota comunes, enfrenta élites y conquista jefes finales. Usa el sistema de combate y skills del panel flotante."
                ]
            },
            "items": {
                "patterns": [
                    r"\b(items|objetos|loot).*(encontrar|conseguir|hay)\b",
                    r"\b(armas|armaduras|pociones|equipamiento)\b"
                ],
                "responses": [
                    "Sistema de items con rareza:\n⚪ Common - Básicos\n🟢 Uncommon - Mejores\n🔵 Rare - Poderosos\n🟣 Epic - Muy raros\n🟡 Legendary - Únicos\n\nEncuéntralos en el mundo o cómpralos a NPCs.",
                    "Loot por rareza con colores. Explora biomas para encontrar items legendarios. Úsalos en combate o véndelos. Sistema de inventario en el panel de combate.",
                    "Items generados por IA:\n• 15+ items por mundo\n• Rarity system con 5 niveles\n• Armas, armaduras, pociones, etc.\n• Visuales 3D con efectos brillantes\n• Gestión en inventario del panel flotante"
                ]
            },
            "skills": {
                "patterns": [
                    r"\b(skills|habilidades|talentos).*(tree|arbol|desbloquear)\b",
                    r"\b(como).*(mejorar|subir|skills)\b"
                ],
                "responses": [
                    "Skill Tree con 3 categorías:\n⚔️ Combate - Ataques y combos\n🛡️ Defensa - Resistencia y escudos\n✨ Especial - Habilidades únicas\n\n3 skills por categoría. Desbloquea con puntos de skill.",
                    "Sistema de progresión:\n1. Gana puntos matando enemigos\n2. Abre panel de combate (botón en sidebar)\n3. Ve a 'Skill Tree'\n4. Desbloquea habilidades de 3 ramas\n5. Usa combos en batalla",
                    "Árbol de habilidades con 9 skills totales. Distribuye puntos entre: Combate (daño), Defensa (tanque) o Especial (utilidad). Abre el panel flotante para gestionar."
                ]
            },
            "panel_colapsable": {
                "patterns": [
                    r"\b(paneles|acordeon|collapsed).*(abrir|cerrar|toggle)\b",
                    r"\b(donde|como).*(ver|encontrar).*(panel|herramientas)\b"
                ],
                "responses": [
                    "Paneles organizados con acordeones:\n📝 Editor & Visualización - Minimapa y misiones\n🤖 Asistente IA - Yo estoy aquí\n🛠️ Herramientas - Exportar, guardar, combate\n📚 Accesos rápidos - Logros y assets\n\nHaz clic en cada título para expandir/colapsar.",
                    "Sidebar reorganizado con acordeones colapsables. Clic en cualquier panel (Editor, Asistente, Herramientas, etc.) para abrir/cerrar. Mantén tu espacio limpio.",
                    "Los paneles ahora se colapsan. Haz clic en los títulos con ▼ para expandir/contraer secciones. Organiza tu espacio de trabajo como prefieras."
                ]
            },
            "quests": {
                "patterns": [
                    r"\b(quests|misiones|quest).*(hay|tipos|sistema)\b",
                    r"\b(como).*(hacer|completar).*(misiones|quests)\b"
                ],
                "responses": [
                    "Sistema de Quests con árboles de decisión:\n🎯 Misiones principales (main)\n🗺️ Misiones secundarias (side)\n📅 Desafíos diarios\n📆 Desafíos semanales\n\nTus elecciones afectan el desarrollo y recompensas.",
                    "Misiones dinámicas con múltiples caminos. Acepta quests, toma decisiones importantes y recibe recompensas. El sistema rastrea tu progreso en cada mundo.",
                    "Cada mundo genera misiones únicas. Completa objectives para ganar experiencia, items y monedas. Ve al panel de progreso para ver tus quests activas."
                ]
            },
            "crafting": {
                "patterns": [
                    r"\b(crafting|crear items|craft).*(funciona|sistema|como)\b",
                    r"\b(como).*(hacer|craftear|crear).*(items|objetos|armas)\b"
                ],
                "responses": [
                    "Sistema de Crafting:\n🔨 5 recetas base incluidas\n⚗️ Combina ingredientes\n⏱️ Tiempo de crafting\n📊 Nivel requerido\n\nCategorías: armas, armaduras, consumibles. Encuentra ingredientes explorando.",
                    "Crafting te permite crear items poderosos. Recolecta ingredientes, aprende recetas y fabrica equipo. Mejores recetas requieren nivel más alto.",
                    "Para craftear: 1) Reúne ingredientes 2) Ve al menu de crafting 3) Selecciona receta 4) Espera tiempo de creación. Experimenta combinando items raros."
                ]
            },
            "economia": {
                "patterns": [
                    r"\b(economia|monedas|comprar|vender|oro|dinero)\b",
                    r"\b(como).*(ganar|conseguir).*(dinero|monedas|oro)\b"
                ],
                "responses": [
                    "Sistema económico completo:\n💰 Gana monedas derrotando enemigos\n🛒 Compra items a NPCs vendedores\n💸 Vende tu loot en el mercado\n📈 Comercia con otros jugadores\n\nGestiona tu inventario y economía sabiamente.",
                    "Economía dinámica con mercado de jugadores. Vende items raros a otros usuarios, compra equipo mejorado y acumula riqueza. Los precios varían según oferta/demanda.",
                    "Gana dinero completando quests, vendiendo items crafteados o derrotando enemigos. Usa tus monedas para comprar mejor equipamiento y expandir inventario."
                ]
            },
            "reputacion": {
                "patterns": [
                    r"\b(reputacion|reputation|facciones|factions)\b",
                    r"\b(como).*(subir|mejorar).*(reputacion)\b"
                ],
                "responses": [
                    "Sistema de Reputación con facciones:\n👿 Hostile (-500 o menos)\n😐 Unfriendly (-500 a 0)\n😶 Neutral (0 a 500)\n😊 Friendly (500 a 1000)\n🌟 Honored (1000+)\n\nTus acciones afectan cómo te ven las facciones.",
                    "Reputación determina relaciones con NPCs y facciones. Ayuda a un grupo, otro puede odiarte. Mayor reputación = mejores precios, quests exclusivas y acceso a zonas especiales.",
                    "Gana reputación completando quests para facciones, ayudando NPCs o derrotando enemigos de grupos rivales. Tu rango mejora con más puntos."
                ]
            },
            "pets_companions": {
                "patterns": [
                    r"\b(pets|mascotas|companions|compa[ñn]eros)\b",
                    r"\b(como).*(tener|conseguir).*(mascota|pet|compa[ñn]ero)\b"
                ],
                "responses": [
                    "Sistema de Mascotas/Compañeros:\n🐕 Perros - Ataque y defensa\n🐉 Dragones - Vuelo y fuego\n🤖 Robots - Tech skills\n🐈 Gatos - Sigilo y agilidad\n\nTu pet te ayuda en combate, recolecta items y evoluciona.",
                    "Adopta mascotas que te acompañan. Sube su nivel peleando, aprenden habilidades y tienen stats propios. Solo una mascota activa a la vez, pero puedes coleccionarlas todas.",
                    "Encuentra pets en el mundo, doma criaturas o compra en tiendas. Cada tipo tiene habilidades únicas. Alimenta y entrena tu mascota para hacerla más fuerte."
                ]
            },
            "clases": {
                "patterns": [
                    r"\b(clases|class|guerrero|mago|arquero|warrior|mage|archer|rogue)\b",
                    r"\b(que|cuales).*(clases|class)\b"
                ],
                "responses": [
                    "4 Clases disponibles:\n⚔️ Warrior - Alto daño físico y tanque\n🧙 Mage - Magia devastadora, baja defensa\n🏹 Archer - Ataque a distancia, críticos\n🗡️ Rogue - Sigilo, backstab, velocidad\n\nCada una con 3 skills únicas.",
                    "Selecciona tu clase al inicio. Determina tu estilo de juego y habilidades. Sube de nivel para desbloquear más poderes. Puedes cambiar de clase (recomienza nivel).",
                    "Clases balanceadas para diferentes estrategias. Warrior para tanquear, Mage para AoE damage, Archer para DPS, Rogue para burst y evasión."
                ]
            },
            "eventos": {
                "patterns": [
                    r"\b(eventos|event|invasiones|meteor|festival)\b",
                    r"\b(que|cuando).*(eventos|event)\b"
                ],
                "responses": [
                    "Eventos Dinámicos del Mundo:\n☄️ Meteoros - Recolecta materiales raros\n👹 Invasiones - Defiende ciudades\n🎉 Festivales - Minijuegos y rewards\n⛈️ Tormentas - Peligro temporal\n\nEventos aparecen aleatoriamente con recompensas únicas.",
                    "Sistema de eventos aleatorios activo. Participa para ganar items exclusivos y experiencia bonus. Duración limitada, algunos son mundiales.",
                    "Cuando aparece un evento, recibes notificación. Ve a la zona marcada, completa objetivos del evento y gana grandes recompensas. ¡Trabaja en equipo!"
                ]
            },
            "clanes": {
                "patterns": [
                    r"\b(clanes|clan|guild|guilds|grupo)\b",
                    r"\b(como).*(crear|unirme).*(clan|guild)\b"
                ],
                "responses": [
                    "Sistema de Clanes/Guilds:\n👥 Crea tu propio clan\n🤝 Invita amigos\n📊 Sube nivel del clan\n🏆 Rankings de clanes\n💬 Chat interno\n\nColabora con tu grupo para dominar el mundo.",
                    "Únete o crea un clan. Beneficios: chat grupal, quests de clan, almacén compartido y bonos por jugar juntos. Los mejores clanes aparecen en leaderboards.",
                    "Clanes tienen líder y miembros. Sube nivel del clan completando objetivos grupales. Mayor nivel = más beneficios y prestigio."
                ]
            },
            "mercado": {
                "patterns": [
                    r"\b(mercado|market|trading|comercio).*(jugadores|player)\b",
                    r"\b(como).*(vender|comprar).*(jugadores|otros)\b"
                ],
                "responses": [
                    "Mercado de Jugadores:\n🏪 Lista items para venta\n💰 Establece tus precios\n🔍 Busca gangas de otros\n📦 Transacciones seguras\n\nEconomía player-driven. Negocia y acumula riqueza.",
                    "Vende tu loot a otros jugadores en el mercado global. Busca ofertas, compara precios y encuentra items raros. Perfecto para comerciantes.",
                    "Para vender: Ve a Mercado → Lista Item → Establece precio. Para comprar: Explora listados → Compra lo que necesites. Sistema toma pequeña comisión."
                ]
            },
            "stats_analytics": {
                "patterns": [
                    r"\b(estadisticas|stats|analytics|progreso)\b",
                    r"\b(donde|como).*(ver|revisar).*(stats|estadisticas)\b"
                ],
                "responses": [
                    "Dashboard de Estadísticas rastrea:\n⏱️ Tiempo jugado\n⚔️ Enemigos derrotados\n📏 Distancia recorrida\n💎 Items colectados\n🎯 Quests completadas\n💀 Muertes\n🌍 Mundos creados\n🏆 Logros desbloqueados",
                    "Ve tus stats completas en el perfil. Compara con amigos, establece records personales y visualiza tu progresión. Stats se actualizan en tiempo real.",
                    "Analytics muestra heatmaps de dónde mueres más, items más usados, zonas más visitadas y mucho más. Úsalo para mejorar tu estrategia."
                ]
            },
            "accesibilidad": {
                "patterns": [
                    r"\b(accesibilidad|accessibility|daltonismo|colorblind|subtitulos)\b",
                    r"\b(opciones).*(accesibilidad|accessibility)\b"
                ],
                "responses": [
                    "Opciones de Accesibilidad:\n🎨 Modo daltonismo (deuteranopia, protanopia, tritanopia)\n📝 Subtítulos configurables (tamaño, color, fondo)\n🎮 Controles remapeables\n🔊 Audio balanceado\n⌨️ Soporte teclado/mouse/gamepad\n\nTodos pueden jugar cómodamente.",
                    "Configuración accesible en Ajustes. Adapta visuales, audio y controles a tus necesidades. Modos de color para diferentes tipos de daltonismo incluidos.",
                    "Accesibilidad es prioridad. Ajusta todo: desde tamaño de UI hasta velocidad del juego. Experimenta hasta encontrar tu configuración perfecta."
                ]
            },
            "plantillas": {
                "patterns": [
                    r"\b(plantillas|templates|mundo|presets)\b",
                    r"\b(como).*(usar|crear).*(plantilla|template)\b"
                ],
                "responses": [
                    "5 Plantillas de Mundos:\n🏰 Dungeon Crawler - Mazmorras clásicas\n🗺️ Open World - Exploración libre\n🏝️ Survival Island - Supervivencia\n🚀 Space Station - Sci-fi\n⚔️ Fantasy Kingdom - Medieval\n\nUsa templates como base y personaliza.",
                    "Plantillas aceleran creación. Selecciona una, modifica parámetros y genera. Perfecto para principiantes o crear mundos rápidos.",
                    "Crea tus propias plantillas guardando configuraciones. Comparte con la comunidad. Las más populares aparecen destacadas."
                ]
            },
            "optimizacion": {
                "patterns": [
                    r"\b(optimizacion|performance|fps|lag|rendimiento)\b",
                    r"\b(como).*(mejorar|optimizar).*(rendimiento|fps)\b"
                ],
                "responses": [
                    "Optimización y Performance:\n⚙️ Presets de calidad (Bajo/Medio/Alto/Ultra)\n🎯 LOD system automático\n🌫️ Occlusion culling\n📊 Monitor de FPS en tiempo real\n💾 Texture streaming\n\nAjusta según tu hardware.",
                    "Baja calidad gráfica en Ajustes si experimentas lag. Sistema ajusta automáticamente detalles basado en performance. Desactiva sombras/partículas para más FPS.",
                    "Modo performance activa: menor distancia de dibujado, modelos simplificados, menos efectos. Mantiene jugabilidad con mejor framerate."
                ]
            }
        }
    
    def get_response(self, user_message: str, context: Optional[Dict] = None) -> str:
        """
        Genera respuesta basada en patrones de la base de conocimiento
        """
        user_message_lower = user_message.lower().strip()
        
        # Buscar coincidencias en la base de conocimiento
        for category, data in self.knowledge_base.items():
            for pattern in data["patterns"]:
                if re.search(pattern, user_message_lower, re.IGNORECASE):
                    # Seleccionar respuesta aleatoria de la categoría
                    response = random.choice(data["responses"])
                    
                    # Agregar contexto si está disponible
                    if context:
                        response = self._add_context(response, context)
                    
                    return response
        
        # Respuesta por defecto si no hay coincidencia
        default_responses = [
            "Interesante pregunta. ¿Podrías reformularla? Puedo ayudarte con: crear mundos, guardar partidas, logros, assets personalizados, combate, VR/AR o explorar la comunidad.",
            "No estoy seguro de entender. Intenta preguntar sobre: generación de mundos, sistema de guardado, achievements, modding, sistema de combate o funciones VR.",
            "Hmm, no encuentro información específica sobre eso. Pregúntame sobre las funcionalidades principales: crear mundos 3D, guardar progreso, logros, custom assets o modo VR."
        ]
        
        return random.choice(default_responses)
    
    def _add_context(self, response: str, context: Dict) -> str:
        """Añade contexto relevante a la respuesta"""
        if "world_name" in context:
            response += f"\n\nEstás trabajando en: {context['world_name']}"
        
        if "user_level" in context:
            response += f"\nTu nivel actual: {context['user_level']}"
        
        return response
    
    def get_tutorial(self, topic: str) -> str:
        """Devuelve tutorial específico sobre un tema"""
        tutorials = {
            "basico": """
            📚 TUTORIAL BÁSICO - DataShark
            
            1️⃣ CREAR TU PRIMER MUNDO:
               • Escribe una descripción (ej: "Bosque mágico con hadas")
               • Selecciona plataformas (Windows, Mac, Linux)
               • Click en "Generar mundo"
               • Espera 10-15 segundos
            
            2️⃣ EXPLORAR EL MUNDO 3D:
               • Usa el mouse para rotar la vista
               • Scroll para hacer zoom
               • Observa biomas, NPCs y enemigos
            
            3️⃣ GUARDAR TU PROGRESO:
               • Click en "Guardar partida" (sidebar)
               • O ve a Biblioteca → Partidas guardadas
            
            4️⃣ COMPARTIR CON LA COMUNIDAD:
               • Click en "Publicar" en tu mundo
               • Otros usuarios podrán jugarlo
            
            ¡Eso es todo! ¿Listo para empezar?
            """,
            
            "avanzado": """
            🎮 TUTORIAL AVANZADO - Funcionalidades Pro
            
            1️⃣ SISTEMA DE COMBATE:
               • Abre el panel de combate (sidebar)
               • Mejora habilidades en el skill tree
               • Usa items del inventario
               • Aprende combos para bonus de daño
            
            2️⃣ CUSTOM ASSETS:
               • Crea modelos 3D externos (.glb)
               • Súbelos en Custom Assets
               • Usa texturas personalizadas
               • Comparte con la comunidad
            
            3️⃣ LOGROS Y ACHIEVEMENTS:
               • Se desbloquean automáticamente
               • Gana puntos de experiencia
               • Completa desafíos especiales
               • Compite en rankings globales
            
            4️⃣ MODO VR/AR:
               • Conecta tu headset VR
               • Click en botón "🥽 Modo VR"
               • Usa hand tracking
               • Experimenta en realidad virtual
            
            5️⃣ OPTIMIZACIÓN:
               • Ajusta settings de física
               • Controla calidad de render
               • Gestiona assets para performance
            
            ¡Domina todas las funcionalidades!
            """
        }
        
        return tutorials.get(topic, "Tutorial no disponible. Temas: 'basico', 'avanzado'")
    
    def get_faq(self) -> List[Dict[str, str]]:
        """Devuelve lista de preguntas frecuentes"""
        return [
            {
                "q": "¿Cómo creo mi primer mundo?",
                "a": "Escribe una descripción en el campo de texto (ej: 'Ciudad futurista'), selecciona las plataformas y haz clic en 'Generar mundo'. ¡Así de simple!"
            },
            {
                "q": "¿Qué es el sistema de Quests?",
                "a": "Misiones con árboles de decisión donde tus elecciones importan. Hay misiones principales, secundarias, diarias y semanales con diferentes recompensas."
            },
            {
                "q": "¿Cómo funciona el Crafting?",
                "a": "Recolecta ingredientes explorando, aprende recetas y combina items para crear armas, armaduras y consumibles. Necesitas nivel mínimo para recetas avanzadas."
            },
            {
                "q": "¿Puedo tener mascotas?",
                "a": "¡Sí! Adopta pets que te ayudan en combate: perros, dragones, robots, gatos. Cada uno tiene stats y habilidades únicas. Súbelos de nivel jugando."
            },
            {
                "q": "¿Qué son las clases?",
                "a": "Elige entre Warrior, Mage, Archer o Rogue. Cada clase tiene 3 habilidades únicas y determina tu estilo de juego. Puedes cambiar de clase reiniciando nivel."
            },
            {
                "q": "¿Cómo funcionan los eventos dinámicos?",
                "a": "Eventos aleatorios aparecen en el mundo: meteoros, invasiones, festivales, tormentas. Participa para obtener recompensas exclusivas de duración limitada."
            },
            {
                "q": "¿Puedo crear un clan?",
                "a": "Sí, crea o únete a clanes para jugar con amigos. Beneficios: chat grupal, quests de clan, rankings y bonos por jugar juntos."
            },
            {
                "q": "¿Existe mercado de jugadores?",
                "a": "Sí, vende y compra items con otros jugadores. Lista tus items, establece precios y busca gangas. Economía player-driven con transacciones seguras."
            },
            {
                "q": "¿Qué estadísticas se rastrean?",
                "a": "Tiempo jugado, enemigos derrotados, distancia recorrida, items colectados, quests completadas, muertes, mundos creados y logros desbloqueados."
            },
            {
                "q": "¿Hay opciones de accesibilidad?",
                "a": "Sí: modos de daltonismo (deuteranopia, protanopia, tritanopia), subtítulos configurables, controles remapeables y ajustes de audio balanceado."
            },
            {
                "q": "¿Qué son las plantillas de mundos?",
                "a": "Templates predefinidos (Dungeon, Open World, Survival, Space Station, Fantasy Kingdom) que aceleran la creación. Úsalos como base y personaliza."
            },
            {
                "q": "¿Cómo optimizo el rendimiento?",
                "a": "Ajusta presets de calidad (Bajo/Medio/Alto/Ultra) en configuración. El sistema incluye LOD automático, occlusion culling y texture streaming."
            },
            {
                "q": "¿Necesito internet siempre?",
                "a": "Solo para generar mundos inicialmente. Una vez cargado, puedes jugar offline. El sistema guarda localmente."
            },
            {
                "q": "¿El asistente IA usa APIs externas?",
                "a": "¡No! El asistente ahora es 100% local. Usa una base de conocimiento predefinida sin necesitar conexión a OpenAI u otras APIs."
            }
        ]


# Instancia global del asistente local
local_assistant = LocalAI()
