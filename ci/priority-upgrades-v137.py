from pathlib import Path
import re

ROOT = Path('.')
JAVA = ROOT / 'app/src/main/java/com/cefalo/angulos'
TEST = ROOT / 'app/src/test/java/com/cefalo/angulos'
TEST.mkdir(parents=True, exist_ok=True)

# -----------------------------------------------------------------------------
# v1.37: turn the post-audit priorities into user-facing functionality.
# - Analysis selector before tracing.
# - Trace quality-control summary.
# - Research CSV export with measurements + placed landmark coordinates.
# - Preserve partial-analysis behavior and Sassouni-only workflows.
# -----------------------------------------------------------------------------
gradle = ROOT / 'app/build.gradle'
g = gradle.read_text(encoding='utf-8')
g = re.sub(r'versionCode\s+\d+', 'versionCode 38', g, count=1)
g = re.sub(r"versionName\s+'[^']+'", "versionName '1.37'", g, count=1)
gradle.write_text(g, encoding='utf-8')

# -----------------------------------------------------------------------------
# AnalysisProfile: pure-Java profile selection/filtering so it can be unit-tested.
# -----------------------------------------------------------------------------
profile = JAVA / 'AnalysisProfile.java'
profile.write_text(r'''package com.cefalo.angulos;

import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;

public final class AnalysisProfile {
    public static final String EXTRA_SELECTED = "SELECTED_ANALYSES";
    public static final String ALL = "ALL";

    public static final String STEINER = "STEINER";
    public static final String DOWNS = "DOWNS";
    public static final String TWEED = "TWEED";
    public static final String RICKETTS = "RICKETTS";
    public static final String BJORK = "BJORK_JARABAK";
    public static final String MCNAMARA = "MCNAMARA";
    public static final String WITS = "WITS";
    public static final String HOLDAWAY = "HOLDAWAY";
    public static final String POWELL = "POWELL";
    public static final String BURSTONE = "BURSTONE_COGS";
    public static final String LEGAN = "LEGAN_BURSTONE";
    public static final String SASSOUNI = "SASSOUNI";
    public static final String CERVICAL = "CERVICAL";
    public static final String AIRWAY = "AIRWAY";

    private static final String[] IDS = {
            STEINER, DOWNS, TWEED, RICKETTS, BJORK, MCNAMARA, WITS,
            HOLDAWAY, POWELL, BURSTONE, LEGAN, SASSOUNI, CERVICAL, AIRWAY
    };

    private static final String[] LABELS = {
            "Steiner",
            "Downs",
            "Tweed",
            "Ricketts",
            "Björk–Jarabak",
            "McNamara",
            "Jacobson · Wits",
            "Holdaway",
            "Powell",
            "Burstone COGS",
            "Legan–Burstone · tejidos blandos",
            "Sassouni · arquitectura",
            "Cráneo-cervical / Rocabado",
            "Vía aérea 2D"
    };

    private AnalysisProfile() {}

    public static String[] ids() { return IDS.clone(); }
    public static String[] labels() { return LABELS.clone(); }

    public static boolean isAll(String csv) {
        return csv == null || csv.trim().isEmpty() || ALL.equalsIgnoreCase(csv.trim());
    }

    public static boolean includes(String csv, String id) {
        if (isAll(csv)) return true;
        for (String token : csv.split(",")) {
            if (id.equalsIgnoreCase(token.trim())) return true;
        }
        return false;
    }

    public static String normalize(String csv) {
        if (isAll(csv)) return ALL;
        Set<String> valid = new LinkedHashSet<>();
        for (String raw : csv.split(",")) {
            String token = raw.trim();
            for (String id : IDS) {
                if (id.equalsIgnoreCase(token)) {
                    valid.add(id);
                    break;
                }
            }
        }
        if (valid.isEmpty() || valid.size() == IDS.length) return ALL;
        StringBuilder out = new StringBuilder();
        for (String id : valid) {
            if (out.length() > 0) out.append(',');
            out.append(id);
        }
        return out.toString();
    }

    public static String displayLabel(String csv) {
        if (isAll(csv)) return "Integral · todos los análisis";
        List<String> selected = new ArrayList<>();
        for (int i = 0; i < IDS.length; i++) {
            if (includes(csv, IDS[i])) selected.add(LABELS[i]);
        }
        if (selected.size() <= 3) {
            StringBuilder out = new StringBuilder();
            for (String label : selected) {
                if (out.length() > 0) out.append(" + ");
                out.append(label);
            }
            return out.toString();
        }
        return selected.size() + " análisis seleccionados";
    }

    public static List<MeasurementDefinition> filterAngular(
            List<MeasurementDefinition> source, String csv) {
        if (source == null) return new ArrayList<>();
        if (isAll(csv)) return new ArrayList<>(source);
        List<MeasurementDefinition> out = new ArrayList<>();
        for (MeasurementDefinition def : source) {
            if (def != null && matches(def.name, csv, false)) out.add(def);
        }
        return out;
    }

    public static List<LinearMeasurementDefinition> filterLinear(
            List<LinearMeasurementDefinition> source, String csv) {
        if (source == null) return new ArrayList<>();
        if (isAll(csv)) return new ArrayList<>(source);
        List<LinearMeasurementDefinition> out = new ArrayList<>();
        for (LinearMeasurementDefinition def : source) {
            if (def != null && matches(def.name, csv, true)) out.add(def);
        }
        return out;
    }

    private static boolean matches(String rawName, String csv, boolean linear) {
        String name = rawName == null ? "" : rawName;

        if (includes(csv, DOWNS) && name.startsWith("Downs")) return true;
        if (includes(csv, RICKETTS) && name.startsWith("Ricketts")) return true;
        if (includes(csv, MCNAMARA) && name.startsWith("McNamara")) return true;
        if (includes(csv, WITS) && name.startsWith("Jacobson")) return true;
        if (includes(csv, HOLDAWAY) && name.startsWith("Holdaway")) return true;
        if (includes(csv, BURSTONE) && name.startsWith("Burstone COGS")) return true;
        if (includes(csv, LEGAN) && name.startsWith("Legan-Burstone")) return true;
        if (includes(csv, SASSOUNI) && name.startsWith("Sassouni")) return true;

        if (includes(csv, TWEED)
                && ("FMA".equals(name) || "FMIA".equals(name) || "IMPA".equals(name))) {
            return true;
        }

        if (includes(csv, POWELL)
                && ("Nasofrontal".equals(name)
                || "Nasofacial".equals(name)
                || "Nasomental".equals(name)
                || "Mentocervical".equals(name))) {
            return true;
        }

        if (includes(csv, BJORK)
                && (name.contains("Björk")
                || name.contains("Jarabak")
                || name.contains("Ángulo de la silla")
                || name.contains("Ángulo articular")
                || name.contains("goníaco Ar-Go-Me"))) {
            return true;
        }

        if (includes(csv, CERVICAL) && isCervical(name)) return true;
        if (includes(csv, AIRWAY) && isAirway(name)) return true;
        if (includes(csv, STEINER) && isSteiner(name, linear)) return true;

        return false;
    }

    private static boolean isSteiner(String name, boolean linear) {
        if (name.startsWith("Steiner")) return true;
        if (linear) {
            return name.equals("Segmento SL")
                    || name.equals("Segmento SE")
                    || name.startsWith("Incisivo superior a NA")
                    || name.startsWith("Incisivo inferior a NB");
        }
        return name.equals("SNA")
                || name.equals("SNB")
                || name.equals("ANB")
                || name.equals("SND")
                || name.equals("SN / Go-Gn")
                || name.equals("Eje Y · NS / S-Gn")
                || name.equals("Incisivo superior / SN")
                || name.startsWith("Incisivo superior / NA")
                || name.startsWith("Incisivo inferior / NB")
                || name.equals("Plano oclusal / SN")
                || name.equals("Ángulo interincisal");
    }

    private static boolean isCervical(String name) {
        return name.contains("cráneo-odontoideo")
                || name.equals("SN / OPT")
                || name.equals("SN / CVT")
                || name.startsWith("Curvatura cervical")
                || name.startsWith("Espacio C0-C1")
                || name.startsWith("Espacio C1-C2")
                || name.equals("C3-RGn")
                || name.equals("C3-H")
                || name.equals("H-RGn")
                || name.startsWith("Altura / posición del hioides")
                || name.startsWith("Profundidad de la columna cervical")
                || name.startsWith("Dimensión AP ósea de nasofaringe");
    }

    private static boolean isAirway(String name) {
        return name.startsWith("AD1")
                || name.startsWith("AD2")
                || name.startsWith("AD3")
                || name.startsWith("Faringe")
                || name.contains("vía aérea")
                || name.contains("nasofaringe");
    }
}
''', encoding='utf-8')

