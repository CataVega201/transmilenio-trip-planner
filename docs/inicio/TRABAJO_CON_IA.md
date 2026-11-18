# Trabajar con ChatGPT y subir tus contribuciones

Pega los prompts en orden en un mismo chat. Reemplaza los textos entre corchetes. Las instrucciones también sirven al retomar en un chat nuevo.

### 1. Preparar tu primera tarea

> Soy [nombre], trabajo en mi propia copia de CataVega201/transmilenio-trip-planner en Windows. Trabaja en español, con herramientas gratuitas. Comprueba la carpeta, el remoto, git status, la rama y mi nombre y correo Git. No inventes mi correo. Lee mi ficha, docs/CONTRATOS.md y la guía de Git. Si faltan localmente, haz git fetch origin y léelas con git show origin/docs/guias-equipo:RUTA. Si solo tienes acceso al chat, dame bloques de hasta tres instrucciones para VS Code y espera mis resultados. Si tienes acceso local, ejecuta las acciones tú. Nunca afirmes haber ejecutado o subido algo sin comprobarlo.

### 2. Implementar

Pega el encargo de **un bloque** de tu ficha, seguido de este prompt:

> Busca una Issue o PR existente para esta tarea antes de duplicarla. Registra responsable, archivos y rama en la Issue. Con el árbol limpio, crea mi rama desde main actualizado con git pull --ff-only. Si ya existe, retómala. Implementa solamente mi bloque. Dentro de motor/ usa las estructuras propias del equipo y respeta todas las prohibiciones del contrato. Conserva las firmas públicas y las decisiones del equipo sobre retornos. Añade casos normales y extremos, ejecuta pruebas, documenta alternativa, Big O, variables y límites en mi archivo R12. Explícame el algoritmo con un ejemplo que yo pueda defender. Si falta el módulo de otro autor, usa una dependencia de prueba fuera de motor/ y señala qué queda sin comprobar.

### 3. Guardar, subir y abrir revisión

> Revisa el diff y confirma que solo contiene mis archivos. Haz commits coherentes con mi identidad configurada y sube mi rama con git push -u origin NOMBRE_REAL_DE_MI_RAMA. Verifica que el commit local coincide con el remoto. Abre o actualiza una PR hacia main con resumen, pruebas realmente ejecutadas, Issue y pendientes. Déjala en borrador si faltan dependencias. Si GitHub pide autenticación, la hago yo; si no puedes abrir la PR, dame el enlace y el texto exacto. No integres la PR por mí. Devuélveme el hash, el enlace y cualquier fallo. No añadas atribuciones de otros integrantes.

### Retomar mañana o resolver un conflicto

> Comprueba mi rama, git status y las PR abiertas. Conserva cualquier trabajo sin guardar. Con el árbol limpio, trae origin e incorpora origin/main a mi rama si ha cambiado. Si hay un conflicto con trabajo ajeno, identifica los archivos y las dos intenciones. Detente antes de elegir una versión sin acuerdo. No uses force push, reset --hard ni Discard Changes. Si el conflicto viene de ese merge y se inició con el árbol limpio, git merge --abort permite volver a mis commits previos. Continúa una tarea independiente mientras llega la revisión.

**Para revisar a otra persona.** Abre la PR → **Archivos cambiados** (Files changed). Comprueba firmas, casos extremos y pruebas. En **Revisar cambios** elige **Aprobar** o **Solicitar cambios**. Tras aprobación y comprobaciones, integra con **Crear un commit de fusión** para conservar los commits de cada integrante. Una rama por tarea y un responsable por archivo reducen los conflictos; dos cambios compatibles en Git todavía pueden necesitar una prueba conjunta.
