import React, { useState } from 'react';
import { X, ChevronRight, Search, Book, HelpCircle, FileText, Settings, Zap } from 'lucide-react';

interface HelpMenuProps {
  isOpen: boolean;
  onClose: () => void;
}

interface HelpSection {
  id: string;
  title: string;
  icon: React.ComponentType<any>;
  content: HelpContent[];
}

interface HelpContent {
  title: string;
  description: string;
  steps?: string[];
  tips?: string[];
  examples?: string[];
}

const HelpMenu: React.FC<HelpMenuProps> = ({ isOpen, onClose }) => {
  const [activeSection, setActiveSection] = useState<string>('getting-started');
  const [searchQuery, setSearchQuery] = useState('');

  const helpSections: HelpSection[] = [
    {
      id: 'getting-started',
      title: 'Démarrage rapide',
      icon: Zap,
      content: [
        {
          title: 'Premiers pas avec DataAnalyzer',
          description: 'Apprenez à utiliser l\'application en 5 minutes.',
          steps: [
            'Importez vos données (CSV, XLSX ou JSON)',
            'Prévisualisez et validez les colonnes détectées',
            'Configurez les types de colonnes si nécessaire',
            'Sélectionnez les analyses à effectuer',
            'Consultez les résultats et générez un rapport PDF'
          ],
          tips: [
            'Les fichiers CSV doivent avoir une ligne d\'en-tête',
            'Maximum 1 million de lignes recommandé',
            'Format de date accepté : YYYY-MM-DD ou DD/MM/YYYY'
          ]
        },
        {
          title: 'Types de fichiers supportés',
          description: 'Formats de données acceptés par l\'application.',
          examples: [
            'CSV : Fichiers texte avec virgules ou point-virgules',
            'XLSX : Fichiers Excel (Microsoft Office)',
            'JSON : Fichiers JavaScript Object Notation'
          ]
        }
      ]
    },
    {
      id: 'data-preparation',
      title: 'Préparation des données',
      icon: FileText,
      content: [
        {
          title: 'Types de colonnes',
          description: 'Comprendre les différents types de données détectés automatiquement.',
          examples: [
            'Number : Variables numériques continues (prix, âge, température)',
            'Categorical : Variables à catégories (ville, catégorie produit)',
            'Date : Variables temporelles (dates de vente, périodes)',
            'Boolean : Variables binaires (oui/non, vrai/faux)',
            'String : Texte libre (commentaires, descriptions)'
          ],
          tips: [
            'Vérifiez toujours la détection automatique',
            'Les colonnes de dates doivent être au format standard',
            'Sélectionnez uniquement les colonnes pertinentes pour l\'analyse'
          ]
        },
        {
          title: 'Nettoyage des données',
          description: 'Préparez vos données pour une analyse optimale.',
          steps: [
            'Supprimez les doublons automatiquement',
            'Gérez les valeurs manquantes (moyenne, médiane, KNN)',
            'Détectez et traitez les valeurs aberrantes',
            'Normalisez les données numériques si nécessaire',
            'Encodez les variables catégorielles'
          ]
        }
      ]
    },
    {
      id: 'basic-analyses',
      title: 'Analyses de base',
      icon: Book,
      content: [
        {
          title: 'Statistiques descriptives',
          description: 'Mesures de tendance centrale et de dispersion.',
          examples: [
            'Moyenne : Valeur centrale des données',
            'Médiane : Valeur qui sépare les données en deux parties égales',
            'Écart-type : Mesure de la dispersion autour de la moyenne',
            'Quartiles : Division des données en 4 parties égales',
            'Min/Max : Valeurs extrêmes'
          ]
        },
        {
          title: 'Analyse de corrélation',
          description: 'Identifiez les relations entre variables numériques.',
          tips: [
            'Corrélation proche de 1 : relation positive forte',
            'Corrélation proche de -1 : relation négative forte',
            'Corrélation proche de 0 : pas de relation linéaire',
            'La corrélation n\'implique pas la causalité'
          ]
        },
        {
          title: 'Détection d\'anomalies',
          description: 'Identifiez les valeurs aberrantes dans vos données.',
          examples: [
            'Méthode IQR : Détecte les valeurs hors de l\'intervalle interquartile',
            'Méthode Z-score : Détecte les valeurs à plus de 3 écarts-types',
            'Isolation Forest : Algorithme de machine learning pour anomalies complexes'
          ]
        }
      ]
    },
    {
      id: 'advanced-analyses',
      title: 'Analyses avancées',
      icon: Settings,
      content: [
        {
          title: 'Régression',
          description: 'Prédisez une variable continue à partir d\'autres variables.',
          examples: [
            'Régression linéaire : Relation linéaire simple',
            'Régression polynomiale : Relations non-linéaires',
            'Ridge/Lasso : Régularisation pour éviter le surapprentissage',
            'Régression logistique : Classification binaire ou multi-classe'
          ],
          tips: [
            'Vérifiez les hypothèses de normalité des résidus',
            'Utilisez la cross-validation pour valider le modèle',
            'R² > 0.7 indique généralement un bon modèle'
          ]
        },
        {
          title: 'Classification',
          description: 'Prédisez une catégorie à partir de caractéristiques.',
          examples: [
            'Random Forest : Robuste et précis pour la plupart des cas',
            'SVM : Efficace pour les données de haute dimension',
            'XGBoost : Performance maximale pour la compétition',
            'KNN : Simple mais efficace pour données similaires'
          ],
          tips: [
            'Équilibrez vos classes si nécessaire',
            'Utilisez la matrice de confusion pour comprendre les erreurs',
            'F1-Score > 0.8 est considéré comme bon'
          ]
        },
        {
          title: 'Réseaux de neurones',
          description: 'Modèles de deep learning pour problèmes complexes.',
          examples: [
            'MLP : Réseau multicouche pour données tabulaires',
            'CNN : Convolution pour données avec structure spatiale',
            'RNN/LSTM : Séquences et séries temporelles'
          ],
          tips: [
            'Nécessite plus de données que les algorithmes classiques',
            'GPU recommandé pour accélérer l\'entraînement',
            'Utilisez early stopping pour éviter le surapprentissage'
          ]
        },
        {
          title: 'Séries temporelles',
          description: 'Analysez et prédisez des données temporelles.',
          examples: [
            'ARIMA : Modèle autorégressif intégré à moyenne mobile',
            'SARIMA : ARIMA avec composante saisonnière',
            'Prophet : Modèle Facebook pour séries avec tendances'
          ],
          tips: [
            'Vérifiez la stationnarité avec le test ADF',
            'Identifiez la saisonnalité avant de choisir le modèle',
            'MAPE < 10% indique une excellente prévision'
          ]
        },
        {
          title: 'Clustering avancé',
          description: 'Segmentez vos données en groupes homogènes.',
          examples: [
            'K-Means : Rapide, nécessite de définir k',
            'DBSCAN : Détecte les formes arbitraires et le bruit',
            'Hierarchical : Visualisation avec dendrogramme',
            'GMM : Modèle probabiliste avec distributions gaussiennes'
          ],
          tips: [
            'Normalisez les données avant le clustering',
            'Utilisez le silhouette score pour évaluer la qualité',
            'Score > 0.5 indique des clusters bien définis'
          ]
        },
        {
          title: 'Tests statistiques',
          description: 'Validez vos hypothèses avec des tests rigoureux.',
          examples: [
            'Test de normalité : Shapiro-Wilk, D\'Agostino',
            'T-test : Comparaison de moyennes entre 2 groupes',
            'ANOVA : Comparaison de moyennes entre 3+ groupes',
            'Chi-carré : Test d\'indépendance pour variables catégorielles',
            'Tests de corrélation : Pearson, Spearman'
          ],
          tips: [
            'p-value < 0.05 : hypothèse nulle rejetée (significatif)',
            'p-value > 0.05 : on ne peut pas rejeter l\'hypothèse nulle',
            'Vérifiez toujours les conditions d\'application du test'
          ]
        }
      ]
    },
    {
      id: 'reports',
      title: 'Rapports PDF',
      icon: FileText,
      content: [
        {
          title: 'Génération de rapports',
          description: 'Créez des rapports professionnels de vos analyses.',
          steps: [
            'Effectuez vos analyses',
            'Cliquez sur "Générer un rapport PDF"',
            'Le rapport est généré au format A4',
            'Téléchargez le fichier PDF'
          ],
          tips: [
            'Format A4 optimisé pour l\'impression',
            'Police 13-14pt pour une lecture optimale',
            'Mise en page noir et blanc professionnelle',
            'Inclut toutes les analyses effectuées'
          ]
        },
        {
          title: 'Contenu du rapport',
          description: 'Structure et sections incluses dans le rapport PDF.',
          examples: [
            'Page de garde avec titre et date',
            'Table des matières navigable',
            'Résumé exécutif des principales conclusions',
            'Sections détaillées par type d\'analyse',
            'Tableaux de métriques et résultats',
            'Recommandations automatiques'
          ]
        }
      ]
    },
    {
      id: 'best-practices',
      title: 'Bonnes pratiques',
      icon: HelpCircle,
      content: [
        {
          title: 'Qualité des données',
          description: 'Assurez-vous de la qualité de vos données avant l\'analyse.',
          tips: [
            'Vérifiez qu\'il n\'y a pas trop de valeurs manquantes (< 20%)',
            'Identifiez et traitez les valeurs aberrantes',
            'Assurez-vous que les types de colonnes sont corrects',
            'Vérifiez la cohérence des données (dates, formats)',
            'Supprimez les doublons avant l\'analyse'
          ]
        },
        {
          title: 'Choix des analyses',
          description: 'Sélectionnez les bonnes analyses pour votre problématique.',
          tips: [
            'Régression : Prédire une valeur continue (prix, température)',
            'Classification : Prédire une catégorie (client satisfait/non)',
            'Clustering : Découvrir des groupes naturels dans les données',
            'Séries temporelles : Données avec composante temporelle',
            'Tests statistiques : Valider des hypothèses'
          ]
        },
        {
          title: 'Interprétation des résultats',
          description: 'Comprenez et validez vos résultats.',
          tips: [
            'Ne confondez pas corrélation et causalité',
            'Vérifiez les métriques de performance (R², accuracy, F1-score)',
            'Utilisez la cross-validation pour valider les modèles',
            'Comparez plusieurs algorithmes avant de conclure',
            'Documentez vos hypothèses et conclusions'
          ]
        },
        {
          title: 'Performance et limites',
          description: 'Optimisez l\'utilisation de l\'application.',
          tips: [
            'Maximum 1 million de lignes recommandé',
            'Les analyses avancées nécessitent le backend Python',
            'GPU recommandé pour les réseaux de neurones',
            'Minimum 8 GB de RAM pour les gros datasets',
            'Les analyses complexes peuvent prendre plusieurs minutes'
          ]
        }
      ]
    },
    {
      id: 'troubleshooting',
      title: 'Dépannage',
      icon: HelpCircle,
      content: [
        {
          title: 'Problèmes courants',
          description: 'Solutions aux erreurs fréquentes.',
          examples: [
            'Fichier non reconnu : Vérifiez le format (CSV, XLSX, JSON)',
            'Colonnes mal détectées : Modifiez manuellement les types',
            'Analyses non disponibles : Vérifiez que le backend est lancé',
            'Erreur de mémoire : Réduisez la taille du dataset',
            'Temps d\'analyse long : Normal pour deep learning et gros datasets'
          ]
        },
        {
          title: 'Backend non disponible',
          description: 'Si les analyses avancées ne fonctionnent pas.',
          steps: [
            'Vérifiez que Python est installé (version 3.8+)',
            'Installez les dépendances : pip install -r requirements.txt',
            'Lancez le backend : python backend/app.py',
            'Vérifiez que le port 5000 est disponible',
            'Consultez les logs pour identifier l\'erreur'
          ]
        },
        {
          title: 'Qualité des résultats',
          description: 'Que faire si les résultats ne sont pas satisfaisants.',
          tips: [
            'Nettoyez vos données avec l\'option "Data Cleaning"',
            'Essayez différents algorithmes et comparez',
            'Augmentez la taille de votre dataset si possible',
            'Vérifiez que les features sont pertinentes',
            'Normalisez les données pour améliorer les performances'
          ]
        }
      ]
    }
  ];

  const activeContent = helpSections.find(s => s.id === activeSection);

  const filteredSections = searchQuery
    ? helpSections.filter(section =>
        section.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        section.content.some(c =>
          c.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
          c.description.toLowerCase().includes(searchQuery.toLowerCase())
        )
      )
    : helpSections;

  if (!isOpen) return null;

  return (
    <>
      {/* Overlay */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 z-50"
        onClick={onClose}
      />

      {/* Help Menu */}
      <div className="fixed inset-y-0 right-0 w-full sm:max-w-4xl bg-white shadow-2xl z-50 overflow-hidden flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-4 sm:p-6">
          <div className="flex items-center justify-between mb-3 sm:mb-4">
            <h2 className="text-xl sm:text-2xl font-bold">Guide d'utilisation</h2>
            <button
              onClick={onClose}
              className="p-2 hover:bg-white hover:bg-opacity-20 rounded-lg transition-colors"
            >
              <X className="w-5 h-5 sm:w-6 sm:h-6" />
            </button>
          </div>

          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 sm:w-5 sm:h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Rechercher dans le guide..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 sm:pl-10 pr-4 py-2 text-sm sm:text-base rounded-lg text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-white"
            />
          </div>
        </div>

        <div className="flex flex-1 overflow-hidden flex-col sm:flex-row">
          {/* Sidebar - Hidden on mobile, shown as tabs */}
          <div className="hidden sm:block sm:w-64 bg-gray-50 border-r border-gray-200 overflow-y-auto">
            <nav className="p-4 space-y-1">
              {filteredSections.map((section) => {
                const Icon = section.icon;
                return (
                  <button
                    key={section.id}
                    onClick={() => setActiveSection(section.id)}
                    className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition-colors ${
                      activeSection === section.id
                        ? 'bg-blue-600 text-white'
                        : 'text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    <Icon className="w-5 h-5 flex-shrink-0" />
                    <span className="font-medium text-sm">{section.title}</span>
                    <ChevronRight className="w-4 h-4 ml-auto flex-shrink-0" />
                  </button>
                );
              })}
            </nav>
          </div>

          {/* Mobile Section Selector */}
          <div className="sm:hidden bg-gray-50 border-b border-gray-200 px-4 py-3">
            <select
              value={activeSection}
              onChange={(e) => setActiveSection(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {filteredSections.map((section) => (
                <option key={section.id} value={section.id}>
                  {section.title}
                </option>
              ))}
            </select>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
            {activeContent && (
              <div className="max-w-3xl mx-auto">
                <h3 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-4 sm:mb-6">
                  {activeContent.title}
                </h3>

                <div className="space-y-6 sm:space-y-8">
                  {activeContent.content.map((item, index) => (
                    <div key={index} className="bg-white border border-gray-200 rounded-lg p-4 sm:p-6">
                      <h4 className="text-lg sm:text-xl font-semibold text-gray-900 mb-2 sm:mb-3">
                        {item.title}
                      </h4>
                      <p className="text-sm sm:text-base text-gray-600 mb-3 sm:mb-4">{item.description}</p>

                      {item.steps && (
                        <div className="mb-3 sm:mb-4">
                          <h5 className="font-semibold text-gray-900 mb-2 text-sm sm:text-base">Étapes :</h5>
                          <ol className="list-decimal list-inside space-y-1.5 sm:space-y-2 text-gray-700 text-sm sm:text-base">
                            {item.steps.map((step, i) => (
                              <li key={i} className="pl-1">{step}</li>
                            ))}
                          </ol>
                        </div>
                      )}

                      {item.examples && (
                        <div className="mb-3 sm:mb-4">
                          <h5 className="font-semibold text-gray-900 mb-2 text-sm sm:text-base">Exemples :</h5>
                          <ul className="list-disc list-inside space-y-1.5 sm:space-y-2 text-gray-700 text-sm sm:text-base">
                            {item.examples.map((example, i) => (
                              <li key={i} className="pl-1">{example}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {item.tips && (
                        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 sm:p-4">
                          <h5 className="font-semibold text-blue-900 mb-2 text-sm sm:text-base">Conseils :</h5>
                          <ul className="list-disc list-inside space-y-1 text-blue-800 text-xs sm:text-sm">
                            {item.tips.map((tip, i) => (
                              <li key={i} className="pl-1">{tip}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
};

export default HelpMenu;
