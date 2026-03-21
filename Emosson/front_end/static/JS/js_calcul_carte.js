// Prend un t entre 0 et 1 et renvoie une couleur RGB quelque part dans un dégradé
// du bleu clair au bleu foncé

function degrader_bleu(t) {
    var colors = [
        [180, 214, 240],  
        [120, 170, 220],  
        [ 65, 125, 195],  
        [ 30,  85, 160],  
        [ 12,  52, 120],  
        [  5,  25,  75],  
    ];
    
    // On positionne t dans le tableau
    var scaled = t * (colors.length - 1);
    var i = Math.floor(scaled); // couleur de gauche
    var f = scaled - i;         // à quel point on est entre les deux
    
    if (i >= colors.length - 1) return colors[colors.length - 1]; // cas limite
    
    var c0 = colors[i], c1 = colors[i + 1];

    return [
        Math.round(c0[0] + f * (c1[0] - c0[0])),
        Math.round(c0[1] + f * (c1[1] - c0[1])),
        Math.round(c0[2] + f * (c1[2] - c0[2]))
    ];
}


// Fonction principale
// lat/lon = coordonnées du adresse, geomList = les polygones ZICH récupérés
function initMap(lat, lon, geomList) {
    if (lat === null || lon === null) return;
    // Init de la carte Leaflet centrée sur le logement zoom 15 
    var map = L.map('map').setView([lat, lon], 15);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap'
    }).addTo(map);

    if (geomList && geomList.length > 0) {

        // On récupère les classes de hauteur uniques 
        // en dédupliquant par une clé "hmin_hmax"
        var classesSet = {};
        geomList.forEach(function(g) {
            var key = g.hauteur_min_m + '_' + g.hauteur_max_m;
            classesSet[key] = { hmin: g.hauteur_min_m, hmax: g.hauteur_max_m };
        });
        // On trie du moins profond au plus profond
        var classes = Object.values(classesSet).sort(function(a, b) {
            return a.hmin - b.hmin;
        });

        // On attribue une couleur à chaque classe via le dégradé
        // La classe la moins profonde = bleu clair, la plus profonde = bleu foncé
        var classesCouleurs = {};
        classes.forEach(function(c, i) {
            var t = classes.length === 1 ? 0.4 : i / (classes.length - 1);
            var rgb = degrader_bleu(t);
            var key = c.hmin + '_' + c.hmax;
            classesCouleurs[key] = {
                css: 'rgb(' + rgb[0] + ',' + rgb[1] + ',' + rgb[2] + ')',
                hex: '#' + rgb.map(function(v) {
                    return v.toString(16).padStart(2, '0');
                }).join('')
            };
        });

        // On dessine chaque polygone sur la carte avec sa couleur
        geomList.forEach(function(g) {
            var key = g.hauteur_min_m + '_' + g.hauteur_max_m;
            var couleur = classesCouleurs[key] ? classesCouleurs[key].css : '#3388ff';
            L.geoJSON(g.geometry, {
                style: {
                    color:       'rgba(33, 25, 174, 0.53)', // bordure des polygones
                    weight:      1,              
                    fillColor:   couleur,
                    fillOpacity: 0.6
                }
            }).addTo(map);
        });

        // Légende en bas à droite on liste chaque classe avec sa couleur + l'icone maison
        var legend = L.control({ position: 'bottomright' });
        legend.onAdd = function () {
            var div = L.DomUtil.create('div', 'leaflet-legend');
            div.innerHTML = '<h4>Hauteur de submersion possible</h4>';

            classes.forEach(function(c) {
                var key = c.hmin + '_' + c.hmax;
                var couleur = classesCouleurs[key] ? classesCouleurs[key].css : '#3388ff';
                div.innerHTML +=
                    '<div class="legend-item">' +
                    '<div class="legend-swatch" style="background:' + couleur + ';"></div>' +
                    '<span>' + c.hmin + ' m – ' + c.hmax + ' m</span>' +
                    '</div>';
            });

            // Icône maison
            div.innerHTML +=
                '<div class="legend-marker">' +
                '<svg ...></svg>' +
                '<span>Adresse de votre logement</span>' +
                '</div>';

            return div;
        };
        legend.addTo(map);
    }

    // Icone maison
    var monIcone = L.divIcon({
        html: `<svg ...>...</svg>`,
        className: '',
        iconSize:   [28, 40],
        iconAnchor: [14, 40],  // point d'ancrage en bas au centre
        popupAnchor:[0, -40]
    });
    L.marker([lat, lon], { icon: monIcone }).addTo(map);
    setTimeout(function() { map.invalidateSize(); }, 100);
}