# -----------------------------------------------------------------------------
# MainActivity: selector before opening the tracing screen.
# -----------------------------------------------------------------------------
main = JAVA / 'MainActivity.java'
m = main.read_text(encoding='utf-8')

if 'import android.widget.Toast;' not in m:
    m = m.replace('import android.widget.TextView;\n', 'import android.widget.TextView;\nimport android.widget.Toast;\n', 1)
if 'import java.util.ArrayList;' not in m:
    m = m.replace('public class MainActivity extends AppCompatActivity {',
                  'import java.util.ArrayList;\nimport java.util.List;\n\npublic class MainActivity extends AppCompatActivity {', 1)

m = m.replace(
    '        setSafeClick(btnSteiner, v -> openAnalysis("STEINER"));',
    '        setSafeClick(btnSteiner, v -> showAnalysisSelector());',
    1,
)

if 'private void showAnalysisSelector()' not in m:
    anchor = '    private void openAnalysis(String mode) {\n'
    method = r'''    private void showAnalysisSelector() {
        final String[] ids = AnalysisProfile.ids();
        final String[] labels = AnalysisProfile.labels();
        final boolean[] checked = new boolean[ids.length];
        String saved = getSharedPreferences(PREFS, MODE_PRIVATE)
                .getString("last_analysis_selection", AnalysisProfile.ALL);

        for (int i = 0; i < ids.length; i++) {
            checked[i] = AnalysisProfile.isAll(saved) || AnalysisProfile.includes(saved, ids[i]);
        }

        AlertDialog dialog = new AlertDialog.Builder(this)
                .setTitle("¿Qué análisis desea realizar?")
                .setMultiChoiceItems(labels, checked, (unused, which, isChecked) ->
                        checked[which] = isChecked)
                .setNegativeButton("Cancelar", null)
                .setNeutralButton("Seleccionar todo", null)
                .setPositiveButton("Comenzar", null)
                .create();

        dialog.setOnShowListener(unused -> {
            dialog.getButton(AlertDialog.BUTTON_NEUTRAL).setOnClickListener(v -> {
                for (int i = 0; i < checked.length; i++) {
                    checked[i] = true;
                    dialog.getListView().setItemChecked(i, true);
                }
            });

            dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v -> {
                List<String> selected = new ArrayList<>();
                for (int i = 0; i < checked.length; i++) {
                    if (checked[i]) selected.add(ids[i]);
                }
                if (selected.isEmpty()) {
                    Toast.makeText(this, "Seleccione al menos un análisis.", Toast.LENGTH_SHORT).show();
                    return;
                }

                String selection;
                if (selected.size() == ids.length) {
                    selection = AnalysisProfile.ALL;
                } else {
                    StringBuilder csv = new StringBuilder();
                    for (String id : selected) {
                        if (csv.length() > 0) csv.append(',');
                        csv.append(id);
                    }
                    selection = csv.toString();
                }

                getSharedPreferences(PREFS, MODE_PRIVATE)
                        .edit()
                        .putString("last_analysis_selection", selection)
                        .apply();

                dialog.dismiss();
                openAnalysis("STEINER", selection);
            });
        });

        dialog.show();
    }

'''
    if anchor not in m:
        raise RuntimeError('MainActivity openAnalysis anchor not found')
    m = m.replace(anchor, method + anchor, 1)

