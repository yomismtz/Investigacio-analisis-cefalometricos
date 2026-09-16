# Yornis v0.15.6 · Quality & UX

Fecha: 15 de septiembre de 2026.

## Objetivo

v0.15.6 es una actualización de calidad visual y experiencia de uso. Conserva la geometría cefalométrica auditada y la capa de evidencia por edad/sexo de v0.15.5. No redefine fórmulas ni crea normas clínicas nuevas.

## Escritorio

- Lanzador reconstruido con jerarquía visual más clara para Caso individual e Investigación.
- Sistema común de estilos para botones, pestañas, grupos, campos, listas, tablas y estados.
- Tipografía Segoe UI y espaciados más consistentes en Windows/HiDPI.
- Áreas de clic mayores y foco de teclado más visible.
- Los temas inspirados en aves siguen disponibles y usan la misma jerarquía visual.
- Individual e Investigación comparten la misma capa de presentación sin alterar el motor de cálculo.

## Ayuda F1 / referencias

- Nueva interfaz de 17 tablas con búsqueda por tabla, medida o texto de fuente.
- Navegación anterior/siguiente y aumento/reducción de texto.
- Se reemplaza lenguaje visual de “normalidad” por “menor/dentro/mayor a referencia” para evitar que una media se lea como diagnóstico.
- Fuente principal y notas se mantienen visibles.
- Conserva las referencias por edad/sexo de v0.15.5, incluyendo vía aérea pediátrica y contexto C1–C7.
- No se interpolan edades no publicadas.

## Web

- Rediseño responsive de la página pública.
- Filtros por área y búsqueda para los 17 análisis.
- Tarjetas de funciones con viñetas más legibles.
- Sección específica para referencia de muestra, por edad e histórica.
- Mejoras de foco de teclado, navegación móvil y `prefers-reduced-motion`.
- Se mantiene el enlace genérico a `releases/latest` para evitar descargas rotas en futuras versiones.

## Pruebas y distribución

El workflow de v0.15.6 exige antes de publicar:

1. Compilación de todos los módulos Python.
2. Suite unitaria y de regresión completa.
3. Auditoría de 102 mediciones y 17 tablas.
4. Verificación de que C1–C7 no recupere el corte universal 35–45°.
5. Verificación de que no aparezcan edades interpoladas en vía aérea.
6. Smoke test GUI/HiDPI.
7. Build con PyInstaller.
8. Arranque en frío del ejecutable.
9. Creación del instalador Inno Setup.
10. Portable ZIP y SHA-256.

## Alcance clínico

Yornis sigue siendo una herramienta educativa y de investigación. La mejora de interfaz y las pruebas de software no sustituyen una validación clínica externa ni estudios de reproducibilidad intra/interobservador.
