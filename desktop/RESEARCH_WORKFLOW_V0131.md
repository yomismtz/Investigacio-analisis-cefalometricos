# YomCeph Desktop v0.13.1 Classic — Flujo de investigación

Esta versión mantiene la interfaz Classic de YomCeph 0.12.x y añade un flujo secuencial de investigación.

## Secuencia

1. Idioma en el instalador: Español o English.
2. Al abrir: Caso individual o Investigación.
3. Investigación: datos del protocolo mediante campos y listas de verificación.
4. Selección de uno o varios análisis cefalométricos.
5. Para cada análisis, selección de las mediciones/resultados que realmente formarán parte del estudio.
6. YomCeph calcula la lista mínima de landmarks requerida por esas mediciones.
7. Incorporación de radiografías: carga masiva, por lotes o registro manual. Límite de 1000 casos por estudio.
8. Cada registro conserva número/ID, edad, sexo, radiografía, estado y observaciones.
9. Al abrir un registro desde la base, se restauran sus metadatos, imagen, puntos y resultados guardados.
10. El caso se marca Completo (verde) únicamente cuando están registrados todos los resultados seleccionados para el protocolo.
11. Si no puede analizarse, puede marcarse Excluido con motivo documentado (calidad radiográfica, landmarks no identificables, criterios del protocolo u otro). El excluido deja de formar parte de la muestra válida pero permanece en la auditoría.
12. Exportación separada de muestra válida y auditoría completa.

## Estados

- ● verde: Completo / incluido.
- ● naranja: Incompleto.
- ● gris: Pendiente.
- ● rojo: Excluido.

El protocolo puede bloquearse cuando comienzan a registrarse casos válidos para evitar cambiar accidentalmente las variables del estudio a mitad de la recolección.