old_open = '''    private void openAnalysis(String mode) {
        Intent intent = new Intent(this, AnalysisActivity.class);
        intent.putExtra("MODE", mode);
        startActivity(intent);
    }
'''
new_open = '''    private void openAnalysis(String mode) {
        openAnalysis(mode, AnalysisProfile.ALL);
    }

    private void openAnalysis(String mode, String selectedAnalyses) {
        Intent intent = new Intent(this, AnalysisActivity.class);
        intent.putExtra("MODE", mode);
        intent.putExtra(AnalysisProfile.EXTRA_SELECTED, AnalysisProfile.normalize(selectedAnalyses));
        startActivity(intent);
    }
'''
if old_open in m:
    m = m.replace(old_open, new_open, 1)
elif 'openAnalysis(String mode, String selectedAnalyses)' not in m:
    raise RuntimeError('Could not extend MainActivity openAnalysis')
main.write_text(m, encoding='utf-8')

# -----------------------------------------------------------------------------
# AnalysisActivity: filter catalogs, persist selection, QC, and CSV export.
# -----------------------------------------------------------------------------
activity = JAVA / 'AnalysisActivity.java'
a = activity.read_text(encoding='utf-8')

# imports / fields
if 'private static final int REQ_SAVE_CSV' not in a:
    a = a.replace('    private static final int REQ_SAVE_PDF = 1004;\n',
                  '    private static final int REQ_SAVE_PDF = 1004;\n    private static final int REQ_SAVE_CSV = 1005;\n', 1)
