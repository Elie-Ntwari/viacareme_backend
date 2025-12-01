import React, { useState, useMemo } from 'react'; // Ajout de useMemo
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';

// Enregistrer les composants de Chart.js
ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
);

// Données initiales pour 3 visites de base
const initialVisits = [
    { id: 1, Age: 28, SystolicBP: 120, DiastolicBP: 80, BS: 6.5, BodyTemp: 98.6, HeartRate: 85 },
    { id: 2, Age: 28, SystolicBP: 135, DiastolicBP: 88, BS: 7.2, BodyTemp: 99.1, HeartRate: 95 },
    { id: 3, Age: 28, SystolicBP: 145, DiastolicBP: 95, BS: 10.8, BodyTemp: 99.4, HeartRate: 105 },
];

// Valeurs par défaut pour une nouvelle visite
const defaultNewVisit = {
    Age: 28,
    SystolicBP: 120,
    DiastolicBP: 80,
    BS: 6.5,
    BodyTemp: 98.6,
    HeartRate: 85
};

// Mappage des noms de champs bruts vers des noms français lisibles
const featureMap = {
    Age: 'Âge',
    SystolicBP: 'Tension Systolique en mmHg',
    DiastolicBP: 'Tension Diastolique en mmHg',
    BS: 'Glycémie (BS)',
    BodyTemp: 'Température Corporelle en F',
    HeartRate: 'Fréquence Cardiaque',
};

// Fonction pour déterminer le niveau de risque basé sur la prédiction numérique
const getRiskLevel = (prediction) => {
    if (prediction <= 1.5) return { text: 'Faible', class: 'risk-low', threshold: 1, icon: '😊' };
    if (prediction <= 2.5) return { text: 'Moyen', class: 'risk-medium', threshold: 2, icon: '⚠️' };
    return { text: 'Élevé', class: 'risk-high', threshold: 3, icon: '🚨' };
};

// Logique pour déterminer l'explication clinique basée sur les contributions SHAP
const generateClinicalExplanation = (visitData, shapData, prediction) => {
    const risk = getRiskLevel(prediction);

    // 1. Convertir les contributions SHAP en tableau pour le tri
    const contributions = Object.entries(shapData.contributions)
        .map(([feature, value]) => ({
            feature: featureMap[feature] || feature,
            value: value,
            dataValue: visitData[feature]
        }));

    // 2. Trier par valeur absolue de contribution pour trouver les 3 plus influents
    contributions.sort((a, b) => Math.abs(b.value) - Math.abs(a.value));
    const top3 = contributions.slice(0, 3);

    // 3. Séparer les facteurs augmentant et diminuant le risque
    const riskIncreasing = top3.filter(c => c.value > 0).map(c =>
        `${c.feature} (${c.dataValue})`
    );
    const riskDecreasing = top3.filter(c => c.value < 0).map(c =>
        `${c.feature} (${c.dataValue})`
    );

    let explanation = `Le risque de complications pour cette visite est jugé **${risk.text}** (${prediction.toFixed(2)}).`;

    if (risk.threshold === 3) {
        // Risque Élevé
        explanation += ` **Ceci est un signal d'alarme.** Les facteurs principaux qui tirent le risque vers le haut sont : ${riskIncreasing.join(', ')}.`;
        explanation += `<br/>*Analyse : Une surveillance immédiate est essentielle. Les valeurs de ${riskIncreasing[0] || 'ces facteurs clés'} nécessitent une évaluation plus approfondie et une intervention.*`;
    } else if (risk.threshold === 2) {
        // Risque Moyen
        if (riskIncreasing.length > 0) {
            explanation += ` Bien que non critique, la prédiction est influencée par des signes d'alerte. Les facteurs qui augmentent le risque sont notamment : ${riskIncreasing.join(', ')}.`;
            explanation += `<br/>*Analyse : Maintenez une vigilance accrue sur ${riskIncreasing[0] || 'ces paramètres'}. Les mesures préventives doivent être renforcées si ces facteurs persistent.*`;
        } else {
            explanation += ` La patiente est à un niveau Moyen, principalement en raison de sa valeur de base, mais ${riskDecreasing.join(', ')} ont contribué positivement.`;
            explanation += `<br/>*Analyse : Les mesures actuelles semblent aider. Une surveillance rapprochée est recommandée.*`;
        }
    } else {
        // Risque Faible (sans recommandation de routine)
        explanation += ` Le profil de la patiente est rassurant pour cette visite. Les facteurs qui contribuent le plus à maintenir ce faible risque sont : ${riskDecreasing.join(', ')}.`;
        explanation += `<br/>*Analyse : La patiente présente des valeurs normales. Le médecin traitant doit décider des prochaines étapes de la prise en charge.*`;
    }

    return explanation;
};


