mapboxgl.accessToken = '';
const map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/mapbox/dark-v10',
    center: [120.9605, 23.6978],
    zoom: 7
});

const landmarks = [
    {
        coordinates: [121.3604, 23.0975],
        description: 'SANXIANTAI'
    },
    {
        coordinates: [121.1619, 23.2138],
        description: 'EAST COAST NATIONAL SCENIC AREA'
    },
    {
        coordinates: [121.2808, 23.0486],
        description: 'XIAO YELIU'
    },
    {
        coordinates: [121.2008, 22.7554],
        description: 'TAITUNG SEASIDE PARK'
    },
    {
        coordinates: [121.2142, 23.1156],
        description: 'BROWN BOULEVARD'
    }
];

landmarks.forEach(function(landmark) {
    const el = document.createElement('div');
    el.className = 'marker';

    const dot = document.createElement('div');
    dot.className = 'dot';

    const innerDot = document.createElement('div');
    innerDot.className = 'inner-dot';

    dot.appendChild(innerDot);
    el.appendChild(dot);

    const label = document.createElement('div');
    label.className = 'label';
    label.textContent = landmark.description;
    el.appendChild(label);

    new mapboxgl.Marker(el)
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
});