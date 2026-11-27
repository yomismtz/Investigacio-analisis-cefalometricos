from __future__ import annotations

import tempfile
from html import escape
from pathlib import Path

from PIL import Image, ImageDraw
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image as RLImage,
    LongTable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from research_protocol import selected_variables, trace_qc
import yornis_theme


def _safe_text(value, fallback="—"):
    if value is None or str(value).strip() == "":
        return fallback
    return escape(str(value))


def _paragraph(value, style):
    return Paragraph(_safe_text(value), style)


def _page_chrome(theme):
    primary = colors.HexColor(theme.get("primary", "#6D35A4"))

    def draw(canvas, doc):
        canvas.saveState()
        width, height = A4
        canvas.setStrokeColor(primary)
        canvas.setLineWidth(0.6)
        canvas.line(17 * mm, height - 13 * mm, width - 17 * mm, height - 13 * mm)
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(colors.HexColor("#666666"))
        canvas.drawString(17 * mm, 9 * mm, "Yornis · Informe cefalométrico · Uso educativo y de investigación")
        canvas.drawRightString(width - 17 * mm, 9 * mm, f"Página {doc.page}")
        canvas.restoreState()

    return draw


def annotated_image(db, case_id, target):
    case = db.case(case_id)
    protocol_version = db.case_protocol_version(case_id)
    points = db.latest_landmarks(case_id, protocol_version)
    protocol = db.protocol_by_version(case["study_id"], protocol_version)["config"]
    with Image.open(case["image_path"]) as source:
        image = source.convert("RGB")
    draw = ImageDraw.Draw(image, "RGBA")
    theme = yornis_theme.THEMES[yornis_theme.current_theme_name()]

    def rgba(hex_value, alpha=255):
        value = str(hex_value).lstrip("#")
        return tuple(int(value[index:index + 2], 16) for index in (0, 2, 4)) + (alpha,)

    line = rgba(theme["tertiary"], 105)
    dot = rgba(theme["accent"], 240)
    ring = rgba(theme["primary"], 235)
    seen = set()

    for variable in selected_variables(protocol.get("selected_variables") or []):
        ordered = [points[name] for name in variable.points if name in points]
        for first, second in zip(ordered, ordered[1:]):
            key = tuple(sorted((first, second)))
            if key not in seen:
                draw.line([first, second], fill=line, width=2)
                seen.add(key)

    radius = max(3, round(max(image.size) / 700))
    for name, (x, y) in points.items():
        draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill=dot, outline=ring, width=2)
        draw.text((x + radius + 4, y - radius - 10), str(name), fill=(255, 255, 255, 245))

    image.thumbnail((1800, 1800), Image.Resampling.LANCZOS)
    image.save(target, format="JPEG", quality=92, optimize=True)
    return target


def _fit_report_image(path, max_width, max_height):
    image = RLImage(str(path))
    image._restrictSize(max_width, max_height)
    return image