// NOUVEAU COMPOSANT : Résumé et Tendance
const RiskSummary = ({ predictions }) => {
    if (!predictions || predictions.length === 0) return null;

    // 1. Calcul du risque moyen
    const totalRisk = predictions.reduce((sum, current) => sum + current, 0);
    const averageRisk = totalRisk / predictions.length;
    const averageRiskLevel = getRiskLevel(averageRisk);

    // 2. Détermination de la tendance
    let trend = { text: 'Stable', icon: '↔️', class: 'trend-stable' };
    
    if (predictions.length >= 2) {
        const first = predictions[0];
        const last = predictions[predictions.length - 1];
        
        // Calculer la variation en pourcentage ou en point d'échelle (0.2 point d'échelle comme seuil de changement)
        const difference = last - first;
        const trendThreshold = 0.2; // Seuil pour considérer un changement significatif
        
        if (difference > trendThreshold) {
            trend = { text: 'En Hausse', icon: '🔺', class: 'trend-up' };
        } else if (difference < -trendThreshold) {
            trend = { text: 'En Baisse', icon: '✅', class: 'trend-down' };
        }
    }

    return (
        <div className="risk-summary-container">
            <div className={`summary-card ${averageRiskLevel.class}`}>
                <h4>{averageRiskLevel.icon} Niveau de Risque Moyen</h4>
                <p className="value">{averageRiskLevel.text}</p>
                <span className="detail">({averageRisk.toFixed(2)} sur l'échelle 1-3)</span>
            </div>
            <div className={`summary-card ${trend.class}`}>
                <h4>{trend.icon} Tendance Globale du Risque</h4>
                <p className="value">{trend.text}</p>
                {predictions.length >= 2 && (
                    <span className="detail">
                        {predictions.length} visites analysées )
                    </span>
                )}
            </div>
        </div>
    );
};


