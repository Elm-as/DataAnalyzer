from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from datetime import datetime
import io
import json

class PDFReportGenerator:
    def __init__(self):
        self.width, self.height = A4
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configuration des styles personnalisés en noir et blanc"""
        # Titre principal (14pt)
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=14,
            textColor=colors.black,
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Titre de section (13pt)
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=13,
            textColor=colors.black,
            spaceAfter=8,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Sous-titre (13pt)
        self.styles.add(ParagraphStyle(
            name='CustomSubheading',
            parent=self.styles['Heading3'],
            fontSize=13,
            textColor=colors.black,
            spaceAfter=6,
            spaceBefore=8,
            fontName='Helvetica-Bold'
        ))
        
        # Corps de texte (13pt)
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=13,
            textColor=colors.black,
            spaceAfter=6,
            alignment=TA_JUSTIFY,
            fontName='Helvetica'
        ))
        
        # Corps petit (11pt pour les tableaux)
        self.styles.add(ParagraphStyle(
            name='SmallBody',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.black,
            fontName='Helvetica'
        ))
    
    def generate(self, analysis_results, config=None):
        """
        Génère un rapport PDF complet
        Format: A4, police 13-14, noir et blanc
        """
        buffer = io.BytesIO()
        
        # Créer le document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Contenu du document
        story = []
        
        # Page de garde
        story.extend(self._create_cover_page(analysis_results))
        story.append(PageBreak())
        
        # Table des matières
        story.extend(self._create_toc(analysis_results))
        story.append(PageBreak())
        
        # Résumé exécutif
        story.extend(self._create_executive_summary(analysis_results))
        story.append(PageBreak())
        
        # Vue d'ensemble / Résumé des données
        story.extend(self._create_overview_section(analysis_results))
        story.append(PageBreak())
        
        # Sections d'analyse (nouvelle logique structurée)
        analyses = analysis_results.get('analyses', {}) if isinstance(analysis_results, dict) else {}

        # 1. Statistiques Descriptives
        if analyses.get('descriptiveStats'):
            story.extend(self._create_descriptive_stats_section(analyses.get('descriptiveStats')))
            story.append(PageBreak())

        # 2. Corrélations
        if analyses.get('correlations'):
            story.extend(self._create_correlations_section(analyses.get('correlations')))
            story.append(PageBreak())

        # 3. Distributions
        if analyses.get('distributions'):
            story.extend(self._create_distributions_section(analyses.get('distributions')))
            story.append(PageBreak())

        # 4. Anomalies/Outliers
        if analyses.get('outliers'):
            story.extend(self._create_outliers_section(analyses.get('outliers')))
            story.append(PageBreak())

        # 5. Catégorielles
        if analyses.get('categorical'):
            story.extend(self._create_categorical_section(analyses.get('categorical')))
            story.append(PageBreak())

        # 6. Correspondance Donnees (Associations)
        if analyses.get('associations') or analyses.get('symptomMatching'):
            story.extend(self._create_associations_section(
                analyses.get('associations') or analyses.get('symptomMatching')
            ))
            story.append(PageBreak())

        # Advanced Analysis Sections (existing logic)
        section_order = [
            'regression', 'classification', 'discriminant', 'neuralNetworks', 'timeSeries', 'advancedClustering', 'clustering', 'advancedStats'
        ]

        for key in section_order:
            data = analyses.get(key)
            if not data:
                continue
            if key == 'regression':
                story.extend(self._create_regression_section(data))
                story.append(PageBreak())
            elif key == 'classification':
                story.extend(self._create_classification_section(data))
                story.append(PageBreak())
            elif key == 'discriminant':
                story.extend(self._create_discriminant_section(data))
                story.append(PageBreak())
            elif key == 'neuralNetworks':
                story.extend(self._create_neural_networks_section(data))
                story.append(PageBreak())
            elif key == 'timeSeries':
                story.extend(self._create_time_series_section(data))
                story.append(PageBreak())
            elif key in ('advancedClustering','clustering'):
                story.extend(self._create_clustering_section(data))
                story.append(PageBreak())
            elif key == 'advancedStats':
                story.extend(self._create_stats_section(data))
        
        # Construire le PDF
        doc.build(story)
        
        buffer.seek(0)
        return buffer
    
    def _create_cover_page(self, results):
        """Page de garde"""
        story = []
        
        # Espacement
        story.append(Spacer(1, 3*cm))
        
        # Titre
        story.append(Paragraph("RAPPORT D'ANALYSE DE DONNÉES", self.styles['CustomTitle']))
        story.append(Spacer(1, 1*cm))
        
        # Date
        date_str = datetime.now().strftime("%d/%m/%Y à %H:%M")
        story.append(Paragraph(f"Généré le {date_str}", self.styles['CustomBody']))
        story.append(Spacer(1, 2*cm))
        
        # Informations générales
        info_data = [
            ["Nombre total de lignes:", str(results.get('summary', {}).get('totalRows', 'N/A'))],
            ["Colonnes analysées:", str(results.get('summary', {}).get('selectedColumns', 'N/A'))],
            ["Analyses effectuées:", str(len(results.get('analyses', {})))],
        ]
        
        info_table = Table(info_data, colWidths=[8*cm, 6*cm])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 13),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        
        story.append(info_table)
        
        return story
    
    def _create_toc(self, results):
        """Table des matieres"""
        story = []
        
        story.append(Paragraph("TABLE DES MATIERES", self.styles['CustomTitle']))
        story.append(Spacer(1, 1*cm))
        
        toc_items = [
            "1. Resume executif",
            "2. Vue d'ensemble",
            "3. Statistiques descriptives",
            "4. Correlations",
            "5. Distributions",
            "6. Anomalies detectees",
            "7. Variables categoriques",
            "8. Correspondance des donnees",
        ]
        
        analyses = results.get('analyses', {}) if isinstance(results, dict) else {}
        section_num = 9
        
        toc_map = {
            'regression': 'Analyse de regression',
            'classification': 'Classification',
            'discriminant': 'Analyse discriminante',
            'neuralNetworks': 'Reseaux de neurones',
            'timeSeries': 'Series temporelles',
            'advancedClustering': 'Clustering avance',
            'clustering': 'Clustering',
            'advancedStats': 'Tests statistiques',
        }
        
        for k in ['regression','classification','discriminant','neuralNetworks','timeSeries','advancedClustering','clustering','advancedStats']:
            if analyses.get(k):
                toc_items.append(f"{section_num}. {toc_map[k]}")
                section_num += 1
        
        for item in toc_items:
            story.append(Paragraph(item, self.styles['CustomBody']))
            story.append(Spacer(1, 0.3*cm))
        
        return story
    
    def _create_executive_summary(self, results):
        """Resume executif"""
        story = []
        
        story.append(Paragraph("1. RESUME EXECUTIF", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.5*cm))
        
        summary_text = f"""
        Ce rapport presente les resultats des analyses statistiques et d'apprentissage automatique 
        effectuees sur les donnees fournies. Les analyses ont ete realisees le {datetime.now().strftime("%d/%m/%Y")}
        et couvrent plusieurs methodes d'analyse avancees.
        """
        
        story.append(Paragraph(summary_text, self.styles['CustomBody']))
        story.append(Spacer(1, 0.5*cm))
        
        # Points clés
        story.append(Paragraph("Points cles:", self.styles['CustomSubheading']))
        
        key_points = []
        analyses = results.get('analyses', {}) if isinstance(results, dict) else {}
        if analyses.get('regression'):
            best = analyses['regression'].get('best_model')
            key_points.append(f"• Regression: meilleur modele = {best or 'N/A'}")
        if analyses.get('classification'):
            best = analyses['classification'].get('best_model')
            key_points.append(f"• Classification: meilleur modele = {best or 'N/A'}")
        if analyses.get('timeSeries'):
            mets = analyses['timeSeries'].get('metrics', {})
            mape = mets.get('mape')
            key_points.append(f"• Series temporelles: MAPE = {mape:.2f}" if isinstance(mape, (int,float)) else "• Series temporelles: metriques disponibles")
        if analyses.get('advancedClustering'):
            best = analyses['advancedClustering'].get('best_model')
            key_points.append(f"• Clustering avance: meilleur modele = {best or 'N/A'}")
        
        for point in key_points:
            story.append(Paragraph(point, self.styles['CustomBody']))
        story.append(Spacer(1, 0.5*cm))

        # Synthèse tabulaire: meilleurs modèles
        summary = results.get('summary', {}) if isinstance(results, dict) else {}
        best_models = summary.get('bestModels', {})
        if isinstance(best_models, dict) and len(best_models) > 0:
            story.append(Paragraph("Meilleurs modèles par domaine:", self.styles['CustomSubheading']))
            rows = [["Domaine", "Modèle"]]
            # Ordre agréable d'affichage
            order = [
                ('regression','Régression'),
                ('classification','Classification'),
                ('discriminant','Analyse Discriminante'),
                ('neuralNetworks','Réseaux de Neurones'),
                ('clustering','Clustering'),
            ]
            for key, label in order:
                val = best_models.get(key)
                if val:
                    rows.append([label, str(val)])
            # Ajouter les éventuels autres domaines non listés
            for k, v in best_models.items():
                if k not in dict(order) and v:
                    rows.append([str(k), str(v)])
            if len(rows) > 1:
                table = Table(rows, colWidths=[7*cm, 7*cm])
                table.setStyle(self._get_table_style())
                story.append(table)
                story.append(Spacer(1, 0.5*cm))

        # Synthèse tabulaire: performances clés
        performance = summary.get('performance', [])
        if isinstance(performance, list) and len(performance) > 0:
            story.append(Paragraph("Indicateurs de performance clés:", self.styles['CustomSubheading']))
            rows = [["Domaine", "Métrique", "Valeur"]]
            # Limiter à 8 lignes pour lisibilité
            for item in performance[:8]:
                domain = str(item.get('domain', ''))
                metric = str(item.get('metric', ''))
                val = item.get('value', 'N/A')
                if isinstance(val, (int, float)):
                    # Adapter format si métrique en pourcentage
                    if metric.lower() in ('accuracy','mape'):
                        val_fmt = f"{val*100:.2f}%" if metric.lower() == 'accuracy' and val <= 1 else f"{val:.2f}%"
                    else:
                        val_fmt = f"{val:.4f}"
                else:
                    val_fmt = str(val)
                rows.append([domain, metric, val_fmt])
            table = Table(rows, colWidths=[6*cm, 4*cm, 4*cm])
            table.setStyle(self._get_table_style())
            story.append(table)
        
        return story
    
    def _create_regression_section(self, regression_data):
        """Section régression"""
        story = []
        
        story.append(Paragraph("2. ANALYSE DE RÉGRESSION", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.5*cm))
        
        if 'models' in regression_data:
            # Tableau comparatif global
            comp_rows = [["Modèle","R²","RMSE","MAE"]]
            for model_name, model_data in regression_data['models'].items():
                r2 = model_data.get('r2_score') or model_data.get('test_metrics', {}).get('r2')
                rmse = model_data.get('rmse') or model_data.get('test_metrics', {}).get('rmse')
                mae = model_data.get('mae') or model_data.get('test_metrics', {}).get('mae')
                comp_rows.append([
                    model_name,
                    f"{r2:.4f}" if isinstance(r2,(int,float)) else 'N/A',
                    f"{rmse:.4f}" if isinstance(rmse,(int,float)) else 'N/A',
                    f"{mae:.4f}" if isinstance(mae,(int,float)) else 'N/A'
                ])
            table = Table(comp_rows, colWidths=[6*cm,3*cm,3*cm,3*cm])
            table.setStyle(self._get_table_style())
            story.append(table)
            story.append(Spacer(1,0.5*cm))
            best = regression_data.get('best_model')
            if best:
                story.append(Paragraph(f"Meilleur modèle sélectionné: <b>{best}</b>", self.styles['CustomBody']))
                story.append(Spacer(1,0.3*cm))
        
        return story
    
    def _create_classification_section(self, classification_data):
        """Section classification"""
        story = []
        
        story.append(Paragraph("CLASSIFICATION", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.5*cm))
        
        if 'models' in classification_data:
            comp_rows = [["Modèle","Accuracy","Precision","Recall","F1"]]
            for model_name, model_data in classification_data['models'].items():
                acc = model_data.get('accuracy') or model_data.get('test_metrics', {}).get('accuracy')
                prec = model_data.get('precision') or model_data.get('test_metrics', {}).get('precision')
                rec = model_data.get('recall') or model_data.get('test_metrics', {}).get('recall')
                f1 = model_data.get('f1_score') or model_data.get('test_metrics', {}).get('f1') or model_data.get('test_metrics', {}).get('f1_score')
                comp_rows.append([
                    model_name,
                    f"{acc:.4f}" if isinstance(acc,(int,float)) else 'N/A',
                    f"{prec:.4f}" if isinstance(prec,(int,float)) else 'N/A',
                    f"{rec:.4f}" if isinstance(rec,(int,float)) else 'N/A',
                    f"{f1:.4f}" if isinstance(f1,(int,float)) else 'N/A'
                ])
            table = Table(comp_rows, colWidths=[5*cm,2.5*cm,2.5*cm,2.5*cm,2.5*cm])
            table.setStyle(self._get_table_style())
            story.append(table)
            story.append(Spacer(1,0.5*cm))
            best = classification_data.get('best_model')
            if best:
                story.append(Paragraph(f"Meilleur modèle sélectionné: <b>{best}</b>", self.styles['CustomBody']))
                story.append(Spacer(1,0.3*cm))
        
        return story
    
    def _create_discriminant_section(self, discriminant_data):
        """Section analyse discriminante"""
        story = []
        story.append(Paragraph("ANALYSE DISCRIMINANTE", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.5*cm))
        story.append(Paragraph("Analyse discriminante linéaire (LDA) et quadratique (QDA) effectuée.", self.styles['CustomBody']))
        return story
    
    def _create_neural_networks_section(self, nn_data):
        """Section réseaux de neurones"""
        story = []
        story.append(Paragraph("RÉSEAUX DE NEURONES", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.5*cm))
        story.append(Paragraph("Modèles de réseaux de neurones profonds entraînés et évalués.", self.styles['CustomBody']))
        return story
    
    def _create_time_series_section(self, ts_data):
        """Section séries temporelles"""
        story = []
        story.append(Paragraph("ANALYSE DE SÉRIES TEMPORELLES", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.5*cm))
        mets = ts_data.get('metrics', {})
        forecast_info = ts_data.get('forecast', {})
        story.append(Paragraph("Prévisions temporelles réalisées.", self.styles['CustomBody']))
        # Metrics table
        if mets:
            rows = [["Métrique","Valeur"]]
            for k in ['rmse','mape']:
                v = mets.get(k)
                if isinstance(v,(int,float)):
                    rows.append([k.upper(), f"{v:.4f}"])
            table = Table(rows, colWidths=[8*cm,6*cm])
            table.setStyle(self._get_table_style())
            story.append(table)
            story.append(Spacer(1,0.3*cm))
        # Forecast sample
        if forecast_info.get('values'):
            vals = forecast_info['values'][:10]
            rows = [["Index","Prévision"]]
            for i,v in enumerate(vals):
                rows.append([str(i), f"{v:.2f}" if isinstance(v,(int,float)) else str(v)])
            table = Table(rows, colWidths=[4*cm,10*cm])
            table.setStyle(self._get_table_style())
            story.append(Paragraph("Extrait des prévisions (10 premières valeurs):", self.styles['CustomBody']))
            story.append(table)
        return story
    
    def _create_clustering_section(self, clustering_data):
        """Section clustering"""
        story = []
        story.append(Paragraph("CLUSTERING", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.5*cm))
        story.append(Paragraph("Segmentation des données effectuée.", self.styles['CustomBody']))
        if clustering_data.get('models'):
            rows = [["Modèle","Silhouette","Davies-Bouldin"]]
            for name, m in clustering_data['models'].items():
                sil = m.get('silhouette_score') or m.get('metrics',{}).get('silhouette_score')
                db = m.get('davies_bouldin_score') or m.get('metrics',{}).get('davies_bouldin_score')
                rows.append([
                    name,
                    f"{sil:.4f}" if isinstance(sil,(int,float)) else 'N/A',
                    f"{db:.4f}" if isinstance(db,(int,float)) else 'N/A'
                ])
            table = Table(rows, colWidths=[6*cm,5*cm,5*cm])
            table.setStyle(self._get_table_style())
            story.append(table)
            story.append(Spacer(1,0.3*cm))
            best = clustering_data.get('best_model')
            if best:
                story.append(Paragraph(f"Meilleur modèle: <b>{best}</b>", self.styles['CustomBody']))
        return story
    
    def _create_stats_section(self, stats_data):
        """Section tests statistiques (détaillée avec p-values et interprétations)"""
        story = []
        story.append(Paragraph("TESTS STATISTIQUES AVANCÉS", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.5*cm))

        tests = stats_data.get('tests', {}) if isinstance(stats_data, dict) else {}
        summary = stats_data.get('summary', {}) if isinstance(stats_data, dict) else {}

        # Résumé global des tests
        if summary:
            rows = [["Indicateur", "Valeur"]]
            rows.append(["Nombre de familles de tests", str(summary.get('total_tests', 'N/A'))])
            rows.append(["Résultats significatifs (familles ou sous-tests)", str(summary.get('significant_results', 'N/A'))])
            rows.append(["Seuil α", str(summary.get('alpha_level', 'N/A'))])
            if summary.get('tests_performed'):
                rows.append(["Tests effectués", ", ".join(map(str, summary['tests_performed']))])
            table = Table(rows, colWidths=[9*cm, 5*cm])
            table.setStyle(self._get_table_style())
            story.append(table)
            story.append(Spacer(1, 0.5*cm))

        # Normalité
        norm = tests.get('normality')
        if norm and isinstance(norm, dict) and norm.get('results'):
            story.append(Paragraph("Tests de normalité (Shapiro, D'Agostino)", self.styles['CustomSubheading']))
            rows = [["Variable", "n", "Shapiro p", "D'Agostino p", "Skew", "Kurtosis"]]
            for r in norm['results'][:12]:
                sh_p = r.get('shapiro_wilk', {}).get('p_value') if r.get('shapiro_wilk') else None
                da_p = r.get('dagostino', {}).get('p_value') if r.get('dagostino') else None
                rows.append([
                    r.get('column',''),
                    str(r.get('n_samples','')),
                    f"{sh_p:.4f}" if isinstance(sh_p,(int,float)) else 'N/A',
                    f"{da_p:.4f}" if isinstance(da_p,(int,float)) else 'N/A',
                    f"{r.get('skewness',0):.3f}" if isinstance(r.get('skewness'),(int,float)) else 'N/A',
                    f"{r.get('kurtosis',0):.3f}" if isinstance(r.get('kurtosis'),(int,float)) else 'N/A',
                ])
            table = Table(rows, colWidths=[5*cm,1.5*cm,2.2*cm,2.8*cm,2*cm,2*cm])
            table.setStyle(self._get_table_style())
            story.append(table)
            story.append(Spacer(1,0.4*cm))

        # T-test
        tt = tests.get('ttest')
        if tt and isinstance(tt, dict) and not tt.get('error'):
            story.append(Paragraph("T-test", self.styles['CustomSubheading']))
            rows = [["Groupe", "n", "Moyenne", "Écart-type"]]
            g1 = tt.get('groups',{}).get('group1',{})
            g2 = tt.get('groups',{}).get('group2',{})
            rows.append([g1.get('name','G1'), str(g1.get('n','')), f"{g1.get('mean',0):.3f}" if isinstance(g1.get('mean'),(int,float)) else 'N/A', f"{g1.get('std',0):.3f}" if isinstance(g1.get('std'),(int,float)) else 'N/A'])
            rows.append([g2.get('name','G2'), str(g2.get('n','')), f"{g2.get('mean',0):.3f}" if isinstance(g2.get('mean'),(int,float)) else 'N/A', f"{g2.get('std',0):.3f}" if isinstance(g2.get('std'),(int,float)) else 'N/A'])
            table = Table(rows, colWidths=[6*cm,2*cm,3*cm,3*cm])
            table.setStyle(self._get_table_style())
            story.append(table)
            story.append(Spacer(1,0.2*cm))
            info = [["Statistique", f"{tt.get('statistic',0):.4f}" if isinstance(tt.get('statistic'),(int,float)) else 'N/A'],
                    ["p-value", f"{tt.get('p_value',0):.4f}" if isinstance(tt.get('p_value'),(int,float)) else 'N/A'],
                    ["Cohen's d", f"{tt.get('cohens_d',0):.3f}" if isinstance(tt.get('cohens_d'),(int,float)) else 'N/A'],
                    ["Taille d'effet", str(tt.get('effect_size',''))]]
            t2 = Table(info, colWidths=[6*cm,8*cm])
            t2.setStyle(self._get_table_style())
            story.append(t2)
            story.append(Spacer(1,0.4*cm))

        # ANOVA
        an = tests.get('anova')
        if an and isinstance(an, dict) and an.get('group_stats'):
            story.append(Paragraph("ANOVA (One-way)", self.styles['CustomSubheading']))
            rows = [["Groupe","n","Moyenne","Écart-type","Min","Max"]]
            for gs in an['group_stats']:
                rows.append([gs.get('group',''), str(gs.get('n','')), f"{gs.get('mean',0):.3f}", f"{gs.get('std',0):.3f}", f"{gs.get('min',0):.3f}", f"{gs.get('max',0):.3f}"])
            table = Table(rows, colWidths=[5*cm,1.5*cm,2.2*cm,2.2*cm,2*cm,2*cm])
            table.setStyle(self._get_table_style())
            story.append(table)
            story.append(Spacer(1,0.2*cm))
            info = [["F-statistic", f"{an.get('f_statistic',0):.4f}"], ["p-value", f"{an.get('p_value',0):.4f}"], ["Significatif", 'Oui' if an.get('significant') else 'Non']]
            t2 = Table(info, colWidths=[6*cm,8*cm])
            t2.setStyle(self._get_table_style())
            story.append(t2)
            story.append(Spacer(1,0.4*cm))

        # Kruskal-Wallis
        kw = tests.get('kruskal')
        if kw and isinstance(kw, dict) and kw.get('group_stats'):
            story.append(Paragraph("Kruskal-Wallis", self.styles['CustomSubheading']))
            rows = [["Groupe","n","Médiane","Moyenne","Écart-type"]]
            for gs in kw['group_stats']:
                rows.append([gs.get('group',''), str(gs.get('n','')), f"{gs.get('median',0):.3f}", f"{gs.get('mean',0):.3f}", f"{gs.get('std',0):.3f}"])
            table = Table(rows, colWidths=[5*cm,1.5*cm,2.2*cm,2.2*cm,2*cm])
            table.setStyle(self._get_table_style())
            story.append(table)
            story.append(Spacer(1,0.2*cm))
            info = [["H-statistic", f"{kw.get('h_statistic',0):.4f}"], ["p-value", f"{kw.get('p_value',0):.4f}"], ["Significatif", 'Oui' if kw.get('significant') else 'Non']]
            t2 = Table(info, colWidths=[6*cm,8*cm])
            t2.setStyle(self._get_table_style())
            story.append(t2)
            story.append(Spacer(1,0.4*cm))

        # Chi-carré d'indépendance
        chi = tests.get('chi_square')
        if chi and isinstance(chi, dict) and not chi.get('error'):
            story.append(Paragraph("Chi-carré d'indépendance", self.styles['CustomSubheading']))
            info = [["χ² statistic", f"{chi.get('chi2_statistic',0):.4f}"], ["ddl", str(chi.get('degrees_of_freedom',''))], ["p-value", f"{chi.get('p_value',0):.4f}"], ["Cramér's V", f"{chi.get('cramers_v',0):.3f}"], ["Force de l'association", str(chi.get('association_strength',''))], ["Significatif", 'Oui' if chi.get('significant') else 'Non']]
            t2 = Table(info, colWidths=[7*cm,7*cm])
            t2.setStyle(self._get_table_style())
            story.append(t2)
            story.append(Spacer(1,0.3*cm))
            # Petit extrait de la table de contingence
            ct = chi.get('contingency_table', {})
            if isinstance(ct, dict) and len(ct) > 0:
                rows = []
                # En-tête avec premières colonnes
                first_row = next(iter(ct.values()))
                cols = list(first_row.keys())[:5]
                # Eviter l'erreur de f-string due aux crochets non échappés en pré-calculant les variables
                variables = chi.get('variables', ['Var1', 'Var2'])
                var_label = f"{variables[0]}\\{variables[1]}"
                rows.append([var_label] + cols)
                for rname, rvals in list(ct.items())[:5]:
                    rows.append([str(rname)] + [str(rvals.get(c,0)) for c in cols])
                table = Table(rows)
                table.setStyle(self._get_table_style())
                story.append(table)
                story.append(Spacer(1,0.3*cm))

        # Levene
        lev = tests.get('levene')
        if lev and isinstance(lev, dict) and not lev.get('error'):
            story.append(Paragraph("Test de Levene (homogénéité des variances)", self.styles['CustomSubheading']))
            info = [["Statistique", f"{lev.get('statistic',0):.4f}"], ["p-value", f"{lev.get('p_value',0):.4f}"], ["Variances homogènes", 'Oui' if lev.get('homogeneous_variances') else 'Non']]
            t2 = Table(info, colWidths=[7*cm,7*cm])
            t2.setStyle(self._get_table_style())
            story.append(t2)
            story.append(Spacer(1,0.3*cm))

        # Mann-Whitney U
        mw = tests.get('mann_whitney')
        if mw and isinstance(mw, dict) and not mw.get('error'):
            story.append(Paragraph("Mann-Whitney U", self.styles['CustomSubheading']))
            rows = [["Groupe","n","Médiane"]]
            g1 = mw.get('groups',{}).get('group1',{})
            g2 = mw.get('groups',{}).get('group2',{})
            rows.append([g1.get('name','G1'), str(g1.get('n','')), f"{g1.get('median',0):.3f}"])
            rows.append([g2.get('name','G2'), str(g2.get('n','')), f"{g2.get('median',0):.3f}"])
            table = Table(rows, colWidths=[6*cm,3*cm,5*cm])
            table.setStyle(self._get_table_style())
            story.append(table)
            story.append(Spacer(1,0.2*cm))
            info = [["U-statistic", f"{mw.get('u_statistic',0):.4f}"], ["p-value", f"{mw.get('p_value',0):.4f}"], ["Significatif", 'Oui' if mw.get('significant') else 'Non']]
            t2 = Table(info, colWidths=[6*cm,8*cm])
            t2.setStyle(self._get_table_style())
            story.append(t2)

        return story
    
    def _create_cleaning_section(self, cleaning_data):
        """Section nettoyage de données"""
        story = []
        story.append(Paragraph("NETTOYAGE DES DONNEES", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.5*cm))
        story.append(Paragraph("Operations de nettoyage et de pretraitement effectuees.", self.styles['CustomBody']))
        return story

    def _create_overview_section(self, results):
        """Section Vue d'ensemble"""
        story = []
        story.append(Paragraph("VUE D'ENSEMBLE", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.5*cm))
        
        summary = results.get('summary', {})
        
        # Informations sur le dataset
        overview_data = [
            ["Nombre de lignes", str(summary.get('totalRows', 'N/A'))],
            ["Nombre de colonnes", str(summary.get('totalColumns', 'N/A'))],
            ["Colonnes selectionnees", str(summary.get('selectedColumns', 'N/A'))],
            ["Valeurs manquantes (total)", str(summary.get('totalMissing', 'N/A'))],
            ["Valeurs manquantes (%)", f"{summary.get('missingPercentage', 0):.1f}%"],
        ]
        
        table = Table(overview_data, colWidths=[8*cm, 6*cm])
        table.setStyle(self._get_table_style())
        story.append(table)
        
        return story

    def _create_descriptive_stats_section(self, stats_data):
        """Section Statistiques Descriptives"""
        story = []
        story.append(Paragraph("STATISTIQUES DESCRIPTIVES", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.5*cm))
        
        if isinstance(stats_data, dict) and 'columns' in stats_data:
            for col_name, col_stats in stats_data.get('columns', {}).items():
                story.append(Paragraph(f"Variable: {col_name}", self.styles['CustomSubheading']))
                
                stats_table_data = [
                    ["Moyenne", f"{col_stats.get('mean', 'N/A')}"],
                    ["Mediane", f"{col_stats.get('median', 'N/A')}"],
                    ["Ecart-type", f"{col_stats.get('std', 'N/A')}"],
                    ["Min", f"{col_stats.get('min', 'N/A')}"],
                    ["Max", f"{col_stats.get('max', 'N/A')}"],
                ]
                
                table = Table(stats_table_data, colWidths=[6*cm, 8*cm])
                table.setStyle(self._get_table_style())
                story.append(table)
                story.append(Spacer(1, 0.3*cm))
        
        return story

    def _create_correlations_section(self, corr_data):
        """Section Correlations"""
        story = []
        story.append(Paragraph("CORRELATIONS", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.5*cm))
        
        if isinstance(corr_data, dict) and 'pairs' in corr_data:
            table_data = [["Variable 1", "Variable 2", "Correlation"]]
            
            for pair in corr_data.get('pairs', [])[:15]:  # Limiter a 15 pairs
                table_data.append([
                    pair.get('var1', 'N/A'),
                    pair.get('var2', 'N/A'),
                    f"{pair.get('correlation', 0):.3f}"
                ])
            
            table = Table(table_data, colWidths=[5*cm, 5*cm, 4*cm])
            table.setStyle(self._get_table_style())
            story.append(table)
        
        return story

    def _create_distributions_section(self, dist_data):
        """Section Distributions"""
        story = []
        story.append(Paragraph("DISTRIBUTIONS", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.5*cm))
        
        story.append(Paragraph(
            "Analyse des distributions des variables du dataset.",
            self.styles['CustomBody']
        ))
        
        if isinstance(dist_data, dict):
            for key, value in list(dist_data.items())[:5]:
                story.append(Paragraph(f"Variable: {key}", self.styles['CustomSubheading']))
                story.append(Spacer(1, 0.2*cm))
        
        return story

    def _create_outliers_section(self, outliers_data):
        """Section Anomalies/Outliers"""
        story = []
        story.append(Paragraph("ANOMALIES DETECTEES", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.5*cm))
        
        if isinstance(outliers_data, dict):
            total_outliers = outliers_data.get('totalOutliers', 0)
            story.append(Paragraph(f"Nombre total d'anomalies: {total_outliers}", self.styles['CustomBody']))
            
            if outliers_data.get('byColumn'):
                table_data = [["Variable", "Nombre d'anomalies", "Pourcentage"]]
                
                for col, count in list(outliers_data.get('byColumn', {}).items())[:10]:
                    table_data.append([
                        col,
                        str(count.get('count', 0) if isinstance(count, dict) else count),
                        f"{count.get('percentage', 0):.1f}%" if isinstance(count, dict) else "N/A"
                    ])
                
                table = Table(table_data, colWidths=[5*cm, 4*cm, 5*cm])
                table.setStyle(self._get_table_style())
                story.append(Spacer(1, 0.3*cm))
                story.append(table)
        
        return story

    def _create_categorical_section(self, cat_data):
        """Section Variables Categoriques"""
        story = []
        story.append(Paragraph("VARIABLES CATEGORIQUES", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.5*cm))
        
        if isinstance(cat_data, dict) and 'variables' in cat_data:
            for var_name, var_data in list(cat_data.get('variables', {}).items())[:5]:
                story.append(Paragraph(f"Variable: {var_name}", self.styles['CustomSubheading']))
                
                table_data = [["Categorie", "Frequence", "Pourcentage"]]
                
                for cat, freq in list(var_data.get('frequencies', {}).items())[:8]:
                    total = sum(var_data.get('frequencies', {}).values()) or 1
                    pct = (freq / total * 100) if total > 0 else 0
                    table_data.append([str(cat), str(freq), f"{pct:.1f}%"])
                
                table = Table(table_data, colWidths=[5*cm, 3*cm, 6*cm])
                table.setStyle(self._get_table_style())
                story.append(table)
                story.append(Spacer(1, 0.3*cm))
        
        return story

    def _create_associations_section(self, assoc_data):
        """Section Correspondance/Associations"""
        story = []
        story.append(Paragraph("CORRESPONDANCE DES DONNEES", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.5*cm))
        
        if isinstance(assoc_data, dict):
            # Afficher les statistiques principales
            if assoc_data.get('total_diseases'):
                story.append(Paragraph(f"Nombre total d'entites: {assoc_data.get('total_diseases')}", self.styles['CustomBody']))
            
            if assoc_data.get('total_symptoms'):
                story.append(Paragraph(f"Nombre total d'attributs: {assoc_data.get('total_symptoms')}", self.styles['CustomBody']))
            
            # TF-IDF Top Features
            if assoc_data.get('tfidf_analysis', {}).get('top_symptoms_global'):
                story.append(Spacer(1, 0.3*cm))
                story.append(Paragraph("Top Attributs Globaux (TF-IDF):", self.styles['CustomSubheading']))
                
                table_data = [["Rang", "Attribut", "Score"]]
                
                for idx, item in enumerate(assoc_data.get('tfidf_analysis', {}).get('top_symptoms_global', [])[:10], 1):
                    table_data.append([
                        str(idx),
                        item.get('symptom', 'N/A'),
                        f"{item.get('tf_idf_score', 0):.4f}"
                    ])
                
                table = Table(table_data, colWidths=[2*cm, 8*cm, 4*cm])
                table.setStyle(self._get_table_style())
                story.append(table)
        
        return story
    
    def _get_table_style(self):
        """Style de tableau en noir et blanc"""
        return TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
        ])
