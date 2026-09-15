# Auditoría de software Yornis — 15 de septiembre de 2026

## Alcance

Revisión de la cadena de publicación, pruebas automatizadas, empaquetado Windows, sitio público y consistencia de versión. Esta auditoría no sustituye una validación clínica externa de las fórmulas cefalométricas ni modifica automáticamente referencias clínicas.

## Hallazgos confirmados

1. **Riesgo de release mutable en v0.15.4.** El workflow `build-yornis-v0154.yml` publica de nuevo la etiqueta `v0.15.4` en cualquier `push` a `main` que cambie `desktop/**`. Esto permite que binarios diferentes compartan el mismo número de versión y rompe la reproducibilidad de checksums.
2. **La web dependía de nombres de activos concretos.** Corregido el 15-sep-2026: el CTA principal usa la página `releases/latest`, evitando enlaces obsoletos cuando cambia el nombre del instalador.
3. **Validación de Pages acoplada al enlace antiguo.** Corregido el 15-sep-2026.
4. **Accesibilidad y navegación móvil.** Corregidos contador dinámico, cierre de menú por Escape/click exterior/resize y fallback de `IntersectionObserver`.

## Hallazgos que requieren validación clínica externa

- El rango fijo de lordosis cervical C1–C7 de 35–45° no debe considerarse universal sin definir con precisión el método de medición, postura, edad, sexo y población. La literatura muestra variación sustancial entre métodos y poblaciones.
- Las referencias de vía aérea y otras tablas históricas deben conservar la fuente y evitar presentarse como límites diagnósticos universales.

## Regla para la siguiente versión

La nueva versión debe usar una etiqueta nueva e inmutable, ejecutar toda la suite de pruebas antes de empaquetar, generar SHA-256 para instalador y portable, comprobar arranque en frío y actualizar la web sólo después de verificar que los artefactos existan.
