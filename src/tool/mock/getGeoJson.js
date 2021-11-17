function getGeoJson(net_data, locs) {
    const getLocs = code => locs[code].locs.slice().reverse()

    const lineGeoJson = {
        type: "FeatureCollection",
        features: []
    }
    features = lineGeoJson.features
    net_data.forEach(link => {
        geometry = {
            coordinates: [
                getLocs(link[0]),
                getLocs(link[1]),
            ],
            properties: {
                tradeValue: link[2],
                tradeQt: link[3],
            },
            type: "LineString"
        }
        features.push({
            type: "Featrue",
            geometry,
        })
    })
    return lineGeoJson
}
