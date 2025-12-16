# LANCEMENT RAPIDE - DataAnalyzer

## Pour Windows (Double-clic)

### Premiere utilisation

1. **Installez le backend** (une seule fois)
   - Double-cliquez sur `install-backend.bat`
   - Attendez la fin de l'installation (2-5 minutes)

2. **Lancez l'application**
   - Double-cliquez sur `start-all.bat`
   - Deux fenetres s'ouvrent (Backend + Frontend)
   - Ouvrez votre navigateur sur http://localhost:5173

### Utilisations suivantes

Double-cliquez simplement sur `start-all.bat`

## Scripts disponibles

- `install-backend.bat` - Installation initiale du backend (une seule fois)
- `start-all.bat` - Lance backend + frontend ensemble
- `start-backend.bat` - Lance uniquement le backend (port 5000)
- `start-frontend.bat` - Lance uniquement le frontend (port 5173)

## Problemes courants

### Le backend ne demarre pas
- Verifiez que Python est installe (version 3.10, 3.11 ou 3.12)
- Executez `install-backend.bat` pour reinstaller

### Le frontend ne demarre pas
- Verifiez que Node.js est installe
- Executez dans un terminal : `npm install`

### Port 5000 ou 5173 deja utilise
- Arretez les autres applications utilisant ces ports
- Ou modifiez les ports dans les fichiers de configuration

## Documentation complete

- `README.md` - Documentation complete du projet
- `QUICKSTART.md` - Guide de demarrage rapide
- `USER_GUIDE.md` - Guide utilisateur detaille
- `CONFIG_EXAMPLES.md` - Exemples de configuration
- `backend/INSTALLATION.md` - Guide d'installation backend detaille

## Support

En cas de probleme :
1. Consultez `backend/INSTALLATION.md` pour les erreurs Python
2. Verifiez les logs dans les fenetres de terminal
3. Assurez-vous d'avoir Python 3.10/3.11/3.12 (pas 3.14)

## Configuration requise

- **Python** : 3.10, 3.11 ou 3.12 (pas 3.14)
- **Node.js** : 16 ou superieur
- **RAM** : 4 GB minimum, 8 GB recommande
- **Espace disque** : 2 GB pour les dependances

## Demarrage reussi

Vous savez que tout fonctionne quand :

1. **Backend** affiche :
   ```
   * Running on http://127.0.0.1:5000
   * Debug mode: on
   ```

2. **Frontend** affiche :
   ```
   Local:   http://localhost:5173/
   ```

3. **Navigateur** sur http://localhost:5173 montre l'interface DataAnalyzer

Bon usage !