if 'private String selectedAnalyses' not in a:
    a = a.replace('    private String mode;\n',
                  '    private String mode;\n    private String selectedAnalyses = AnalysisProfile.ALL;\n', 1)
if 'private String pendingCsvText;' not in a:
    a = a.replace('    private Bitmap pendingPdfBitmap;\n',
                  '    private Bitmap pendingPdfBitmap;\n    private String pendingCsvText;\n', 1)

# Resolve saved/intent selection before catalogs are built.
selection_anchor = '        setContentView(R.layout.activity_analysis);\n'
if 'AnalysisProfile.EXTRA_SELECTED' not in a[:a.find(selection_anchor)]:
    selection_block = r'''        String savedSelection = savedInstanceState == null
                ? null
                : savedInstanceState.getString(AnalysisProfile.EXTRA_SELECTED);
        if ((savedSelection == null || savedSelection.trim().isEmpty()) && studyId != null) {
            savedSelection = getSharedPreferences("yomceph_analysis_profiles", MODE_PRIVATE)
                    .getString(studyId, null);
        }
        if (savedSelection == null || savedSelection.trim().isEmpty()) {
            savedSelection = getIntent().getStringExtra(AnalysisProfile.EXTRA_SELECTED);
        }
        selectedAnalyses = AnalysisProfile.normalize(savedSelection);

'''
    if selection_anchor not in a:
        raise RuntimeError('AnalysisActivity setContentView anchor not found')
    a = a.replace(selection_anchor, selection_block + selection_anchor, 1)

# Apply filters after the comprehensive catalog has been assembled by earlier passes.
landmark_anchor = '        landmarks = buildLandmarkList(definitions, linearDefinitions);\n'
if 'AnalysisProfile.filterAngular' not in a:
    filter_block = r'''        if ("STEINER".equals(mode)) {
            definitions = AnalysisProfile.filterAngular(definitions, selectedAnalyses);
            linearDefinitions = AnalysisProfile.filterLinear(linearDefinitions, selectedAnalyses);
        }

'''
    if landmark_anchor not in a:
        raise RuntimeError('AnalysisActivity landmark anchor not found')
    a = a.replace(landmark_anchor, filter_block + landmark_anchor, 1)

# Show selected analysis profile under study info/title.
mode_title_old = '        return "Análisis de Steiner";\n'
mode_title_new = '        return "Análisis cefalométrico · " + AnalysisProfile.displayLabel(selectedAnalyses);\n'
if mode_title_old in a:
    a = a.replace(mode_title_old, mode_title_new, 1)

# Persist selection on rotation.
if 'outState.putString(AnalysisProfile.EXTRA_SELECTED' not in a:
    a = a.replace('        outState.putString("MODE", mode);\n',
                  '        outState.putString("MODE", mode);\n        outState.putString(AnalysisProfile.EXTRA_SELECTED, selectedAnalyses);\n', 1)

# Persist selection with the study using a small sidecar SharedPreferences key.
save_anchor = '        SavedStudyStore.save(\n                this,\n                study\n        );\n'
if 'yomceph_analysis_profiles' not in a[a.find('private boolean saveStudy'):]:
    save_extra = r'''        getSharedPreferences("yomceph_analysis_profiles", MODE_PRIVATE)
                .edit()
                .putString(study.id, selectedAnalyses)
                .apply();

'''
    if save_anchor not in a:
        raise RuntimeError('SavedStudyStore.save anchor not found')
    a = a.replace(save_anchor, save_anchor + '\n' + save_extra, 1)

