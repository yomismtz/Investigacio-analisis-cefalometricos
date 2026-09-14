from __future__ import annotations

# Offline, native-Tk reference tables for Yornis v0.15.4.
# Native text is used intentionally so labels stay sharp on HiDPI monitors.

DISCLAIMER = (
    "Referencias históricas/orientativas. Estar por debajo, dentro o por encima de la "
    "referencia no equivale por sí solo a diagnóstico. Correlacionar con edad, sexo, "
    "población, técnica radiográfica, biotipo y evaluación clínica integral."
)

COLORS = {
    "navy": "#0B2C62",
    "grid": "#8EA6C4",
    "header": "#EAF2FB",
    "low": "#FFF0A8",
    "normal": "#D8F5D2",
    "high": "#F7C4CC",
    "white": "#FFFFFF",
}

def _row(name, norm, de, low, normal, high):
    return (name, norm, de, low, normal, high)

TABLES = [
    {
        "id": "steiner", "title": "ANÁLISIS DE STEINER", "subtitle": "Normas históricas orientativas",
        "first": "Ángulo o plano",
        "source": "Steiner CC. Cephalometrics for you and me. Am J Orthod. 1953;39(10):729-755. DOI 10.1016/0002-9416(53)90082-7.",
        "rows": [
            _row("SNA","82°","±2°","Sugiere retrusión maxilar o deficiencia sagital del maxilar; tendencia esqueletal Clase III.","Posición sagital maxilar adecuada respecto a la base craneal.","Sugiere protrusión maxilar o adelantamiento del maxilar; tendencia esqueletal Clase II."),
            _row("SNB","80°","±2°","Sugiere retrusión mandibular y mentón más posterior; tendencia Clase II.","Posición sagital mandibular adecuada respecto a la base craneal.","Sugiere protrusión mandibular y mentón adelantado; tendencia Clase III."),
            _row("ANB","2°","±2°","Relación maxilomandibular hacia Clase III; maxilar más retruido o mandíbula más adelantada.","Relación sagital maxilomandibular equilibrada.","Relación maxilomandibular hacia Clase II; maxilar más adelantado o mandíbula más retruida."),
            _row("SND","76°","±2°","Sugiere retrusión mandibular y/o mentón más posterior.","Relación sagital mandibular y mentoniana armónica.","Sugiere protrusión mandibular y/o mentón más prominente."),
            _row("GoGn-SN","32°","±5°","Patrón hipodivergente o braquifacial; crecimiento más horizontal y menor altura facial inferior.","Patrón vertical equilibrado.","Patrón hiperdivergente o dolicofacial; crecimiento más vertical y mayor altura facial inferior."),
            _row("Plano oclusal-SN","14°","±4°","Plano oclusal más plano y horizontal.","Inclinación del plano oclusal dentro de lo esperado.","Plano oclusal más inclinado; mayor tendencia vertical."),
            _row("1-NA (ángulo)","22°","±4°","Incisivo superior retroinclinado; menor soporte labial superior.","Inclinación del incisivo superior adecuada.","Incisivo superior proinclinado; protrusión dentoalveolar superior y mayor soporte labial."),
            _row("1-NA (mm)","4 mm","±2 mm","Incisivo superior más retruido respecto a NA.","Posición anteroposterior del incisivo superior adecuada.","Incisivo superior más protrusivo respecto a NA."),
            _row("1-NB (ángulo)","25°","±4°","Incisivo inferior retroinclinado; compensación dentaria en Clase III o apiñamiento.","Inclinación del incisivo inferior adecuada.","Incisivo inferior proinclinado; compensación en Clase II o protrusión dentoalveolar inferior."),
            _row("1-NB (mm)","4 mm","±2 mm","Incisivo inferior más retruido respecto a NB.","Posición anteroposterior del incisivo inferior adecuada.","Incisivo inferior más protrusivo respecto a NB."),
            _row("Ángulo interincisal","131°","±6°","Sugiere proinclinación/protrusión de incisivos, a menudo con biprotrusión dentoalveolar.","Relación interincisal equilibrada.","Sugiere retroinclinación de incisivos y menor protrusión dentoalveolar."),
            _row("Pg-NB","2 mm","±1 mm","Mentón óseo menos prominente o más retruido respecto a NB.","Prominencia del mentón dentro de lo esperado.","Mentón óseo más prominente respecto a NB."),
        ],
    },
    {
        "id":"downs","title":"ANÁLISIS DE DOWNS","subtitle":"Normas históricas orientativas","first":"Ángulo o plano",
        "source":"Downs WB. Variations in facial relationships: their significance in treatment and prognosis. Am J Orthod. 1948;34(10):812-840. DOI 10.1016/0002-9416(48)90015-3.",
        "rows":[
            _row("Ángulo facial","87.8°","±3.6°","Sugiere retrusión mandibular o mentón más posterior; tendencia Clase II.","Relación anteroposterior facial equilibrada.","Sugiere prognatismo mandibular o mentón adelantado; tendencia Clase III."),
            _row("Ángulo de convexidad","0°","±4°","Perfil más recto o cóncavo; tendencia esqueletal Clase III.","Perfil blando/óseo armónico.","Perfil más convexo; tendencia esqueletal Clase II."),
            _row("Plano A-B","-4.6°","±3.5°","Discrepancia más hacia Clase II; relación maxilomandibular más distal.","Relación maxilomandibular equilibrada.","Discrepancia más hacia Clase III; relación maxilomandibular más mesial."),
            _row("Plano mandibular","21.9°","±3.2°","Patrón hipodivergente o braquifacial; crecimiento más horizontal.","Patrón vertical equilibrado.","Patrón hiperdivergente o dolicofacial; crecimiento más vertical."),
            _row("Eje Y","59.4°","±3.8°","Dirección de crecimiento más horizontal y hacia adelante.","Dirección de crecimiento equilibrada.","Dirección de crecimiento más vertical y hacia abajo-atrás."),
            _row("Plano oclusal a FH","9.3°","±3.8°","Plano oclusal más plano.","Inclinación del plano oclusal dentro de lo esperado.","Plano oclusal más inclinado; mayor componente vertical."),
            _row("Incisivo inferior a plano oclusal","14.5°","±3.5°","Incisivo inferior retroinclinado.","Inclinación del incisivo inferior adecuada.","Incisivo inferior proinclinado."),
        ],
    },
    {
        "id":"tweed","title":"ANÁLISIS DE TWEED","subtitle":"Normas históricas orientativas","first":"Ángulo o plano",
        "source":"Tweed CH. The diagnostic facial triangle in the control of treatment objectives. Am J Orthod. 1969;55(6):651-667. DOI 10.1016/0002-9416(69)90041-4.",
        "rows":[
            _row("FMA","25°","±5°","Patrón hipodivergente o braquifacial; crecimiento más horizontal y tendencia a sobremordida profunda.","Relación Frankfort-plano mandibular equilibrada.","Patrón hiperdivergente o dolicofacial; crecimiento más vertical y tendencia a mordida abierta."),
            _row("FMIA","65°","±5°","Incisivo inferior más proinclinado/protrusivo respecto a Frankfort.","Inclinación del incisivo inferior dentro de lo esperado.","Incisivo inferior más retroinclinado o retraído."),
            _row("IMPA","90°","±5°","Incisivo inferior retroinclinado; posible compensación dentaria en Clase III o apiñamiento.","Inclinación del incisivo inferior equilibrada respecto al plano mandibular.","Incisivo inferior proinclinado; posible compensación en Clase II o protrusión dentoalveolar inferior."),
        ],
    },
    {
        "id":"ricketts","title":"ANÁLISIS DE RICKETTS","subtitle":"Normas históricas orientativas","first":"Ángulo o plano",
        "source":"Ricketts RM. A foundation for cephalometric communication. Am J Orthod. 1960;46(5):330-357. DOI 10.1016/0002-9416(60)90047-6.",
        "rows":[
            _row("Eje facial","90°","±3.5°","Sugiere patrón dolicofacial y crecimiento mandibular más hacia abajo-atrás.","Dirección de crecimiento facial equilibrada.","Sugiere patrón braquifacial y crecimiento más hacia adelante."),
            _row("Profundidad facial","87°","±3°","Sugiere retrusión mandibular relativa.","Posición anteroposterior mandibular adecuada.","Sugiere protrusión mandibular relativa."),
            _row("Profundidad maxilar","90°","±3°","Sugiere retrusión maxilar relativa.","Posición anteroposterior maxilar adecuada.","Sugiere protrusión maxilar relativa."),
            _row("Convexidad en punto A","2 mm","±2 mm","Perfil óseo más plano o cóncavo; tendencia Clase III.","Convexidad esqueletal equilibrada.","Perfil más convexo; tendencia Clase II."),
            _row("Incisivo inferior a A-Pg (ángulo)","22°","±4°","Incisivo inferior retroinclinado.","Inclinación del incisivo inferior adecuada.","Incisivo inferior proinclinado."),
            _row("Incisivo inferior a A-Pg (mm)","1 mm","±2 mm","Incisivo inferior más retruido respecto a A-Pg.","Posición anteroposterior del incisivo inferior equilibrada.","Incisivo inferior más protrusivo respecto a A-Pg."),
        ],
    },
    {
        "id":"bjork_jarabak","title":"ANÁLISIS DE BJÖRK–JARABAK","subtitle":"Normas históricas orientativas","first":"Parámetro",
        "source":"Björk A. Prediction of mandibular growth rotation. Am J Orthod. 1969;55(6):585-599. DOI 10.1016/0002-9416(69)90036-0; Jarabak JR, Fizzell JA. Technique and Treatment with Light-wire Edgewise Appliances. 1972.",
        "rows":[
            _row("Ángulo silla","123°","±5°","Puede asociarse a tendencia de prognatismo mandibular o base craneal anterior más cerrada.","Relación craneomandibular dentro de lo esperado.","Puede asociarse a retrognatismo mandibular o base craneal más abierta."),
            _row("Ángulo articular","143°","±6°","Sugiere crecimiento mandibular más hacia adelante y rotación anterior.","Relación articular equilibrada.","Sugiere crecimiento mandibular más hacia abajo-atrás y rotación posterior."),
            _row("Ángulo gonial","130°","±7°","Patrón braquifacial o rotación anterior mandibular.","Morfología mandibular equilibrada.","Patrón dolicofacial o rotación posterior mandibular."),
            _row("Altura facial posterior (S-Go)","81 mm","±5 mm","Altura facial posterior reducida; favorece rotación posterior mandibular.","Altura facial posterior proporcional.","Altura facial posterior aumentada; favorece rotación anterior mandibular."),
            _row("Altura facial anterior (N-Me)","112 mm","±6 mm","Cara anterior más corta; patrón más horizontal.","Altura facial anterior dentro de lo esperado.","Cara anterior más larga; patrón más vertical."),
            _row("Índice de Jarabak (S-Go/N-Me ×100)","65%","±4%","Relación posterior/anterior reducida; patrón hiperdivergente o mordida abierta.","Proporción facial equilibrada.","Relación posterior/anterior aumentada; patrón hipodivergente o sobremordida profunda."),
        ],
    },
    {
        "id":"wits","title":"ANÁLISIS DE WITS","subtitle":"Norma histórica orientativa","first":"Ángulo o plano",
        "source":"Jacobson A. The Wits appraisal of jaw disharmony. Am J Orthod. 1975;67(2):125-138. DOI 10.1016/0002-9416(75)90065-2.",
        "note":"Se mide proyectando los puntos A y B perpendicularmente sobre el plano oclusal funcional.",
        "rows":[
            _row("Wits appraisal","♀ 0 mm / ♂ -1 mm","±2 mm","Valor más negativo: discrepancia sagital hacia Clase III; mandíbula relativamente adelantada o maxilar retruido.","Relación sagital maxilomandibular equilibrada al proyectar A y B sobre el plano oclusal.","Valor más positivo: discrepancia sagital hacia Clase II; maxilar relativamente adelantado o mandíbula retruida."),
        ],
    },
    {
        "id":"mcnamara","title":"ANÁLISIS DE McNAMARA","subtitle":"Normas históricas orientativas","first":"Ángulo o plano",
        "source":"McNamara JA Jr. A method of cephalometric evaluation. Am J Orthod. 1984;86(6):449-469. DOI 10.1016/S0002-9416(84)90352-X.",
        "note":"Las longitudes Co-A, Co-Gn, diferencia mandibular-maxilar y altura facial dependen de edad, sexo y tamaño facial; no deben forzarse a una única norma universal.",
        "rows":[
            _row("A-Nperp","1 mm","±2 mm","Sugiere retrusión maxilar relativa.","Posición anteroposterior maxilar adecuada.","Sugiere protrusión maxilar relativa."),
            _row("Pg-Nperp","-4 mm","±4 mm","Sugiere retrusión mandibular/mentoniana relativa.","Posición anteroposterior mandibular adecuada.","Sugiere protrusión mandibular/mentoniana relativa."),
            _row("Co-A","según edad/sexo","—","Longitud maxilar disminuida.","Longitud maxilar acorde con edad y sexo.","Longitud maxilar aumentada."),
            _row("Co-Gn","según edad/sexo","—","Longitud mandibular disminuida.","Longitud mandibular acorde con edad y sexo.","Longitud mandibular aumentada."),
            _row("Co-Gn − Co-A","según edad/sexo","—","Mandíbula relativamente corta respecto al maxilar; tendencia Clase II.","Relación de longitudes maxilar-mandibular equilibrada.","Mandíbula relativamente larga respecto al maxilar; tendencia Clase III."),
            _row("ENA-Me","según edad/sexo","—","Altura facial inferior reducida.","Altura facial inferior proporcional.","Altura facial inferior aumentada."),
            _row("Plano mandibular-FH","22°","±4°","Patrón hipodivergente o más horizontal.","Patrón vertical equilibrado.","Patrón hiperdivergente o más vertical."),
            _row("Faringe superior","17 mm","±3 mm","Espacio nasofaríngeo más reducido.","Espacio nasofaríngeo dentro de lo esperado.","Espacio nasofaríngeo más amplio."),
            _row("Faringe inferior","13 mm","±2 mm","Espacio orofaríngeo más reducido.","Espacio orofaríngeo dentro de lo esperado.","Espacio orofaríngeo más amplio."),
        ],
    },
    {
        "id":"holdaway","title":"ANÁLISIS DE HOLDAWAY","subtitle":"Normas históricas orientativas","first":"Ángulo o plano",
        "source":"Holdaway RA. A soft-tissue cephalometric analysis and its use in orthodontic treatment planning. Parts I-II. Am J Orthod. 1983;84(1):1-28; 1984;85(4):279-293.",
        "note":"El ángulo H debe interpretarse junto con la convexidad esquelética; Holdaway no propuso una lectura aislada de una sola cifra para todos los perfiles.",
        "rows":[
            _row("Ángulo H","10°","±4°","Perfil más plano o menos convexo; labios más retruidos respecto a la línea H.","Relación labial y convexidad facial equilibrada.","Perfil más convexo y/o labios más protrusivos respecto a la línea H."),
            _row("Ángulo facial de tejidos blandos","91°","±7°","Mentón blando más retruido.","Proyección de tejidos blandos del mentón dentro de lo esperado.","Mentón blando más prominente."),
            _row("Labio inferior a línea H","0 mm","±1 mm","Labio inferior más retruido respecto a la línea H.","Posición del labio inferior adecuada.","Labio inferior más protrusivo respecto a la línea H."),
            _row("Espesor del mentón blando (nivel suprapogonion)","11 mm","±2 mm","Tejido blando mentoniano más delgado.","Espesor del mentón blando dentro de lo esperado.","Tejido blando mentoniano más grueso."),
        ],
    },
    {
        "id":"burstone_cogs","title":"ANÁLISIS DE BURSTONE COGS","subtitle":"Normas históricas orientativas","first":"Ángulo o plano",
        "source":"Burstone CJ, James RB, Legan H, Murphy GA, Norton LA. Cephalometrics for orthognathic surgery. J Oral Surg. 1978;36(4):269-277. PMID 273073.",
        "note":"H/M = hombres/mujeres. Son referencias de la muestra histórica, no límites diagnósticos universales.",
        "rows":[
            _row("Ar-Ptm // HP","H 37 mm / M 33 mm","±3 mm","Base posterior maxilar corta.","Base posterior maxilar proporcional.","Base posterior maxilar larga."),
            _row("Ptm-N // HP","H 53 mm / M 50 mm","±3 mm","Tercio medio superior corto.","Longitud del tercio medio dentro de lo esperado.","Tercio medio superior largo."),
            _row("Convexidad N-A-Pg","2 mm","±2 mm","Perfil óseo más plano o cóncavo; tendencia Clase III.","Convexidad esqueletal equilibrada.","Perfil más convexo; tendencia Clase II."),
            _row("N-A // HP","H 0 mm / M -1 mm","±1 mm","Retrusión maxilar.","Posición maxilar equilibrada.","Protrusión maxilar."),
            _row("N-B // HP","H -5 mm / M -6 mm","±1 mm","Retrusión mandibular.","Posición mandibular equilibrada.","Protrusión mandibular."),
            _row("N-Pg // HP","H -8 mm / M -9 mm","±3 mm","Mentón retrusivo.","Proyección mentoniana equilibrada.","Mentón prominente."),
            _row("N-ANS ⟂ HP","H 54 mm / M 50 mm","±3 mm","Altura facial superior anterior reducida.","Altura facial superior anterior proporcionada.","Altura facial superior anterior aumentada."),
            _row("ANS-Gn ⟂ HP","H 70 mm / M 61 mm","±4 mm","Altura facial inferior reducida.","Altura facial inferior proporcionada.","Altura facial inferior aumentada."),
            _row("PNS-N ⟂ HP","H 52 mm / M 50 mm","±3 mm","Altura facial superior posterior reducida.","Altura facial superior posterior proporcional.","Altura facial superior posterior aumentada."),
            _row("MP-HP","H 24° / M 22°","±4°","Patrón más horizontal.","Patrón vertical equilibrado.","Patrón más vertical."),
            _row("U1-NF (altura)","H 28 mm / M 27 mm","±2 mm","Incisivo superior menos erupcionado.","Altura del incisivo superior adecuada.","Incisivo superior más erupcionado."),
            _row("U6-NF (altura)","H 23 mm / M 22 mm","±2 mm","Molar superior menos erupcionado.","Altura del molar superior adecuada.","Molar superior más erupcionado."),
            _row("L1-MP (altura)","H 43 mm / M 40 mm","±3 mm","Incisivo inferior menos erupcionado.","Altura del incisivo inferior adecuada.","Incisivo inferior más erupcionado."),
            _row("L6-MP (altura)","H 34 mm / M 32 mm","±3 mm","Molar inferior menos erupcionado.","Altura del molar inferior adecuada.","Molar inferior más erupcionado."),
            _row("PNS-ANS // HP","H 57.7 mm / M 52.6 mm","H ±2.5 / M ±3.5 mm","Longitud maxilar/palatina reducida.","Longitud maxilar/palatina adecuada.","Longitud maxilar/palatina aumentada."),
            _row("Ar-Go","H 52 mm / M 46 mm","±4 mm","Rama mandibular corta.","Longitud de rama adecuada.","Rama mandibular larga."),
            _row("Go-Pg","H 81 mm / M 75 mm","±4 mm","Cuerpo mandibular corto.","Longitud del cuerpo mandibular adecuada.","Cuerpo mandibular largo."),
            _row("B-Pg // MP","7 mm","±2 mm","Sínfisis menos prominente.","Sínfisis/proyección mentoniana equilibrada.","Sínfisis más prominente."),
            _row("Ar-Go-Gn","130°","±7°","Gonial más cerrado; rotación anterior.","Ángulo gonial equilibrado.","Gonial más abierto; rotación posterior."),
            _row("OP-HP","8°","±4°","Plano oclusal más plano.","Plano oclusal dentro de lo esperado.","Plano oclusal más inclinado."),
            _row("A-B/OP","-4 mm","±2 mm","Relación más hacia Clase II.","Relación sagital dentoesqueletal equilibrada.","Relación más hacia Clase III."),
            _row("U1-NF (ángulo)","111°","±5°","Incisivo superior retroinclinado.","Inclinación del incisivo superior adecuada.","Incisivo superior proinclinado."),
            _row("L1-MP (ángulo)","95°","±7°","Incisivo inferior retroinclinado.","Inclinación del incisivo inferior adecuada.","Incisivo inferior proinclinado."),
        ],
    },
    {
        "id":"legan_burstone","title":"ANÁLISIS DE LEGAN–BURSTONE","subtitle":"Normas históricas orientativas","first":"Parámetro",
        "source":"Legan HL, Burstone CJ. Soft tissue cephalometric analysis for orthognathic surgery. J Oral Surg. 1980;38(10):744-751. PMID 6932485.",
        "rows":[
            _row("Convexidad facial (G'-Sn-Pg')","12°","±4°","Perfil más plano o cóncavo.","Convexidad facial equilibrada.","Perfil más convexo."),
            _row("Prognatismo maxilar","6 mm","±3 mm","Maxila blanda relativamente retruida.","Posición maxilar de tejidos blandos equilibrada.","Maxila blanda relativamente protrusiva."),
            _row("Prognatismo mandibular","0 mm","±4 mm","Mandíbula/mentón de tejidos blandos retrusivos.","Posición mandibular de tejidos blandos equilibrada.","Mandíbula/mentón de tejidos blandos protrusivos."),
            _row("Relación vertical G'-Sn / Sn-Me'","1.0","±0.1","Tercio inferior relativamente aumentado.","Proporción vertical facial equilibrada.","Tercio superior relativamente predominante o tercio inferior reducido."),
            _row("Ángulo cara inferior-garganta","100°","±7°","Ángulo más cerrado; mentón relativamente más prominente.","Relación cuello-cara inferior equilibrada.","Ángulo más abierto; mentón menos prominente."),
            _row("Relación altura-profundidad facial inferior","1.2","±0.1","Cara inferior relativamente corta/profunda.","Relación altura-profundidad equilibrada.","Cara inferior relativamente larga y menos profunda."),
            _row("Ángulo nasolabial","102°","±8°","Ángulo agudo; labio superior/incisivo superior más protrusivos.","Relación nasolabial equilibrada.","Ángulo obtuso; labio superior más retruido."),
            _row("Labio superior a Sn-Pg'","3 mm","±1 mm","Labio superior retruido.","Posición del labio superior adecuada.","Labio superior protrusivo."),
            _row("Labio inferior a Sn-Pg'","2 mm","±1 mm","Labio inferior retruido.","Posición del labio inferior adecuada.","Labio inferior protrusivo."),
            _row("Profundidad del surco mentolabial","4 mm","±2 mm","Surco mentolabial poco marcado.","Surco mentolabial equilibrado.","Surco mentolabial profundo."),
            _row("Exposición del incisivo superior","2 mm","±2 mm","Menor exposición incisiva.","Exposición incisiva dentro de lo esperado.","Mayor exposición incisiva."),
            _row("Brecha interlabial","2 mm","±2 mm","Brecha labial reducida o cierre labial más competente.","Competencia labial cercana a lo esperado.","Brecha interlabial aumentada o incompetencia labial."),
            _row("Proporción labio-mentón","0.5","±0.1","Segmento labial inferior relativamente corto o mentón más dominante.","Proporción labio-mentón equilibrada.","Segmento labial inferior relativamente largo o mentón menos dominante."),
        ],
    },
    {
        "id":"sassouni","title":"ANÁLISIS DE SASSOUNI","subtitle":"Normas históricas orientativas · análisis geométrico/orientativo","first":"Parámetro",
        "source":"Sassouni V. A roentgenographic cephalometric analysis of cephalo-facio-dental relationships. Am J Orthod. 1955;41(10):735-764. DOI 10.1016/0002-9416(55)90171-8; A classification of skeletal facial types. 1969;55(2):109-123.",
        "note":"Método eminentemente geométrico y visual. La clasificación automatizada es una ayuda computacional y requiere confirmación del trazado.",
        "rows":[
            _row("Convergencia de planos (SN, PP, OP, MP)","Intersección posterior común","cualitativa","Planos menos convergentes o más abiertos; tendencia hiperdivergente/dolicofacial.","Planos convergen de forma armónica hacia un punto posterior común.","Convergencia más cerrada o anterior; tendencia hipodivergente/braquifacial."),
            _row("Arco anterior","Dentición anterior y sínfisis cercanas al arco anterior","cualitativa","Sector anterior más retruido o corto; posible retrusión incisiva/mentoniana.","Relación anterior armónica con el arco.","Sector anterior más protrusivo o prominente."),
            _row("Arco posterior","Cóndilo, rama y cuerpo mandibular cercanos al arco posterior","cualitativa","Mandíbula/rama relativamente retruidas o cortas.","Relación posterior armónica con el arco.","Mandíbula/rama relativamente protruidas o largas."),
            _row("Relación vertical global","Proporciones verticales equilibradas","cualitativa","Menor altura facial anterior inferior; patrón corto.","Proporción vertical equilibrada.","Mayor altura facial anterior inferior; patrón largo."),
            _row("Plano oclusal","Entre PP y MP; compatible con la arquitectura facial","cualitativa","Plano oclusal más plano u horizontal.","Plano oclusal armónico.","Plano oclusal más inclinado o vertical."),
            _row("Armonía sagital maxilomandibular","Maxilar y mandíbula coherentes con la arquitectura facial","cualitativa","Tendencia a Clase III o perfil más cóncavo.","Relación sagital global armónica.","Tendencia a Clase II o perfil más convexo."),
        ],
    },
    {
        "id":"cvm","title":"MADURACIÓN VERTEBRAL CERVICAL (CVM)","subtitle":"Baccetti–Franchi–McNamara · referencia orientativa","first":"Parámetro",
        "source":"Franchi L, Baccetti T, McNamara JA Jr. Mandibular growth as related to cervical vertebral maturation and body height. AJODO. 2000;118:335-340. PMID 10982936; Baccetti T, Franchi L, McNamara JA Jr. Angle Orthod. 2002;72(4):316-323. PMID 12169031.",
        "note":"CS1–CS2: prepuberales; CS3: cercano al pico; CS4: postpico inmediato; CS5–CS6: maduración avanzada. CVM no equivale a edad cronológica exacta.",
        "rows":[
            _row("Maduración cervical global","Concordante con edad/sexo","cualitativa","Estadio menor al esperado: maduración retrasada; mayor potencial de crecimiento remanente.","Maduración acorde con edad, sexo y fase de crecimiento.","Estadio mayor al esperado: maduración avanzada; menor potencial de crecimiento remanente."),
            _row("Concavidad borde inferior C2","Aparece desde CS3","cualitativa","Ausente cuando debería observarse: maduración más inmadura.","Hallazgo concordante con el estadio CVM.","Presente precozmente o muy marcada: maduración más avanzada."),
            _row("Concavidad borde inferior C3","Aparece desde CS3–CS4","cualitativa","Ausente cuando ya se esperaría: desarrollo más inmaduro.","Concordante con la transición hacia el pico o postpico temprano.","Más marcada de lo esperado: desarrollo más avanzado."),
            _row("Concavidad borde inferior C4","Aparece desde CS4","cualitativa","Ausente: sugiere que el pico puberal aún no ha pasado por completo.","Compatible con estadio alrededor o después del pico.","Muy marcada: compatible con mayor madurez postpico."),
            _row("Forma de cuerpos C3–C4","Trapecio → rectangular horizontal → cuadrado/vertical según estadio","cualitativa","Forma más inmadura que la esperada.","Morfología vertebral concordante con el estadio.","Forma más madura que la esperada."),
            _row("Pico de crecimiento mandibular","Entre CS3 y CS4","cualitativa","Si aún no alcanza CS3: pico puberal no iniciado.","CS3–CS4 compatible con cercanía o paso del pico de crecimiento.","Si ya está en CS5–CS6: crecimiento puberal prácticamente concluido."),
        ],
    },
    {
        "id":"alineacion_cervical_c2_c4","title":"ALINEACIÓN CERVICAL C2–C4","subtitle":"Outcome especial orientativo","first":"Parámetro",
        "source":"Solow B, Tallgren A. Head posture and craniofacial morphology. Am J Phys Anthropol. 1976;44(3):417-435. DOI 10.1002/ajpa.1330440306; Dentoalveolar morphology in relation to craniocervical posture. Angle Orthod. 1977;47(3):157-164.",
        "note":"Outcome postural orientativo; no sustituye una evaluación clínica o radiológica específica de columna cervical.",
        "rows":[
            _row("Curvatura global C2–C4","Lordosis cervical suave","cualitativa","Rectificación o cifosis relativa.","Curvatura fisiológica equilibrada.","Hiperlordosis cervical."),
            _row("Continuidad de la línea posterior vertebral","Trazo continuo y armónico","cualitativa","Escalones o quiebres posteriores; desalineación relativa.","Alineación posterior continua.","Curvatura posterior acentuada."),
            _row("Relación cabeza–columna cervical","Posición cefálica neutra","cualitativa","Flexión relativa de la cabeza.","Relación cráneo-cervical equilibrada.","Extensión relativa de la cabeza."),
            _row("Implicación postural","Compatible con postura funcional","cualitativa","Puede asociarse a compensación postural, vía aérea reducida o patrón vertical aumentado.","Sin alteración postural evidente en esta proyección.","Puede asociarse a extensión cefálica y adaptación postural."),
        ],
    },
]