def export_case_pdf(db, case_id, path):
    case = db.case(case_id)
    if not case:
        raise KeyError(f"Case not found: {case_id}")
    study = db.study(case["study_id"])
    protocol_version = db.case_protocol_version(case_id)
    protocol_row = db.protocol_by_version(case["study_id"], protocol_version)
    protocol = protocol_row["config"]
    results = [dict(row) for row in db.latest_results(case_id, protocol_version)]
    points = db.latest_landmarks(case_id, protocol_version)
    calibration = case["case_mm_per_px"] or study["study_mm_per_px"]
    variables = selected_variables(protocol.get("selected_variables") or [])

    theme = yornis_theme.THEMES[yornis_theme.current_theme_name()]
    accent = colors.HexColor(theme.get("primary", "#6D35A4"))
    border = colors.HexColor(theme.get("border", "#D8D0E2"))
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "YornisReportTitle", parent=styles["Title"], fontName="Helvetica-Bold",
        fontSize=19, leading=23, textColor=accent, alignment=TA_LEFT, spaceAfter=5,
    )
    section_style = ParagraphStyle(
        "YornisSection", parent=styles["Heading2"], fontSize=10, leading=13,
        textColor=accent, spaceBefore=8, spaceAfter=5,
    )
    body_style = ParagraphStyle(
        "YornisBody", parent=styles["BodyText"], fontSize=8, leading=11,
        spaceAfter=2, wordWrap="CJK",
    )
    small_style = ParagraphStyle(
        "YornisSmall", parent=body_style, fontSize=6.4, leading=8,
    )
    cell_style = ParagraphStyle(
        "YornisCell", parent=small_style, splitLongWords=1,
    )
    header_style = ParagraphStyle(
        "YornisHeader", parent=cell_style, textColor=colors.white,
        fontName="Helvetica-Bold",
    )
    doc = SimpleDocTemplate(
        str(path), pagesize=A4, rightMargin=17*mm, leftMargin=17*mm,
        topMargin=19*mm, bottomMargin=16*mm, title=f"Yornis · {case['study_code']}",
        author="Yornis",
    )
    story = [
        Paragraph("Yornis · Informe cefalométrico", title_style),
        Paragraph(_safe_text(study["title"]), section_style),
        Paragraph(
            f"Caso: {_safe_text(case['study_code'])}  ·  Protocolo: v{protocol_version}  ·  "
            f"Estado: {_safe_text(case['status'])}",
            body_style,
        ),
    ]

    metadata = [
        ["Código de caso", case["study_code"] or "—", "Sexo", case["sex"] or "—"],
        ["Edad", f"{case['age']} años" if case["age"] is not None else "—", "Examinador", case["examiner"] or "—"],
        ["Radiografía", case["original_filename"] or Path(case["image_path"] or "").name or "—", "Revisión", case["image_revision"]],
        ["Calibración", f"{float(calibration):.6f} mm/píxel" if calibration else "No registrada", "Landmarks", f"{len(points)} colocados"],
    ]
    meta = Table(
        [[_paragraph(v, cell_style) for v in row] for row in metadata],
        colWidths=[27*mm, 63*mm, 24*mm, 58*mm],
        hAlign="LEFT",
    )
    meta.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#F1ECF7")),
        ("BACKGROUND", (2,0), (2,-1), colors.HexColor("#F1ECF7")),
        ("GRID", (0,0), (-1,-1), 0.35, border),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING", (0,0), (-1,-1), 5),
        ("RIGHTPADDING", (0,0), (-1,-1), 5),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTNAME", (2,0), (2,-1), "Helvetica-Bold"),
    ]))
    story += [meta, Spacer(1, 7)]

    with tempfile.TemporaryDirectory(prefix="yornis_report_") as temp_dir:
        temp = Path(temp_dir)
        image_path = Path(case["image_path"]) if case["image_path"] else None
        if image_path and image_path.is_file():
            if image_path.suffix.lower() not in {".pdf"}:
                try:
                    original_target = temp / "radiograph_original.jpg"
                    annotated_target = temp / "radiograph_annotated.jpg"
                    with Image.open(image_path) as source:
                        original = source.convert("RGB")
                        original.thumbnail((1800, 1800), Image.Resampling.LANCZOS)
                        original.save(original_target, "JPEG", quality=90, optimize=True)
                    annotated_image(db, case_id, annotated_target)
                    image_pair = Table(
                        [[
                            _fit_report_image(original_target, 82*mm, 58*mm),
                            _fit_report_image(annotated_target, 82*mm, 58*mm),
                        ], [
                            Paragraph("Radiografía original", small_style),
                            Paragraph("Radiografía con landmarks y trazos", small_style),
                        ]],
                        colWidths=[88*mm, 88*mm],
                        hAlign="LEFT",
                    )
                    image_pair.setStyle(TableStyle([
                        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
                        ("ALIGN", (0,0), (-1,-1), "CENTER"),
                        ("LEFTPADDING", (0,0), (-1,-1), 2),
                        ("RIGHTPADDING", (0,0), (-1,-1), 2),
                        ("TOPPADDING", (0,0), (-1,-1), 2),
                        ("BOTTOMPADDING", (0,0), (-1,-1), 2),
                    ]))
                    story += [Paragraph("Radiografía y trazado", section_style), image_pair, Spacer(1, 6)]
                except Exception as exc:
                    story.append(Paragraph(
                        f"No fue posible incrustar la radiografía: {_safe_text(type(exc).__name__)}.",
                        small_style,
                    ))
            else:
                story.append(Paragraph(
                    "La imagen de origen es un PDF. Se conserva como archivo fuente, pero no se rasteriza dentro de este informe.",
                    small_style,
                ))

        story.append(Paragraph("Control técnico del trazado", section_style))
        try:
            qc_items = trace_qc(protocol.get("selected_variables") or [], points, calibration)
        except Exception:
            qc_items = []
        if qc_items:
            qc_data = [[Paragraph("Nivel", header_style), Paragraph("Hallazgo", header_style)]]
            for item in qc_items:
                qc_data.append([
                    _paragraph(item.get("level", "review"), cell_style),
                    _paragraph(item.get("message", item.get("code", "")), cell_style),
                ])
            qc_table = Table(qc_data, colWidths=[25*mm, 151*mm], repeatRows=1, hAlign="LEFT")
            qc_table.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,0), accent),
                ("GRID", (0,0), (-1,-1), 0.3, border),
                ("VALIGN", (0,0), (-1,-1), "TOP"),
                ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#FAF8FC")]),
                ("LEFTPADDING", (0,0), (-1,-1), 4),
                ("RIGHTPADDING", (0,0), (-1,-1), 4),
                ("TOPPADDING", (0,0), (-1,-1), 4),
                ("BOTTOMPADDING", (0,0), (-1,-1), 4),
            ]))
            story += [qc_table, Spacer(1, 6)]
        else:
            story.append(Paragraph("No se pudo reconstruir el control técnico a partir del protocolo guardado.", small_style))

        story.append(Paragraph("Resultados", section_style))
        table_data = [[
            Paragraph("Análisis", header_style),
            Paragraph("Medición", header_style),
            Paragraph("Valor", header_style),
            Paragraph("Unidad", header_style),
            Paragraph("Referencia", header_style),
            Paragraph("Interpretación", header_style),
        ]]
        for result in results:
            value = result.get("value")
            try:
                value_text = f"{float(value):.3f}" if value is not None else "—"
            except (TypeError, ValueError, OverflowError):
                value_text = str(value)
            table_data.append([
                _paragraph(result.get("analysis"), cell_style),
                _paragraph(result.get("measurement"), cell_style),
                _paragraph(value_text, cell_style),
                _paragraph(result.get("unit"), cell_style),
                _paragraph(result.get("reference_text"), cell_style),
                _paragraph(result.get("interpretation"), cell_style),
            ])
        if len(table_data) == 1:
            table_data.append([Paragraph("No hay resultados vigentes para esta imagen y versión de protocolo.", cell_style), "", "", "", "", ""])
        results_table = LongTable(
            table_data,
            colWidths=[25*mm, 38*mm, 17*mm, 15*mm, 39*mm, 42*mm],
            repeatRows=1,
            hAlign="LEFT",
            splitByRow=1,
        )
        results_table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), accent),
            ("GRID", (0,0), (-1,-1), 0.3, border),
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#FAF8FC")]),
            ("LEFTPADDING", (0,0), (-1,-1), 3),
            ("RIGHTPADDING", (0,0), (-1,-1), 3),
            ("TOPPADDING", (0,0), (-1,-1), 4),
            ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ]))
        story += [results_table, Spacer(1, 8)]
        story.append(Paragraph(
            "Alcance: documento de apoyo educativo y de investigación. El control de calidad incluido es técnico/geométrico; no constituye validación clínica ni sustituye la interpretación profesional. Los valores y referencias se muestran tal como fueron guardados para el caso y el protocolo indicados.",
            small_style,
        ))
        doc.build(story, onFirstPage=_page_chrome(theme), onLaterPages=_page_chrome(theme))

    db.audit(
        case["study_id"], "export_case_pdf_yornis", case_id=case_id,
        target=str(path), protocol_version=protocol_version,
        result_count=len(results), landmark_count=len(points),
    )
    return str(path)