# Sassouni landmarks should only be requested when Sassouni is selected.
sass_old = r'''        String[] sassouniArchitecture = {
                "Sella inf.", "ACB post.", "ACB ant.",
                "Sass Oc post.", "Sass Oc ant.",
                "Mand base post.", "Mand base ant.",
                "Sp", "FE", "U6 raíz", "L6 raíz",
                "Rama post sup.", "Rama post inf."
        };
        for (String label : sassouniArchitecture) ordered.add(label);
'''
sass_new = r'''        if (AnalysisProfile.includes(selectedAnalyses, AnalysisProfile.SASSOUNI)) {
            String[] sassouniArchitecture = {
                    "Sella inf.", "ACB post.", "ACB ant.",
                    "ENP", "ENA", "N", "Me",
                    "Sass Oc post.", "Sass Oc ant.",
                    "Mand base post.", "Mand base ant.",
                    "Sp", "FE", "Pg", "Go",
                    "IS borde", "IS ápice", "II borde", "II ápice",
                    "U6 cusp", "U6 raíz", "L6 cusp", "L6 raíz",
                    "Rama post sup.", "Rama post inf."
            };
            for (String label : sassouniArchitecture) ordered.add(label);
        }
'''
if sass_old in a:
    a = a.replace(sass_old, sass_new, 1)
elif 'AnalysisProfile.includes(selectedAnalyses, AnalysisProfile.SASSOUNI)' not in a:
    raise RuntimeError('Sassouni landmark block changed upstream')

# Sassouni summary only when selected.
if 'private String sassouniSummaryText()' in a and 'if (!AnalysisProfile.includes(selectedAnalyses, AnalysisProfile.SASSOUNI)) return null;' not in a:
    a = a.replace('    private String sassouniSummaryText() {\n',
                  '    private String sassouniSummaryText() {\n        if (!AnalysisProfile.includes(selectedAnalyses, AnalysisProfile.SASSOUNI)) return null;\n', 1)