def validate_tables() -> None:
    ids = [t["id"] for t in TABLES]
    if len(ids) != len(set(ids)):
        raise RuntimeError("IDs duplicados en tablas de referencia")
    for table in TABLES:
        if not table.get("title") or not table.get("source") or not table.get("rows"):
            raise RuntimeError(f"Tabla incompleta: {table.get('id')}")
        for row in table["rows"]:
            if len(row) != 6:
                raise RuntimeError(f"Fila inválida en {table['id']}: {row}")


def _display_quality(win) -> None:
    try:
        from yornis_display_v0152 import apply_display_quality
        apply_display_quality(win, launcher=False)
    except Exception:
        pass


def open_reference_help(root, initial: str | None = None) -> None:
    import tkinter as tk
    from tkinter import ttk

    validate_tables()
    win = tk.Toplevel(root)
    win.title("Yornis · Ayuda · Tablas de referencia")
    win.transient(root)
    _display_quality(win)

    try:
        sw, sh = int(root.winfo_screenwidth()), int(root.winfo_screenheight())
    except Exception:
        sw, sh = 1366, 768
    width = min(max(1050, int(sw * 0.88)), max(1050, sw - 40))
    height = min(max(700, int(sh * 0.88)), max(700, sh - 60))
    win.geometry(f"{width}x{height}")
    win.minsize(960, 620)

    top = ttk.Frame(win, padding=(14, 10))
    top.pack(fill="x")
    ttk.Label(top, text="Ayuda · Tablas de referencia cefalométrica", font=("Segoe UI", 16, "bold")).pack(anchor="w")
    ttk.Label(top, text=DISCLAIMER, wraplength=max(760, width - 70)).pack(anchor="w", pady=(3, 0))

    legend = ttk.Frame(top)
    legend.pack(anchor="w", pady=(8, 0))
    for text, color in (("Menor a la norma", COLORS["low"]), ("En la norma", COLORS["normal"]), ("Mayor a la norma", COLORS["high"])):
        box = tk.Label(legend, text="   ", bg=color, relief="solid", bd=1)
        box.pack(side="left", padx=(0, 5))
        ttk.Label(legend, text=text).pack(side="left", padx=(0, 18))

    body = ttk.Panedwindow(win, orient="horizontal")
    body.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    left = ttk.Frame(body, padding=4)
    right = ttk.Frame(body, padding=4)
    body.add(left, weight=0)
    body.add(right, weight=1)

    ttk.Label(left, text=f"Tablas ({len(TABLES)})", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 5))
    list_frame = ttk.Frame(left)
    list_frame.pack(fill="both", expand=True)
    lst = tk.Listbox(list_frame, width=31, exportselection=False, font=("Segoe UI", 10))
    lst.pack(side="left", fill="both", expand=True)
    lsb = ttk.Scrollbar(list_frame, orient="vertical", command=lst.yview)
    lsb.pack(side="right", fill="y")
    lst.configure(yscrollcommand=lsb.set)
    for t in TABLES:
        lst.insert("end", t["title"].replace("ANÁLISIS DE ", "").title())

    tool = ttk.Frame(right)
    tool.pack(fill="x", pady=(0, 5))
    title_var = tk.StringVar()
    ttk.Label(tool, textvariable=title_var, font=("Segoe UI", 12, "bold")).pack(side="left")
    font_size = tk.IntVar(value=10)
    size_lbl = tk.StringVar(value="100%")

    canvas_frame = ttk.Frame(right)
    canvas_frame.pack(fill="both", expand=True)
    canvas = tk.Canvas(canvas_frame, bg="white", highlightthickness=1, highlightbackground=COLORS["grid"])
    ybar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
    xbar = ttk.Scrollbar(canvas_frame, orient="horizontal", command=canvas.xview)
    canvas.configure(yscrollcommand=ybar.set, xscrollcommand=xbar.set)
    canvas.grid(row=0, column=0, sticky="nsew")
    ybar.grid(row=0, column=1, sticky="ns")
    xbar.grid(row=1, column=0, sticky="ew")
    canvas_frame.rowconfigure(0, weight=1)
    canvas_frame.columnconfigure(0, weight=1)

    table_host = tk.Frame(canvas, bg=COLORS["grid"])
    window_id = canvas.create_window((0, 0), window=table_host, anchor="nw")

    source_var = tk.StringVar()
    note_var = tk.StringVar()
    ttk.Label(right, textvariable=note_var, wraplength=max(650, width - 390), justify="left").pack(fill="x", pady=(5, 0))
    ttk.Label(right, textvariable=source_var, wraplength=max(650, width - 390), justify="left").pack(fill="x", pady=(3, 0))

    nav = ttk.Frame(right)
    nav.pack(fill="x", pady=(6, 0))

    state = {"index": 0}
    column_widths = (165, 130, 85, 270, 250, 270)

    def _cell(parent, text, row, col, bg, bold=False, header=False):
        fs = font_size.get()
        font = ("Segoe UI", fs + (1 if header else 0), "bold" if (bold or header) else "normal")
        wrap = max(80, column_widths[col] - 16)
        label = tk.Label(
            parent, text=text, bg=bg, fg=COLORS["navy"], font=font,
            justify="left" if col in (0, 3, 4, 5) else "center",
            anchor="w" if col in (0, 3, 4, 5) else "center",
            wraplength=wrap, padx=8, pady=7,
        )
        label.grid(row=row, column=col, sticky="nsew", padx=(1 if col else 0), pady=(1 if row else 0))
        parent.grid_columnconfigure(col, minsize=column_widths[col])
        return label

    def _render():
        for child in table_host.winfo_children():
            child.destroy()
        t = TABLES[state["index"]]
        title_var.set(t["title"] + " · " + t["subtitle"])
        headers = (t.get("first", "Parámetro"), "Norma", "DE", "Si está menor a la norma", "Si está en la norma", "Si está mayor a la norma")
        header_bg = (COLORS["header"], COLORS["header"], COLORS["header"], COLORS["low"], COLORS["normal"], COLORS["high"])
        for c, text in enumerate(headers):
            _cell(table_host, text, 0, c, header_bg[c], header=True)
        for r, values in enumerate(t["rows"], start=1):
            backgrounds = (COLORS["white"], COLORS["white"], COLORS["white"], COLORS["low"], COLORS["normal"], COLORS["high"])
            for c, text in enumerate(values):
                _cell(table_host, text, r, c, backgrounds[c], bold=(c == 0))
        note_var.set(t.get("note", ""))
        source_var.set("Fuente principal: " + t["source"])
        table_host.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

    def _select(index):
        state["index"] = int(index)
        lst.selection_clear(0, "end")
        lst.selection_set(state["index"])
        lst.see(state["index"])
        _render()

    def _from_list(_event=None):
        sel = lst.curselection()
        if sel:
            _select(sel[0])

    def _change_font(delta):
        font_size.set(max(8, min(15, font_size.get() + delta)))
        size_lbl.set(f"{int(round(font_size.get() / 10 * 100))}%")
        _render()

    ttk.Button(tool, text="A−", width=4, command=lambda: _change_font(-1)).pack(side="right", padx=2)
    ttk.Button(tool, text="A+", width=4, command=lambda: _change_font(1)).pack(side="right", padx=2)
    ttk.Label(tool, textvariable=size_lbl, width=7, anchor="center").pack(side="right", padx=4)
    ttk.Button(nav, text="◀ Anterior", command=lambda: _select(max(0, state["index"] - 1))).pack(side="left")
    ttk.Button(nav, text="Siguiente ▶", command=lambda: _select(min(len(TABLES) - 1, state["index"] + 1))).pack(side="left", padx=5)
    ttk.Button(nav, text="Cerrar", command=win.destroy).pack(side="right")

    def _resize_canvas(event):
        bbox = canvas.bbox(window_id)
        if bbox:
            natural = max(sum(column_widths), bbox[2] - bbox[0])
            canvas.itemconfigure(window_id, width=max(event.width - 4, natural))

    lst.bind("<<ListboxSelect>>", _from_list)
    canvas.bind("<Configure>", _resize_canvas)
    win.bind("<Escape>", lambda _e: win.destroy())
    win.bind("<Control-plus>", lambda _e: _change_font(1))
    win.bind("<Control-minus>", lambda _e: _change_font(-1))

    start = 0
    if initial:
        key = initial.casefold()
        for i, t in enumerate(TABLES):
            if key in {t["id"].casefold(), t["title"].casefold()}:
                start = i
                break
    win.after_idle(lambda: _select(start))


def attach_help_button(root, *, compact: bool = False) -> None:
    if getattr(root, "_yornis_reference_help_button", None) is not None:
        return
    from tkinter import ttk
    text = "Ayuda · Referencias" if compact else "Ayuda · Tablas de referencia"
    btn = ttk.Button(root, text=text, command=lambda: open_reference_help(root))
    btn.place(relx=1.0, x=-18, y=14, anchor="ne")
    try:
        btn.lift()
    except Exception:
        pass
    root._yornis_reference_help_button = btn
    root.bind("<F1>", lambda _e: open_reference_help(root), add="+")
