/**
 * Utilitaire de validation des données avant analyse
 */

export interface DataValidationReport {
  isValid: boolean;
  quality: {
    completeness: number;  // % de valeurs non-nulles
    uniquenessRatio: number;  // Ratio de valeurs uniques
    nullPercentage: number;
    duplicateRows: number;
  };
  columnAnalysis: {
    [columnName: string]: {
      nullCount: number;
      nullPercentage: number;
      uniqueValues: number;
      type: string;
      variance: number;  // 0 = pas de variance
      issue?: string;
    };
  };
  issues: string[];
  warnings: string[];
  suggestions: string[];
  problematicColumns: string[];
}

export class DataValidator {
  /**
   * Analyse la qualité des données
   */
  static validate(data: any[], columns?: string[]): DataValidationReport {
    const report: DataValidationReport = {
      isValid: true,
      quality: {
        completeness: 0,
        uniquenessRatio: 0,
        nullPercentage: 0,
        duplicateRows: 0,
      },
      columnAnalysis: {},
      issues: [],
      warnings: [],
      suggestions: [],
      problematicColumns: [],
    };

    if (!data || data.length === 0) {
      report.isValid = false;
      report.issues.push('Les données sont vides');
      return report;
    }

    // Analyser chaque colonne
    const colsToAnalyze = columns || Object.keys(data[0]);

    for (const col of colsToAnalyze) {
      const values = data.map(row => row[col]);
      const nonNullValues = values.filter(v => v !== null && v !== undefined && v !== '');
      const nullCount = values.length - nonNullValues.length;
      const nullPercentage = (nullCount / values.length) * 100;
      const uniqueValues = new Set(nonNullValues).size;
      
      // Détecter le type
      const type = this.detectType(nonNullValues);
      
      // Calculer la variance
      const variance = type === 'number' ? this.calculateVariance(nonNullValues) : 0;

      const analysis: any = {
        nullCount,
        nullPercentage: Math.round(nullPercentage * 100) / 100,
        uniqueValues,
        type,
        variance: Math.round(variance * 100) / 100,
      };

      // Identifier les problèmes
      const issues = this.identifyIssues(col, nullPercentage, uniqueValues, variance, values.length);
      if (issues.length > 0) {
        analysis.issue = issues[0];
        report.problematicColumns.push(col);
      }

      report.columnAnalysis[col] = analysis;
    }

    // Calculer les métriques globales
    const totalValues = Object.values(report.columnAnalysis).reduce(
      (sum: number, col: any) => sum + (data.length - col.nullCount),
      0
    );
    const totalPossibleValues = Object.keys(report.columnAnalysis).length * data.length;
    
    report.quality.completeness = Math.round((totalValues / totalPossibleValues) * 100 * 100) / 100;
    report.quality.nullPercentage = 100 - report.quality.completeness;

    // Détecter les doublons
    const jsonStrings = data.map(row => JSON.stringify(row));
    const uniqueRows = new Set(jsonStrings);
    report.quality.duplicateRows = data.length - uniqueRows.size;

    // Générer les alertes
    this.generateAlerts(report);

    return report;
  }

  private static detectType(values: any[]): string {
    if (values.length === 0) return 'unknown';

    // Détection booléenne: 0/1, true/false, oui/non
    const booleanValues = values.filter(v => 
      v === 0 || v === 1 || v === '0' || v === '1' ||
      v === true || v === false || v === 'true' || v === 'false' ||
      v?.toString?.().toLowerCase() === 'oui' ||
      v?.toString?.().toLowerCase() === 'non' ||
      v?.toString?.().toLowerCase() === 'yes' ||
      v?.toString?.().toLowerCase() === 'no'
    ).length;
    
    if (booleanValues / values.length > 0.95) return 'boolean';

    const numericCount = values.filter(v => !isNaN(Number(v))).length;
    if (numericCount / values.length > 0.8) return 'number';

    const uniqueCount = new Set(values).size;
    if (uniqueCount < 20 && uniqueCount < values.length / 10) return 'categorical';

    return 'string';
  }