# Quality-control helper and CSV generator.
quality_anchor = '    private void calculateFullAnalysis() {\n'
if 'private String traceQualityText()' not in a:
    helpers = r'''    private String traceQualityText() {
        if (measurementView == null) return "Control de calidad no disponible.";
        List<PointF> pts = measurementView.getPointsSnapshot();
        List<String> labels = measurementView.getLandmarkLabels();
        int placed = measurementView.getPlacedCount();
        int total = measurementView.getTotalCount();
        int nearDuplicates = 0;
        String firstDuplicate = null;

        for (int i = 0; i < pts.size(); i++) {
            PointF a = pts.get(i);
            if (a == null) continue;
            for (int j = i + 1; j < pts.size(); j++) {
                PointF b = pts.get(j);
                if (b == null) continue;
                if (Math.hypot(a.x - b.x, a.y - b.y) < 1.5) {
                    nearDuplicates++;
                    if (firstDuplicate == null) {
                        firstDuplicate = labels.get(i) + " / " + labels.get(j);
                    }
                }
            }
        }

        int degenerate = 0;
        for (MeasurementDefinition def : definitions) {
            if (def == null || def.pointLabels == null) continue;
            if (def.type == MeasurementDefinition.Type.THREE_POINTS && def.pointLabels.length >= 3) {
                PointF p0 = measurementView.getPoint(def.pointLabels[0]);
                PointF p1 = measurementView.getPoint(def.pointLabels[1]);
                PointF p2 = measurementView.getPoint(def.pointLabels[2]);
                if (tooClose(p0, p1) || tooClose(p1, p2)) degenerate++;
            } else if (def.type == MeasurementDefinition.Type.TWO_LINES && def.pointLabels.length >= 4) {
                if (tooClose(measurementView.getPoint(def.pointLabels[0]), measurementView.getPoint(def.pointLabels[1]))
                        || tooClose(measurementView.getPoint(def.pointLabels[2]), measurementView.getPoint(def.pointLabels[3]))) {
                    degenerate++;
                }
            } else if (def.type == MeasurementDefinition.Type.SIGNED_ANB && def.pointLabels.length >= 4) {
                if (tooClose(measurementView.getPoint(def.pointLabels[0]), measurementView.getPoint(def.pointLabels[1]))) {
                    degenerate++;
                }
            }
        }

        boolean needsCalibration = !linearDefinitions.isEmpty();
        boolean calibrated = !Double.isNaN(mmPerPixel) && mmPerPixel > 0.0;
        int warnings = nearDuplicates + degenerate + ((needsCalibration && !calibrated) ? 1 : 0);

        StringBuilder text = new StringBuilder();
        text.append("Control de calidad del trazado · ");
        text.append(warnings == 0 ? "SIN ALERTAS GEOMÉTRICAS" : warnings + " advertencia(s)");
        text.append("\nPuntos colocados: ").append(placed).append(" / ").append(total);
        text.append(" · Perfil: ").append(AnalysisProfile.displayLabel(selectedAnalyses));
        if (needsCalibration) {
            text.append("\nCalibración lineal: ").append(calibrated ? "OK" : "PENDIENTE");
        }
        if (nearDuplicates > 0) {
            text.append("\nPuntos casi superpuestos: ").append(nearDuplicates);
            if (firstDuplicate != null) text.append(" · revise ").append(firstDuplicate);
        }
        if (degenerate > 0) {
            text.append("\nConstrucciones con eje demasiado corto: ").append(degenerate);
        }
        text.append("\nEstas alertas detectan problemas geométricos/técnicos; no emiten diagnóstico clínico.");
        return text.toString();
    }

    private boolean tooClose(PointF a, PointF b) {
        return a != null && b != null && Math.hypot(a.x - b.x, a.y - b.y) < 3.0;
    }

    private String csvEscape(String value) {
        String s = value == null ? "" : value;
        return "\"" + s.replace("\"", "\"\"") + "\"";
    }

    private String buildResearchCsv() {
        StringBuilder csv = new StringBuilder();
        csv.append("record_type,study_id,study_name,patient_id,age,sex,analysis_profile,item,value,unit,reference,diagnosis,x_px,y_px,calibration\n");
        String cal = (!Double.isNaN(mmPerPixel) && mmPerPixel > 0.0)
                ? calibrationLabel + " · " + String.format(Locale.US, "%.6f mm/px", mmPerPixel)
                : "sin calibración";

        for (MeasurementDefinition def : definitions) {
            Double value = measurementView.calculate(def);
            if (value == null) continue;
            csv.append("ANGULAR,")
                    .append(csvEscape(studyId)).append(',')
                    .append(csvEscape(studyName)).append(',')
                    .append(csvEscape(patientName)).append(',')
                    .append(csvEscape(patientAge)).append(',')
                    .append(csvEscape(patientSex)).append(',')
                    .append(csvEscape(selectedAnalyses)).append(',')
                    .append(csvEscape(def.name)).append(',')
                    .append(String.format(Locale.US, "%.4f", value)).append(',')
                    .append("deg,")
                    .append(csvEscape(angularNormText(def, value))).append(',')
                    .append(csvEscape(angularDiagnosis(def, value))).append(",,,")
                    .append(csvEscape(cal)).append('\n');
        }

        for (LinearMeasurementDefinition def : linearDefinitions) {
            Double value = calculateLinear(def);
            if (value == null) continue;
            String unit = def.type == LinearMeasurementDefinition.Type.RATIO_PERCENT ? "%" : "mm";
            csv.append("LINEAR,")
                    .append(csvEscape(studyId)).append(',')
                    .append(csvEscape(studyName)).append(',')
                    .append(csvEscape(patientName)).append(',')
                    .append(csvEscape(patientAge)).append(',')
                    .append(csvEscape(patientSex)).append(',')
                    .append(csvEscape(selectedAnalyses)).append(',')
                    .append(csvEscape(def.name)).append(',')
                    .append(String.format(Locale.US, "%.4f", value)).append(',')
                    .append(csvEscape(unit)).append(',')
                    .append(csvEscape(linearNormText(def, value))).append(',')
                    .append(csvEscape(linearDiagnosis(def, value))).append(",,,")
                    .append(csvEscape(cal)).append('\n');
        }

        List<PointF> pts = measurementView.getPointsSnapshot();
        List<String> labels = measurementView.getLandmarkLabels();
        for (int i = 0; i < pts.size() && i < labels.size(); i++) {
            PointF p = pts.get(i);
            if (p == null) continue;
            csv.append("LANDMARK,")
                    .append(csvEscape(studyId)).append(',')
                    .append(csvEscape(studyName)).append(',')
                    .append(csvEscape(patientName)).append(',')
                    .append(csvEscape(patientAge)).append(',')
                    .append(csvEscape(patientSex)).append(',')
                    .append(csvEscape(selectedAnalyses)).append(',')
                    .append(csvEscape(labels.get(i))).append(",,,,")
                    .append(',')
                    .append(String.format(Locale.US, "%.3f", p.x)).append(',')
                    .append(String.format(Locale.US, "%.3f", p.y)).append(',')
                    .append(csvEscape(cal)).append('\n');
        }
        return csv.toString();
    }

    private void startSaveCsv() {
        pendingCsvText = buildResearchCsv();
        Intent intent = new Intent(Intent.ACTION_CREATE_DOCUMENT);
        intent.addCategory(Intent.CATEGORY_OPENABLE);
        intent.setType("text/csv");
        intent.putExtra(Intent.EXTRA_TITLE, safeFileName(studyName + "_datos_yomceph.csv"));
        startActivityForResult(intent, REQ_SAVE_CSV);
    }

    private void writePendingCsv(Uri uri) {
        if (pendingCsvText == null || uri == null) return;
        try (OutputStream out = getContentResolver().openOutputStream(uri)) {
            if (out == null) throw new IOException("No se pudo abrir el archivo CSV.");
            out.write(pendingCsvText.getBytes(java.nio.charset.StandardCharsets.UTF_8));
            out.flush();
            Toast.makeText(this, "Datos de investigación exportados en CSV.", Toast.LENGTH_LONG).show();
        } catch (Exception e) {
            Toast.makeText(this, "No se pudo guardar el CSV.", Toast.LENGTH_LONG).show();
        } finally {
            pendingCsvText = null;
        }
    }

'''
    if quality_anchor not in a:
        raise RuntimeError('calculateFullAnalysis anchor not found')
    a = a.replace(quality_anchor, helpers + quality_anchor, 1)

