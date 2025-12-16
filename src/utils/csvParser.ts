/**
 * Parser CSV robuste utilisant une approche native optimisée
 * Gère correctement les guillemets, les virgules dans les valeurs, et l'encodage UTF-8
 */

export interface CSVParseResult {
  data: any[];
  errors: string[];
  warnings: string[];
  stats: {
    rowCount: number;
    columnCount: number;
    estimatedSize: number;
  };
}

export class CSVParser {
  /**
   * Parse un fichier CSV avec gestion robuste des cas limites
   */
  static parse(text: string): CSVParseResult {
    const errors: string[] = [];
    const warnings: string[] = [];
    const data: any[] = [];

    try {
      // Nettoyer et splitter les lignes (gérer \r\n, \n, \r)
      const lines = text
        .split(/\r\n|\r|\n/)
        .map(line => line.trim())
        .filter(line => line.length > 0);

      if (lines.length < 2) {
        errors.push('Le fichier doit contenir au moins un en-tête et une ligne de données');
        return { data, errors, warnings, stats: { rowCount: 0, columnCount: 0, estimatedSize: 0 } };
      }

      // Parser les en-têtes
      const headers = this.parseCSVLine(lines[0]);
      
      if (headers.length === 0) {
        errors.push('Les en-têtes ne peuvent pas être vides');
        return { data, errors, warnings, stats: { rowCount: 0, columnCount: 0, estimatedSize: 0 } };
      }

      // Vérifier les colonnes dupliquées
      const duplicates = headers.filter((h, i) => headers.indexOf(h) !== i);
      if (duplicates.length > 0) {
        warnings.push(`⚠️ ${duplicates.length} colonnes ont des noms dupliqués : ${[...new Set(duplicates)].join(', ')}`);
      }

      // Parser les données
      for (let i = 1; i < lines.length; i++) {
        try {
          const values = this.parseCSVLine(lines[i]);
          
          // Ignorer les lignes vides
          if (values.every(v => v === '' || v === null)) {
            continue;
          }

          // Avertir si nombre de colonnes ≠
          if (values.length !== headers.length) {
            if (i <= 5) {  // Avertir seulement pour les 5 premières lignes
              warnings.push(
                `Ligne ${i + 1}: ${values.length} colonnes au lieu de ${headers.length} ` +
                `(${values.length > headers.length ? 'trop' : 'pas assez'})`
              );
            }
          }

          const row: any = {};
          headers.forEach((header, index) => {
            let value = values[index] || '';
            
            // Essayer de parser en nombre
            if (value !== '') {
              const numValue = parseFloat(value);
              row[header] = !isNaN(numValue) && value.trim() !== '' ? numValue : value;
            } else {
              row[header] = null;  // Utiliser null pour les valeurs vides
            }
          });

          data.push(row);
        } catch (err) {
          errors.push(`Erreur ligne ${i + 1}: ${err instanceof Error ? err.message : 'Erreur de parsing'}`);
        }
      }

      if (data.length === 0) {
        errors.push('Aucune ligne de données valide trouvée');
      }

      return {
        data,
        errors,
        warnings,
        stats: {
          rowCount: data.length,
          columnCount: headers.length,
          estimatedSize: text.length,
        }
      };
    } catch (err) {
      errors.push(`Erreur de parsing global: ${err instanceof Error ? err.message : 'Erreur inconnue'}`);
      return { data, errors, warnings, stats: { rowCount: 0, columnCount: 0, estimatedSize: 0 } };
    }
  }

  /**
   * Parse une ligne CSV en respectant les guillemets
   * Gère les cas : "valeur", valeur sans guillemets, "valeur avec, virgule"
   */
  private static parseCSVLine(line: string): string[] {
    const result: string[] = [];
    let current = '';
    let insideQuotes = false;

    for (let i = 0; i < line.length; i++) {
      const char = line[i];
      const nextChar = line[i + 1];

      if (char === '"') {
        if (insideQuotes && nextChar === '"') {
          // Guillemets échappés ("" → ")
          current += '"';
          i++;  // Sauter le prochain guillemet
        } else {
          // Toggle guillemets
          insideQuotes = !insideQuotes;
        }
      } else if (char === ',' && !insideQuotes) {
        // Fin de champ
        result.push(current.trim().replace(/^"|"$/g, ''));
        current = '';
      } else {
        current += char;
      }
    }

    // Ajouter le dernier champ
    result.push(current.trim().replace(/^"|"$/g, ''));

    return result;
  }

  /**
   * Valide un fichier CSV avant parsing complet
   */
  static validate(file: File): { valid: boolean; error?: string; warning?: string } {
    const MAX_SIZE = 100 * 1024 * 1024;  // 100MB
    
    if (file.size > MAX_SIZE) {
      return {
        valid: false,
        error: `Fichier trop volumineux (${(file.size / 1024 / 1024).toFixed(2)}MB > 100MB)`
      };
    }

    if (!file.name.toLowerCase().endsWith('.csv')) {
      return {
        valid: false,
        error: 'Seuls les fichiers .csv sont acceptés'
      };
    }

    return { valid: true };
  }

  /**
   * Détecte si un fichier CSV est trop volumineux et suggère un sous-ensemble
   */
  static estimateColumns(firstLine: string): number {
    return this.parseCSVLine(firstLine).length;
  }
}
