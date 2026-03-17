function blueGradient(t) {
    var colors = [
        [180, 214, 240],  
        [120, 170, 220],  
        [ 65, 125, 195],  
        [ 30,  85, 160],  
        [ 12,  52, 120],  
        [  5,  25,  75],  
    ];
    var scaled = t * (colors.length - 1);
    var i = Math.floor(scaled);
    var f = scaled - i;
    if (i >= colors.length - 1) return colors[colors.length - 1];
    var c0 = colors[i], c1 = colors[i + 1];
    return [
        Math.round(c0[0] + f * (c1[0] - c0[0])),
        Math.round(c0[1] + f * (c1[1] - c0[1])),
        Math.round(c0[2] + f * (c1[2] - c0[2]))
    ];
}

function initMap(lat, lon, geomList) {
    var map = L.map('map').setView([lat, lon], 15);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap'
    }).addTo(map);

    if (geomList && geomList.length > 0) {

        var classesSet = {};
        geomList.forEach(function(g) {
            var key = g.hauteur_min_m + '_' + g.hauteur_max_m;
            classesSet[key] = { hmin: g.hauteur_min_m, hmax: g.hauteur_max_m };
        });
        var classes = Object.values(classesSet).sort(function(a, b) {
            return a.hmin - b.hmin;
        });

        var classesCouleurs = {};
        classes.forEach(function(c, i) {
            var t = classes.length === 1 ? 0.4 : i / (classes.length - 1);
            var rgb = blueGradient(t);
            var key = c.hmin + '_' + c.hmax;
            classesCouleurs[key] = {
                css: 'rgb(' + rgb[0] + ',' + rgb[1] + ',' + rgb[2] + ')',
                hex: '#' + rgb.map(function(v) {
                    return v.toString(16).padStart(2, '0');
                }).join('')
            };
        });

        geomList.forEach(function(g) {
            var key = g.hauteur_min_m + '_' + g.hauteur_max_m;
            var couleur = classesCouleurs[key] ? classesCouleurs[key].css : '#3388ff';
            L.geoJSON(g.geometry, {
            style: {
                color:       'rgba(33, 25, 174, 0.53)', 
                weight:      1,              
                fillColor:   couleur,
                fillOpacity: 0.3
            }
        }).addTo(map);
        });

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

            div.innerHTML +=
                '<div class="legend-marker">' +
                '<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 32 32"><circle fill="#255585" cx="16" cy="16" r="16"/><path fill="white" d="M16 7L7 15h3v9h6v-6h4v6h2v-9h3z"/></svg>' +
                '<span>Adresse de votre logement</span>' +
                '</div>';

            return div;
        };
        legend.addTo(map);
    }

    var monIcone = L.divIcon({
        html: `<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32">
        <circle fill="#255585" cx="16" cy="16" r="16"/>
        <path fill="white" d="M16 7L7 15h3v9h6v-6h4v6h2v-9h3z"/></svg>`,
        className: '',
        iconSize:   [28, 40],
        iconAnchor: [14, 40],
        popupAnchor:[0, -40]
    });
    L.marker([lat, lon], { icon: monIcone }).addTo(map);

    setTimeout(function() { map.invalidateSize(); }, 100);
}