# Add QC card in result dialog after the evidence notice.
qc_anchor = '        container.addView(evidenceNotice);\n'
if 'traceQualityText()' in a and 'Control de calidad del trazado' in a and 'qcNotice.setText(traceQualityText())' not in a:
    qc_block = r'''        TextView qcNotice = new TextView(this);
        qcNotice.setText(traceQualityText());
        qcNotice.setTextSize(12.5f);
        qcNotice.setTextColor(getColor(R.color.text_primary));
        qcNotice.setGravity(Gravity.CENTER);
        qcNotice.setTextAlignment(View.TEXT_ALIGNMENT_CENTER);
        qcNotice.setIncludeFontPadding(false);
        qcNotice.setLineSpacing(0f, 1.06f);
        qcNotice.setBackgroundResource(R.drawable.button_soft_purple_centered);
        qcNotice.setPadding(dp(12), dp(10), dp(12), dp(10));
        LinearLayout.LayoutParams qcLp = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT
        );
        qcLp.setMargins(0, 0, 0, dp(12));
        qcNotice.setLayoutParams(qcLp);
        container.addView(qcNotice);

'''
    if qc_anchor not in a:
        raise RuntimeError('evidence notice anchor not found')
    a = a.replace(qc_anchor, qc_anchor + '\n' + qc_block, 1)

# Export CSV button after PDF button.
if 'startSaveCsv();' not in a:
    pdf_button_anchor = '        container.addView(savePdf);\n'
    csv_button = r'''
        TextView saveCsv = createDialogButton(
                "EXPORTAR DATOS CSV · INVESTIGACIÓN",
                R.drawable.button_soft_mint,
                getColor(R.color.mint_text)
        );
        saveCsv.setOnClickListener(v -> startSaveCsv());
        container.addView(saveCsv);
'''
    if pdf_button_anchor not in a:
        raise RuntimeError('PDF button anchor not found')
    a = a.replace(pdf_button_anchor, pdf_button_anchor + csv_button, 1)

# Handle CSV save result before image/open-image branches.
activity_result_anchor = '        if (requestCode == REQ_SAVE_PDF) {\n'
if 'if (requestCode == REQ_SAVE_CSV)' not in a:
    csv_result = r'''        if (requestCode == REQ_SAVE_CSV) {
            if (resultCode == RESULT_OK
                    && data != null
                    && data.getData() != null) {
                writePendingCsv(data.getData());
            } else {
                pendingCsvText = null;
            }
            return;
        }

'''
    if activity_result_anchor not in a:
        raise RuntimeError('onActivityResult save anchor not found')
    a = a.replace(activity_result_anchor, csv_result + activity_result_anchor, 1)

