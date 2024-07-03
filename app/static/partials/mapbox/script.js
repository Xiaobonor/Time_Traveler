// app/static/partials/mapbox/script.js
mapboxgl.accessToken = '';
const map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/xiaobocute/clxykmzy0003e01r442wq6r0o',
    center: [120.9605, 23.6978],
    zoom: 7
});

let markers = [];

function addLandmark(landmark) {
    const el = document.createElement('div');
    el.className = 'marker';

    const dot = document.createElement('div');
    dot.className = 'dot';

    const innerDot = document.createElement('div');
    innerDot.className = 'inner-dot';

    dot.appendChild(innerDot);
    el.appendChild(dot);

    const nameLabel = document.createElement('div');
    nameLabel.className = 'label';
    nameLabel.textContent = landmark.name;
    el.appendChild(nameLabel);

    const marker = new mapboxgl.Marker(el)
        .setLngLat(landmark.coordinates)
        .setPopup(new mapboxgl.Popup({ offset: 25 }).setText(landmark.description))
        .addTo(map);

    el.addEventListener('click', () => {
        map.flyTo({
            center: landmark.coordinates,
            zoom: 14,
            essential: true
        });
    });

    markers.push(marker);
}

function clearLandmarks() {
    markers.forEach(marker => marker.remove());
    markers = [];
}
//
// // 初始加載地標
// const landmarks = [
//     {
//         coordinates: [121.3604, 23.0975],
//         name: '測試1',
//         description: 'SANXIANTAI'
//     },
//     {
//         coordinates: [121.1619, 23.2138],
//         name: '測試2',
//         description: 'EAST COAST NATIONAL SCENIC AREA'
//     },
//     {
//         coordinates: [121.2808, 23.0486],
//         name: '測試3',
//         description: 'XIAO YELIU'
//     },
//     {
//         coordinates: [121.2008, 22.7554],
//         name: '測試4',
//         description: 'TAITUNG SEASIDE PARK'
//     },
//     {
//         coordinates: [121.2142, 23.1156],
//         name: '測試5',
//         description: 'BROWN BOULEVARD'
//     }
// ];
//
// landmarks.forEach(addLandmark);