  private static calculateVariance(values: any[]): number {
    const nums = values.map(v => Number(v)).filter(v => !isNaN(v));
    if (nums.length === 0) return 0;

    const mean = nums.reduce((a, b) => a + b, 0) / nums.length;
    const variance = nums.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / nums.length;
    return variance;
  }

  private static identifyIssues(
    colName: string,
    nullPercentage: number,
    uniqueValues: number,
    variance: number,
    totalCount: number
  ): string[] {
    const issues: string[] = [];

    if (nullPercentage === 100) {
      issues.push(`❌ Colonne complètement vide`);
    } else if (nullPercentage >= 70) {
      issues.push(`⚠️ ${nullPercentage.toFixed(1)}% de valeurs manquantes`);
    } else if (nullPercentage >= 50) {
      issues.push(`⚠️ ${nullPercentage.toFixed(1)}% de valeurs manquantes`);
    }

    if (uniqueValues === 1) {
      issues.push(`❌ Pas de variance (une seule valeur)`);
    }

    if (variance === 0 && uniqueValues > 1) {
      issues.push(`⚠️ Pas de variance numérique`);
    }

    if (uniqueValues < 3 && uniqueValues > 1) {
      issues.push(`⚠️ Très peu de valeurs uniques (${uniqueValues})`);
    }

    return issues;
  }

  private static generateAlerts(report: DataValidationReport): void {
    // Alertes sur la complétude
    if (report.quality.nullPercentage > 50) {
      report.issues.push(`🔴 Données incomplètes : ${report.quality.nullPercentage.toFixed(1)}% de valeurs manquantes`);
      report.isValid = false;
    } else if (report.quality.nullPercentage > 30) {
      report.warnings.push(`⚠️ Données partiellement incomplètes : ${report.quality.nullPercentage.toFixed(1)}% N/A`);
    }

    // Alertes sur les doublons
    if (report.quality.duplicateRows > 0) {
      report.warnings.push(`⚠️ ${report.quality.duplicateRows} lignes dupliquées détectées`);
    }

    // Alertes par colonne
    const problematicCols = Object.entries(report.columnAnalysis)
      .filter(([_, analysis]: any) => analysis.issue);

    if (problematicCols.length > 0) {
      report.warnings.push(
        `⚠️ ${problematicCols.length} colonnes problématiques : ` +
        problematicCols.map(([name]) => name).join(', ')
      );
    }

    // Suggestions
    if (report.problematicColumns.length > 0) {
      report.suggestions.push(
        `Envisager de supprimer ou nettoyer ces colonnes : ` +
        report.problematicColumns.slice(0, 5).join(', ')
      );
    }

    if (report.quality.nullPercentage > 20) {
      report.suggestions.push('Utiliser l\'option "Nettoyage Automatique" avant l\'analyse');
    }

    if (report.quality.completeness >= 80) {
      report.suggestions.push('✅ Qualité des données suffisante pour l\'analyse');
    }
  }

  /**
   * Suggère les colonnes à garder pour une analyse optimale
   */
  static suggestBestColumns(
    data: any[],
    maxColumns: number = 50,
    minCompletenessRatio: number = 0.7
  ): string[] {
    const report = this.validate(data);
    
    // Classer les colonnes par qualité
    const sortedCols = Object.entries(report.columnAnalysis)
      .sort(([_, a]: any, [__, b]: any) => {
        // Score = complétude - pénalité pour manque de variance
        const scoreA = (1 - a.nullPercentage / 100) - (a.variance === 0 ? 0.2 : 0);
        const scoreB = (1 - b.nullPercentage / 100) - (b.variance === 0 ? 0.2 : 0);
        return scoreB - scoreA;
      })
      .filter(([_, col]: any) => {
        // Garder seulement les colonnes complètes à 70%+
        return (1 - col.nullPercentage / 100) >= minCompletenessRatio;
      })
      .slice(0, maxColumns)
      .map(([name]) => name);

    return sortedCols;
  }
}
