# Firma de código de Windows para Yornis

Yornis usa Authenticode para reducir advertencias de Windows y mostrar una identidad de editor verificable.

## Política de publicación estable

Las compilaciones de validación (pull request o ejecución manual) pueden generarse sin certificado para probar código, interfaz e instalador. Una publicación estable desde `main` no puede publicarse si `Yornis.exe` o el instalador no tienen una firma Authenticode con estado `Valid`.

El workflow espera estos secretos de GitHub Actions:

- `WINDOWS_CERTIFICATE_BASE64`: contenido Base64 de un certificado PFX/P12 de firma de código confiable.
- `WINDOWS_CERTIFICATE_PASSWORD`: contraseña del archivo PFX/P12.

La firma usa SHA-256 y marca de tiempo RFC 3161. Después de firmar, el workflow ejecuta `signtool verify /pa /v` y `Get-AuthenticodeSignature`. Si la firma no es válida, la Release se detiene.

## Certificado

Para distribución pública no sirve un certificado autofirmado. Debe usarse un certificado de firma de código cuya cadena llegue a una autoridad de certificación confiable para Windows. Conviene mantener la misma identidad de editor entre versiones para conservar la reputación del publicador.

## SmartScreen

Una firma válida mejora la identidad y permite que se acumule reputación, pero Microsoft puede seguir mostrando SmartScreen en archivos nuevos hasta que exista reputación suficiente. La distribución mediante Microsoft Store es la vía documentada por Microsoft que evita la advertencia de descarga de SmartScreen de forma consistente.

## Metadatos

El ejecutable incluye información de versión de Windows y el instalador incluye editor, versión, sitio, soporte y URL de actualizaciones. Estos datos mejoran la presentación, pero no sustituyen una firma criptográfica de confianza.