activity.write_text(a, encoding='utf-8')

# -----------------------------------------------------------------------------
# Labels: make the single launcher clearly describe the new workflow.
# -----------------------------------------------------------------------------
for strings in [ROOT / 'app/src/main/res/values/strings.xml', ROOT / 'app/src/main/res/values-en/strings.xml']:
    s = strings.read_text(encoding='utf-8')
    if 'values-en' in str(strings):
        s = re.sub(r'<string name="analysis_steiner">.*?</string>',
                   '<string name="analysis_steiner">CHOOSE CEPHALOMETRIC ANALYSES</string>', s, count=1, flags=re.S)
    else:
        s = re.sub(r'<string name="analysis_steiner">.*?</string>',
                   '<string name="analysis_steiner">ELEGIR ANÁLISIS CEFALOMÉTRICOS</string>', s, count=1, flags=re.S)
    strings.write_text(s, encoding='utf-8')

# -----------------------------------------------------------------------------
# Unit tests for the selector contract.
# -----------------------------------------------------------------------------
test = TEST / 'AnalysisProfileTest.java'
test.write_text(r'''package com.cefalo.angulos;

import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;
import static org.junit.Assert.assertEquals;

import org.junit.Test;

public class AnalysisProfileTest {
    @Test public void allProfileIncludesEveryModule() {
        assertTrue(AnalysisProfile.includes(AnalysisProfile.ALL, AnalysisProfile.STEINER));
        assertTrue(AnalysisProfile.includes(AnalysisProfile.ALL, AnalysisProfile.SASSOUNI));
        assertTrue(AnalysisProfile.includes(AnalysisProfile.ALL, AnalysisProfile.BURSTONE));
    }

    @Test public void normalizeRejectsUnknownIdsAndPreservesKnownOrder() {
        String value = AnalysisProfile.normalize("MCNAMARA,NO_EXISTE,WITS");
        assertEquals("MCNAMARA,WITS", value);
        assertTrue(AnalysisProfile.includes(value, AnalysisProfile.MCNAMARA));
        assertTrue(AnalysisProfile.includes(value, AnalysisProfile.WITS));
        assertFalse(AnalysisProfile.includes(value, AnalysisProfile.STEINER));
    }

    @Test public void filteringSeparatesAuthorGroups() {
        java.util.List<MeasurementDefinition> defs = new java.util.ArrayList<>();
        defs.add(new MeasurementDefinition("SNA", MeasurementDefinition.Type.THREE_POINTS,
                new String[]{"S","N","A"},0,0,"","","","","",false));
        defs.add(new MeasurementDefinition("Ricketts · prueba", MeasurementDefinition.Type.THREE_POINTS,
                new String[]{"S","N","A"},0,0,"","","","","",false));
        java.util.List<MeasurementDefinition> filtered =
                AnalysisProfile.filterAngular(defs, AnalysisProfile.RICKETTS);
        assertEquals(1, filtered.size());
        assertTrue(filtered.get(0).name.startsWith("Ricketts"));
    }
}
''', encoding='utf-8')

# Guardrails.
checks = {
    'version 1.37': "versionName '1.37'" in gradle.read_text(encoding='utf-8'),
    'profile class': profile.exists(),
    'selector launcher': 'showAnalysisSelector()' in main.read_text(encoding='utf-8'),
    'profile filtering': 'AnalysisProfile.filterAngular' in activity.read_text(encoding='utf-8'),
    'qc': 'qcNotice.setText(traceQualityText())' in activity.read_text(encoding='utf-8'),
    'csv export': 'EXPORTAR DATOS CSV · INVESTIGACIÓN' in activity.read_text(encoding='utf-8'),
    'selection persisted': 'yomceph_analysis_profiles' in activity.read_text(encoding='utf-8'),
}
missing = [name for name, ok in checks.items() if not ok]
if missing:
    raise RuntimeError('Priority upgrades incomplete: ' + ', '.join(missing))

print('v1.37 priorities applied: selective tracing, geometric QC, and research CSV export.')