function App() {
    // Initialise avec 3 visites
    const [visits, setVisits] = useState(initialVisits);
    const [results, setResults] = useState(null);
    const [loading, setLoading] = useState(false);
    // L'état d'erreur stockera soit une chaîne simple, soit l'objet d'erreur détaillé de Django
    const [error, setError] = useState(null);

    const handleChange = (id, field, value) => {
        setVisits(prevVisits =>
            prevVisits.map(visit =>
                visit.id === id ? { ...visit, [field]: parseFloat(value) || 0 } : visit
            )
        );
    };

    // LOGIQUE DE GESTION DES VISITES
    const addVisit = () => {
        // Détermine le nouvel ID (max ID + 1)
        const newId = visits.length > 0 ? Math.max(...visits.map(v => v.id)) + 1 : 1;
        setVisits(prevVisits => [
            ...prevVisits,
            { id: newId, ...defaultNewVisit }
        ]);
        setResults(null); // Réinitialiser les résultats lors de l'ajout/suppression
    };

    const removeVisit = () => {
        if (visits.length > 1) {
            // Retire la dernière visite de la liste
            setVisits(prevVisits => prevVisits.slice(0, -1));
            setResults(null); // Réinitialiser les résultats
        } else {
            setError({ message: "Impossible de supprimer. Au moins une visite est requise.", details: [] });
            setTimeout(() => setError(null), 3000);
        }
    };
    // FIN LOGIQUE DE GESTION DES VISITES

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setResults(null);

        // Assurez-vous que toutes les valeurs sont numériques (même si les inputs sont de type number)
        const visitsData = visits.map(({ id, ...rest }) =>
            Object.fromEntries(
                Object.entries(rest).map(([key, value]) => [key, Number(value)])
            )
        );

        // URL de l'API : Assurez-vous que le serveur Django est en cours d'exécution
        const apiUrl = 'http://127.0.0.1:8000/api/predict/';

        try {
            const makeApiCallWithBackoff = async (url, options, retries = 3) => {
                for (let i = 0; i < retries; i++) {
                    try {
                        const response = await fetch(url, options);

                        let responseData = {};
                        
                        // 1. Vérifier si la réponse est de type JSON
                        const contentType = response.headers.get("content-type");
                        const isJson = contentType && contentType.includes("application/json");

                        if (isJson) {
                            try {
                                responseData = await response.json();
                            } catch (parseError) {
                                // Erreur de parsing JSON (souvent un 500 HTML)
                                throw {
                                    status: response.status,
                                    message: "Erreur de format de réponse. Le serveur a renvoyé un contenu non-JSON.",
                                    details: [parseError.message]
                                };
                            }
                        } else if (!response.ok) {
                            // Réponse non-OK (ex: 404, 500) qui n'est pas JSON
                            throw {
                                status: response.status,
                                message: `Erreur HTTP ${response.status} sans format JSON. Le serveur est peut-être en panne.`,
                                details: []
                            };
                        }
                        
                        // 2. Si la réponse est OK (200-299)
                        if (response.ok) {
                            return responseData; // Succès
                        }


                        // 3. Gestion des erreurs formatées par l'API (4xx ou 5xx)
                        if (responseData.status === 'error' && responseData.message) {
                            // Lancer une erreur personnalisée avec les détails de Django
                            throw {
                                status: response.status,
                                message: responseData.message,
                                details: responseData.details || []
                            };
                        }

                        // Gestion de la limite de débit (Too Many Requests - 429)
                        if (response.status === 429) {
                            throw new Error('Too Many Requests - Retrying');
                        }

                        // 4. Autres erreurs HTTP non formatées par le backend
                        throw {
                            status: response.status,
                            message: `Erreur HTTP ${response.status} non détaillée.`,
                            details: []
                        };

                    } catch (err) {
                        // Si c'est une erreur de type 'Too Many Requests', attendre et réessayer
                        if (err.message && err.message.includes('Too Many Requests') && i < retries - 1) {
                             const delay = Math.pow(2, i) * 1000;
                             await new Promise(resolve => setTimeout(resolve, delay));
                             continue;
                        }
                        // Relancer l'erreur pour la capturer dans le bloc catch principal
                        throw err;
                    }
                }
                // Si toutes les tentatives échouent
                throw new Error("Échec de la communication après plusieurs tentatives.");
            };

            const data = await makeApiCallWithBackoff(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ visits: visitsData }),
            });

            // Vérification de la structure des données reçues
            if (!data.predictions || !data.shap_explanations || data.predictions.length !== data.shap_explanations.length) {
                 throw new Error("La structure de la réponse du backend est invalide ou incomplète.");
            }

            // Assurez-vous que les données initiales (visits) sont passées aux explications
            const resultsWithInputs = {
                ...data,
                input_visits: visitsData
            };
            setResults(resultsWithInputs);

        } catch (err) {
            console.error("Erreur lors de la soumission :", err);

            // Si l'erreur provient de la validation Django (400) ou des erreurs custom lancées dans le try
            if (err.status && err.message) {
                 setError(err); // Stocke l'objet { status, message, details }
            } else {
                // Erreur réseau (serveur injoignable, CORS, etc.) ou Erreur JavaScript (non-API)
                 setError({
                     message: `Erreur de communication: ${err.message || 'Problème de connexion'}. Veuillez vérifier que le serveur Django est démarré et accessible à l'adresse '${apiUrl}'.`,
                     details: []
                 });
            }
        } finally {
            setLoading(false); // S'assure que le bouton revient à l'état normal
        }
    };

    // Configuration du graphique Chart.js (mise à jour pour l'échelle 1-3)
    const chartData = useMemo(() => ({
        labels: results ? results.predictions.map((_, index) => `Visite ${index + 1}`) : [],
        datasets: [
            {
                label: 'Risque Prédit (1=Faible, 2=Moyen, 3=Élevé)',
                data: results ? results.predictions : [],
                borderColor: '#007bff',
                backgroundColor: 'rgba(0, 123, 255, 0.4)',
                tension: 0.3,
                borderWidth: 3,
                pointBackgroundColor: '#dc3545',
                pointRadius: 5,
                pointHoverRadius: 7,
            },
        ],
    }), [results]); // useMemo pour optimiser la re-création des données

    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { 
                position: 'top', 
                labels: {
                    color: '#333' // Texte de la légende
                }
            },
            title: {
                display: true,
                text: 'Évolution du risque de la patiente (Échelle: 1 à 3)',
                color: '#495057', // Couleur du titre du graphique
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        let label = context.dataset.label || '';
                        if (context.parsed.y !== null) {
                            const riskLevel = context.parsed.y;
                            const { text: riskText } = getRiskLevel(riskLevel);

                            label = `${riskText} (${riskLevel.toFixed(2)})`;
                        }
                        return label;
                    }
                }
            }
        },
        scales: {
            y: {
                min: 0.5,
                max: 3.5,
                ticks: {
                    stepSize: 1,
                    color: '#6c757d', // Couleur des étiquettes de l'axe Y
                    // MODIFICATION: Afficher seulement 1, 2, 3 sur l'axe Y
                    callback: function(value) {
                        if (value === 1 || value === 2 || value === 3) return value;
                        return null;
                    },
                },
                title: {
                    display: true,
                    text: 'Niveau de Risque Prédit',
                    color: '#495057' // Couleur du titre de l'axe Y
                },
                grid: {
                    color: '#e9ecef' // Lignes de grille horizontales
                }
            },
            x: {
                ticks: {
                    color: '#6c757d' // Couleur des étiquettes de l'axe X
                },
                title: {
                    display: true,
                    text: 'Visites Séquentielles',
                    color: '#495057' // Couleur du titre de l'axe X
                },
                grid: {
                    display: false // Supprimer les lignes de grille verticales
                }
            }
        }
    };

    // Composant pour afficher les explications SHAP
    const ShapExplanations = ({ results }) => {
        if (!results || !results.shap_explanations || results.shap_explanations.length === 0) return null;

        const { shap_explanations, predictions, input_visits } = results;

        return (
            <div className="shap-explanations card-block">
                <h3>🔍 Explications Cliniques Simplifiées par Visite</h3>
                <p className="subtitle">Ce résumé interprète les facteurs influents pour vous guider rapidement.</p>
                {/* Disposition en colonne des cartes d'explication */}
                <div className="visits-column-list">
                    {shap_explanations.map((shap, index) => {
                        const prediction = predictions[index];
                        const risk = getRiskLevel(prediction);
                        const visitData = input_visits[index];
                        const explanationText = generateClinicalExplanation(visitData, shap, prediction);

                        return (
                            <div
                                key={index}
                                className={`visit-explanation-card ${risk.class}`}
                            >
                                <h4>Résultat pour la Visite {index + 1}</h4>
                                <p
                                    className="explanation-text"
                                    dangerouslySetInnerHTML={{ __html: explanationText }}
                                />

                                <div className="raw-details">
                                    <p>Valeur brute du modèle: <span className="raw-value">{prediction.toFixed(4)}</span></p>
                                    <p>Base Value (point de départ): <span className="raw-value">{shap.base_value.toFixed(4)}</span></p>
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>
        );
    };

    // Composant pour afficher les messages d'erreur détaillés
    const ErrorDisplay = ({ error }) => {
        if (!error) return null;

        return (
            <div className="error-message">
                <p><strong>{error.message}</strong></p>
                {error.details && error.details.length > 0 && (
                    <>
                        <p style={{marginTop: '10px', marginBottom: '5px'}}>**Détails de Validation :**</p>
                        <ul style={{listStyleType: 'disc', marginLeft: '20px'}}>
                            {error.details.map((detail, index) => (
                                <li key={index} style={{marginBottom: '5px'}}>{detail}</li>
                            ))}
                        </ul>
                    </>
                )}
            </div>
        );
    };

    // Nouveau composant pour le menu de gauche (Sidebar)
    const SideMenu = () => {
        return (
            <div className="sidebar">
                <div className="logo-container">
                    {/* Simulacre du logo VIA CARE */}
                    <div className="logo-text">
                        <img src="viacare_logo.png" alt="VIA CARE Logo" style={{marginLeft:'10px', marginRight: '10px',width:'200px'}} />
                    
                    </div>
                </div>
                
                <nav className="nav-menu">
                    <a href="#dashboard" className="nav-item">
                        <i className="fas fa-tachometer-alt"></i> Dashboard
                    </a>
                    <a href="#gestion-hopitaux" className="className active">
                        <i className="fas fa-hospital"></i> Gestion des hôpitaux
                    </a>
                    <a href="#gestion-cartes" className="nav-item">
                        <i className="fas fa-id-card"></i> Gestion des cartes
                    </a>
                    <a href="#gestion-utilisateurs" className="nav-item">
                        <i className="fas fa-users"></i> Gestion des utilisateurs
                    </a>
                    {/* L'item actuel 'Analyse de Risque' n'est pas dans l'image, nous le sautons ici */}
                </nav>

                <div className="footer-menu">
                    <div className="hospital-info">
                        <strong>Hôpital Central</strong>
                        <span>Super2 Admin2</span>
                        <span className="email">admin@viacareme.cd</span>
                        <span className="role">SUPERADMIN</span>
                    </div>
                </div>
            </div>
        );
    }
    
    // Nouveau composant pour la barre de navigation supérieure
    const TopNav = () => {
        return (
            <div className="topnav">
                <span className="topnav-title">Accueil</span>
                <div className="user-section">
                    <span className="notification-icon">🔔</span>
                    <div className="user-info">
                        Super2 Admin2
                        <span>SUPERADMIN</span>
                    </div>
                    <div className="avatar">SA</div>
                    <button className="logout-btn">
                        <i className="fas fa-sign-out-alt"></i> Déconnexion
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="LayoutContainer">
            <SideMenu />
            <div className="MainContent">
                <TopNav />
                <div className="App">
                    <h1><i className="fas fa-chart-line"></i> Analyse de Risque de Complications</h1>
                    <p className="subtitle">
                        Saisissez les données des visites séquentielles de la patiente pour prédire l'évolution du risque et obtenir des explications SHAP.
                    </p>

                    <ErrorDisplay error={error} />
                    
                    <div className="card-block">
                        <h2>Données de la Patiente</h2>
                        <form onSubmit={handleSubmit}>
                            <div className="table-responsive">
                                <table className="visits-table">
                                    <thead>
                                        <tr>
                                            <th>Visite</th>
                                            {Object.values(featureMap).map(label => (
                                                <th key={label}>{label}</th>
                                            ))}
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {visits.map((visit, index) => (
                                            <tr key={visit.id}>
                                                <td>{index + 1}</td>
                                                {Object.keys(featureMap).map(field => (
                                                    <td key={field}>
                                                        <input
                                                            type="number"
                                                            step="0.1"
                                                            value={visit[field]}
                                                            onChange={(e) => handleChange(visit.id, field, e.target.value)}
                                                            required
                                                            className="form-control"
                                                        />
                                                    </td>
                                                ))}
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>

                            <div className="action-buttons">
                                <button type="button" onClick={addVisit} className="btn add-btn" disabled={loading}>
                                    + Ajouter Visite
                                </button>
                                <button type="button" onClick={removeVisit} className="btn remove-btn" disabled={visits.length <= 1 || loading}>
                                    - Supprimer Dernière
                                </button>
                            </div>

                            <div className="submit-button-container">
                                <button type="submit" disabled={loading}>
                                    {loading ? 'Calcul en cours...' : 'Calculer le Risque'}
                                </button>
                            </div>
                        </form>
                    </div>

                    {/* Affichage des Résultats */}
                    {results && (
                        <div className="results">
                            <h2>Résultats de la Prédiction</h2>
                            
                            {/* NOUVELLE SECTION DE RÉSUMÉ */}
                            <RiskSummary predictions={results.predictions} />
                            
                            <div className="summary-and-chart">
                                <div className="chart-container card-block">
                                    <Line data={chartData} options={options} />
                                </div>
                            </div>
                            
                            <ShapExplanations results={results} />
                        </div>
                    )}
                </div>
            </div>
            
            <style>
                {/* ---------------------------------- */}
                {/* CHARTE GRAPHIQUE VIA CARE (Hôpital) */}
                {/* ---------------------------------- */}
                {`
                    :root {
                        --color-primary: #007bff; /* Bleu principal */
                        --color-secondary: #dc3545; /* Rouge Déconnexion/Danger */
                        --color-dark-blue: #003366; /* Bleu très foncé pour la sidebar */
                        --color-text-dark: #333;
                        --color-text-light: #fff;
                        --color-bg-light: #f0f2f5; /* Arrière-plan général */
                        --sidebar-width: 250px;
                    }

                    /* Configuration du Layout */
                    body {
                        font-family: 'Arial', sans-serif;
                        background-color: var(--color-bg-light);
                        margin: 0;
                        padding: 0;
                        color: var(--color-text-dark);
                        overflow: hidden; /* Empêche le scroll du body */
                    }

                    .LayoutContainer {
                        display: flex;
                        height: 100vh;
                        width: 100vw;
                    }

                    /* ---------------------------------- */
                    /* Sidebar (Menu de Gauche) */
                    /* ---------------------------------- */
                    .sidebar {
                        width: var(--sidebar-width);
                        background-color: var(--color-dark-blue);
                        color: var(--color-text-light);
                        display: flex;
                        flex-direction: column;
                        justify-content: space-between;
                        padding: 0;
                        position: fixed;
                        height: 100%;
                        left: 0;
                        top: 0;
                        z-index: 1000;
                    }

                    .logo-container {
                        padding: 20px;
                        text-align: center;
                        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                    }
                    .logo-text {
                        font-size: 1.5em;
                        font-weight: 700;
                        color: #fff;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    }
                    
                    .nav-menu {
                        flex-grow: 1;
                        padding: 20px 0;
                    }

                    .nav-item {
                        display: block;
                        padding: 15px 20px;
                        color: rgba(255, 255, 255, 0.7);
                        text-decoration: none;
                        font-size: 1em;
                        transition: background-color 0.2s, color 0.2s;
                    }
                    .nav-item:hover {
                        color: var(--color-text-light);
                        background-color: #004488;
                    }

                    .nav-item.active {
                        background-color: var(--color-primary);
                        color: var(--color-text-light);
                        font-weight: 600;
                        border-right: 5px solid white; /* Effet de sélection */
                    }
                    .nav-item i {
                        margin-right: 10px;
                    }

                    .footer-menu {
                        padding: 20px;
                        border-top: 1px solid rgba(255, 255, 255, 0.1);
                        background-color: #002244;
                        font-size: 0.9em;
                    }
                    .hospital-info {
                        display: flex;
                        flex-direction: column;
                        line-height: 1.5;
                    }
                    .hospital-info strong {
                        color: var(--color-primary);
                        font-size: 1.1em;
                    }
                    .hospital-info .email {
                        font-size: 0.8em;
                        color: rgba(255, 255, 255, 0.5);
                    }
                    .hospital-info .role {
                        font-weight: bold;
                        color: #ffc107; /* Jaune pour SUPERADMIN */
                        margin-top: 5px;
                    }


                    /* ---------------------------------- */
                    /* Contenu Principal et TopNav */
                    /* ---------------------------------- */
                    .MainContent {
                        margin-left: var(--sidebar-width); /* Décalage pour le menu fixe */
                        flex-grow: 1;
                        display: flex;
                        flex-direction: column;
                        overflow-y: auto; /* Permet le scroll du contenu central */
                        height: 100vh;
                    }

                    .topnav {
                        background-color: var(--color-text-light);
                        height: 100px;
                        padding: 0 30px;
                        display: flex;
                        align-items: center;
                        justify-content: space-between;
                        border-bottom: 1px solid #ddd;
                        position: sticky;
                        top: 0;
                        z-index: 999;min-height:80px;
                    }
                    
                    .topnav-title {
                        font-size: 1.2em;
                        font-weight: 600;
                        color: var(--color-text-dark);
                    }
                    
                    .user-section {
                        display: flex;
                        align-items: center;
                        gap: 15px;
                    }
                    
                    .notification-icon {
                        font-size: 1.4em;
                        cursor: pointer;
                        color: #666;
                    }
                    
                    .user-info {
                        display: flex;
                        flex-direction: column;
                        line-height: 1.2;
                        font-size: 0.9em;
                    }
                    .user-info span {
                        font-size: 0.8em;
                        color: var(--color-primary);
                    }
                    
                    .avatar {
                        background-color: var(--color-primary);
                        color: white;
                        width: 35px;
                        height: 35px;
                        border-radius: 50%;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-weight: bold;
                        font-size: 1em;
                    }
                    
                    .logout-btn {
                        background-color: var(--color-secondary);
                        color: white;
                        border: none;
                        padding: 8px 15px;
                        border-radius: 5px;
                        cursor: pointer;
                        font-weight: 600;
                        transition: background-color 0.2s;
                    }
                    .logout-btn:hover {
                        background-color: #c82333;
                    }
                    .logout-btn i {
                        margin-right: 5px;
                    }

                    /* ---------------------------------- */
                    /* Contenu de l'application (App) */
                    /* ---------------------------------- */
                    .App {
                        padding: 30px;
                        flex-grow: 1;
                        background-color: var(--color-bg-light);
                    }

                    /* Cartes de bloc pour l'application (pour contenir les entrées, graphique, etc.) */
                    .card-block {
                        background-color: #fff;
                        padding: 25px;
                        border-radius: 8px;
                        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
                        margin-bottom: 30px;
                    }

                    /* Titres principaux (similaire à "Gestion des hôpitaux") */
                    h1 {
                        color: var(--color-text-dark);
                        font-size: 1.8em;
                        font-weight: 700;
                        margin-top: 0;
                        margin-bottom: 10px;
                        padding-bottom: 0;
                        border-bottom: none;
                        display: flex;
                        align-items: center;
                    }
                    h1 i {
                        font-size: 1.2em;
                        color: var(--color-primary);
                        margin-right: 15px;
                    }
                    h2 {
                        font-size: 1.3em;
                        color: var(--color-primary);
                        margin-top: 0;
                        margin-bottom: 15px;
                        padding-bottom: 0;
                        font-weight: 600;
                    }
                    h3 {
                        font-size: 1.2em;
                        color: var(--color-text-dark);
                        margin-top: 0;
                        margin-bottom: 10px;
                        font-weight: 600;
                    }

                    .subtitle {
                        color: #6c757d;
                        margin-bottom: 25px;
                        font-size: 0.95em;
                    }

                    /* Boutons */
                    .action-buttons {
                        display: flex;
                        gap: 15px;
                        margin-top: 20px;
                    }
                    .action-buttons button, .submit-button-container button {
                        border: none;
                        color: white;
                        padding: 10px 15px;
                        cursor: pointer;
                        border-radius: 5px; /* Forme carrée/arrondie comme dans la charte */
                        font-weight: 600; /* Moins gras */
                        text-transform: uppercase;
                        font-size: 0.85em;
                        transition: background-color 0.2s, opacity 0.2s;
                    }

                    .action-buttons .add-btn {
                        background-color: #28a745; /* Vert pour 'Ajouter' */
                    }
                    .action-buttons .add-btn:hover:not(:disabled) {
                        background-color: #1e7e34;
                    }
                    .action-buttons .remove-btn {
                        background-color: #dc3545; /* Rouge pour 'Supprimer' */
                    }
                    .action-buttons .remove-btn:hover:not(:disabled) {
                        background-color: #c82333;
                    }
                    button:disabled {
                        opacity: 0.6;
                        cursor: not-allowed;
                    }

                    .submit-button-container {
                        margin-top: 30px;
                        text-align: right; /* Aligner le bouton à droite */
                    }
                    .submit-button-container button {
                        background-color: var(--color-primary);
                        color: white;
                        font-weight: 600;
                        padding: 10px 25px;
                        box-shadow: 0 4px 6px rgba(0, 123, 255, 0.2);
                    }
                    .submit-button-container button:hover:not(:disabled) {
                        background-color: #0056b3;
                        box-shadow: 0 6px 8px rgba(0, 123, 255, 0.3);
                    }

                    /* Tableau */
                    .table-responsive {
                        overflow-x: auto;
                    }
                    .visits-table {
                        width: 100%;
                        border-collapse: collapse;
                        font-size: 0.9em;
                    }
                    thead th {
                        background-color: #f8f9fa; /* Fond plus clair */
                        color: var(--color-text-dark);
                        font-weight: 600;
                        border-bottom: 2px solid #e9ecef;
                        padding: 12px 10px;
                        text-align: left;
                    }
                    td {
                        border-bottom: 1px solid #e9ecef;
                        padding: 10px;
                    }
                    input[type="number"] {
                        width: 100%;
                        padding: 8px;
                        border: 1px solid #ced4da;
                        border-radius: 4px;
                        text-align: center;
                        box-sizing: border-box;
                        transition: border-color 0.2s, box-shadow 0.2s;
                    }
                    input[type="number"]:focus {
                        border-color: var(--color-primary);
                        box-shadow: 0 0 5px rgba(0, 123, 255, 0.2);
                        outline: none;
                    }
                    
                    /* Messages d'erreur */
                    .error-message {
                        color: var(--color-secondary);
                        background-color: #f8d7da;
                        border: 1px solid #f5c6cb;
                        padding: 15px;
                        border-radius: 8px;
                        margin-bottom: 30px;
                        text-align: left;
                        font-size: 0.9em;
                        font-weight: 500;
                    }
                    .error-message strong {
                        color: #721c24; /* Couleur de texte plus sombre */
                    }


                    /* Résultats & Graphique (maintenir le style moderne) */
                    .results {
                        margin-top: 0;
                        padding-top: 0;
                        border-top: none;
                    }
                    
                    /* Résumé de Risque (Nouveau Styles) */
                    .risk-summary-container {
                        display: flex;
                        gap: 20px;
                        margin-bottom: 30px;
                    }
                    .summary-card {
                        background-color: #fff;
                        padding: 20px;
                        border-radius: 8px;
                        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                        flex: 1;
                        text-align: center;
                        border-left: 5px solid;
                    }
                    .summary-card h4 {
                        font-size: 1em;
                        margin-bottom: 5px;
                        font-weight: 500;
                    }
                    .summary-card .value {
                        font-size: 2em;
                        font-weight: 700;
                        margin: 0;
                        line-height: 1.2;
                    }
                    .summary-card .detail {
                        display: block;
                        font-size: 0.85em;
                        color: #6c757d;
                        margin-top: 5px;
                    }
                    
                    /* Couleurs pour le Résumé */
                    .summary-card.risk-low { border-color: #28a745; }
                    .summary-card.risk-low .value { color: #28a745; }
                    
                    .summary-card.risk-medium { border-color: #ffc107; }
                    .summary-card.risk-medium .value { color: #ffc107; }

                    .summary-card.risk-high { border-color: #dc3545; }
                    .summary-card.risk-high .value { color: #dc3545; }
                    
                    .summary-card.trend-up { border-color: #dc3545; }
                    .summary-card.trend-up .value { color: #dc3545; }

                    .summary-card.trend-down { border-color: #28a745; }
                    .summary-card.trend-down .value { color: #28a745; }
                    
                    .summary-card.trend-stable { border-color: #007bff; }
                    .summary-card.trend-stable .value { color: #007bff; }


                    /* Graphique */
                    .summary-and-chart {
                        /* Retirer le flex pour que le graphique prenne toute la largeur après le résumé */
                        display: block;
                    }
                    .chart-container {
                        height: 400px;
                        width: 100%;
                    }
                    
                    /* SHAP Explanations */
                    .shap-explanations {
                        margin-top: 30px; /* Espace après le graphique */
                    }
                    .visits-column-list {
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                        gap: 20px;
                        margin-top: 20px;
                    }

                    .visit-explanation-card {
                        padding: 20px;
                        border-radius: 8px;
                        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
                        transition: transform 0.2s;
                    }
                    .visit-explanation-card:hover {
                        transform: translateY(-2px);
                    }
                    .visit-explanation-card h4 {
                        margin-top: 0;
                        padding-bottom: 10px;
                        border-bottom: 1px solid;
                        font-size: 1.1em;
                        font-weight: 700;
                    }

                    /* Couleurs des cartes (maintenues) */
                    .risk-low {
                        background-color: #d4edda;
                        border: 2px solid #28a745; /* Vert pour faible */
                    }
                    .risk-low h4 {
                        color: #155724;
                        border-color: #28a745;
                    }

                    .risk-medium {
                        background-color: #fff3cd;
                        border: 2px solid #ffc107; /* Jaune/Orange pour moyen */
                    }
                    .risk-medium h4 {
                        color: #856404;
                        border-color: #ffc107;
                    }

                    .risk-high {
                        background-color: #f8d7da;
                        border: 2px solid #dc3545; /* Rouge pour élevé */
                    }
                    .risk-high h4 {
                        color: #721c24;
                        border-color: #dc3545;
                    }

                    .explanation-text {
                        line-height: 1.6;
                        font-size: 0.95em;
                    }
                    .explanation-text strong {
                        font-weight: 700;
                    }
                    .explanation-text br {
                        margin-top: 5px;
                    }

                    .raw-details {
                        margin-top: 15px;
                        padding-top: 10px;
                        border-top: 1px dashed #ccc;
                        font-size: 0.8em;
                        color: #6c757d;
                    }
                    .raw-details .raw-value {
                        font-weight: bold;
                        color: var(--color-text-dark);
                    }
                `}
            </style>
        </div>
    );
}

export default App;