import { useMemo } from "react";
import { MapContainer, TileLayer, GeoJSON } from "react-leaflet";
import type { Feature, FeatureCollection, Geometry } from "geojson";
import type { Layer } from "leaflet";

interface RegionProps {
  sgg_code?: string;
  SIG_CD?: string;
  region_name?: string;
  [key: string]: unknown;
}

interface Props {
  geojson: FeatureCollection<Geometry, RegionProps>;
  sggToRegionId: Map<string, number>;
  selectedRegionId: number | null;
  onSelect: (regionId: number) => void;
}

const SEOUL_CENTER: [number, number] = [37.5665, 126.978];

function sggOf(props: RegionProps): string | undefined {
  return props.sgg_code ?? props.SIG_CD;
}

export function MapView({ geojson, sggToRegionId, selectedRegionId, onSelect }: Props) {
  // selectedRegionId가 바뀔 때 GeoJSON 레이어를 다시 그리도록 key 생성
  const layerKey = useMemo(() => `gj-${selectedRegionId ?? "none"}`, [selectedRegionId]);

  function styleFeature(feature?: Feature<Geometry, RegionProps>) {
    const sgg = feature ? sggOf(feature.properties) : undefined;
    const regionId = sgg ? sggToRegionId.get(sgg) : undefined;
    const selected = regionId != null && regionId === selectedRegionId;
    return {
      color: "#555",
      weight: 1,
      fillColor: selected ? "#2563eb" : "#cbd5e1",
      fillOpacity: selected ? 0.6 : 0.35,
    };
  }

  function onEachFeature(feature: Feature<Geometry, RegionProps>, layer: Layer) {
    layer.on("click", () => {
      const sgg = sggOf(feature.properties);
      const regionId = sgg ? sggToRegionId.get(sgg) : undefined;
      if (regionId != null) onSelect(regionId);
    });
  }

  return (
    <MapContainer
      center={SEOUL_CENTER}
      zoom={11}
      style={{ height: "100%", width: "100%" }}
    >
      <TileLayer
        attribution='&copy; OpenStreetMap'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <GeoJSON
        key={layerKey}
        data={geojson}
        style={styleFeature}
        onEachFeature={onEachFeature}
      />
    </MapContainer>
  );
}
