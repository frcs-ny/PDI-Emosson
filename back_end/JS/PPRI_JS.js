async function checkPPRI(lon, lat) {
    console.log('Latitude :', lat);
    console.log('Longitude :', lon);

    proj4.defs("EPSG:2154", "+proj=lcc +lat_1=49 +lat_2=44 +lat_0=46.5 +lon_0=3 +x_0=700000 +y_0=6600000 +ellps=GRS80 +units=m +no_defs");
    const [x, y] = proj4("EPSG:4326", "EPSG:2154", [lon, lat]);
    console.log("X (Lambert 93) :", x);
    console.log("Y (Lambert 93) :", y);

    const point = turf.point([x, y]);

    const response = await fetch('back_end/Données-PPR/ppri_hauteur_val_de_tours.geojson');
    const geojson = await response.json();
    console.log('GeoJSON chargé');

    let isInside = false;
    let hauteur_min = null;
    let hauteur_max = null;

    geojson.features.forEach(feature => {
        if (feature.geometry.type === "Polygon" || feature.geometry.type === "MultiPolygon") {
            if (turf.booleanPointInPolygon(point, feature)) {
                isInside = true;
                hauteur_min = feature.properties.haut_min;
                hauteur_max = feature.properties.haut_max;
            }
        }
    });

    console.log('Dans une zone PPRI :', isInside);
    console.log('hauteur minimum :', hauteur_min);
    console.log('hauteur maximum :', hauteur_max);

    document.getElementById("result1").textContent =
        'Dans une zone PPRI : ' + isInside;
    document.getElementById("result2").textContent =
        'hauteur minimum : ' + hauteur_min + "m";
    document.getElementById("result3").textContent =
        'hauteur maximum : '+ hauteur_max +'m'; 


    // CARTE

    function convertGeojsonToWGS84(geojson) {
        const clone = JSON.parse(JSON.stringify(geojson));
        clone.features.forEach(feature => {
            convertCoords(feature.geometry);
        });
        return clone;
    }

    function convertCoords(geometry) {
        if (geometry.type === "Polygon") {
            geometry.coordinates = geometry.coordinates.map(ring =>
                ring.map(coord => proj4("EPSG:2154", "EPSG:4326", coord))
            );
        } else if (geometry.type === "MultiPolygon") {
            geometry.coordinates = geometry.coordinates.map(polygon =>
                polygon.map(ring =>
                    ring.map(coord => proj4("EPSG:2154", "EPSG:4326", coord))
                )
            );
        }
    }

    const map = L.map('map').setView([lat, lon], 14);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap'
    }).addTo(map);

    const geojsonWGS84 = convertGeojsonToWGS84(geojson);

    L.geoJSON(geojsonWGS84, {
        style: function(feature) {
            return {
                color: '#0077cc',
                weight: 1,
                fillOpacity: 0.3,
                fillColor: '#00b4d8'
            };
        }
    }).addTo(map);

    L.circleMarker([lat, lon], {
        radius: 10,
        color: isInside ? 'red' : 'green',
        fillColor: isInside ? 'red' : 'green',
        fillOpacity: 0.9,
        weight: 2
    })
    .bindPopup(`
        <strong>${isInside ? '📍 DANS une zone PPRI' : '📍 Hors zone PPRI'}</strong><br>
        Lat : ${lat}<br>
        Lon : ${lon}<br>
        ${hauteur_min !== null ? `Hauteur min : ${hauteur_min} m<br>` : ''}
        ${hauteur_max !== null ? `Hauteur max : ${hauteur_max} m` : ''}
    `)
    .addTo(map)
    .openPopup();

    
    
}

// checkPPRI(0.657551, 47.388068);

