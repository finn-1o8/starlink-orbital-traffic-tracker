/**
 * Cesium Globe Component
 * Main 3D visualization of satellites and Earth
 */
import { useEffect, useRef } from 'react';
import * as Cesium from 'cesium';
import { satelliteApi } from '../services/api';
import type { SatellitePosition, OrbitPath } from '../types';
import 'cesium/Build/Cesium/Widgets/widgets.css';

interface GlobeProps {
  positions: SatellitePosition[];
  selectedSatellite: number | null;
  showOrbit: boolean;
  onSatelliteClick: (noradId: number) => void;
}

const hasIonToken = Boolean(import.meta.env.VITE_CESIUM_ION_TOKEN);

function Globe({ positions, selectedSatellite, showOrbit, onSatelliteClick }: GlobeProps) {
  const cesiumContainer = useRef<HTMLDivElement>(null);
  const viewerRef = useRef<Cesium.Viewer | null>(null);
  const satelliteEntitiesRef = useRef<Map<number, Cesium.Entity>>(new Map());
  const orbitEntityRef = useRef<Cesium.Entity | null>(null);

  // Initialize Cesium Viewer
  useEffect(() => {
    if (!cesiumContainer.current || viewerRef.current) return;

    const viewer = new Cesium.Viewer(cesiumContainer.current, {
      // World terrain and Bing imagery need a Cesium ion token. Without one we fall back to
      // OpenStreetMap tiles on a plain ellipsoid so the app still works out of the box.
      terrain: hasIonToken ? Cesium.Terrain.fromWorldTerrain() : undefined,
      baseLayer: hasIonToken
        ? undefined
        : new Cesium.ImageryLayer(
            new Cesium.OpenStreetMapImageryProvider({ url: 'https://tile.openstreetmap.org/' })
          ),
      baseLayerPicker: false,
      geocoder: false,
      homeButton: true,
      sceneModePicker: false,
      timeline: false,
      navigationHelpButton: false,
      animation: false,
      scene3DOnly: true,
    });

    viewer.camera.setView({
      destination: Cesium.Cartesian3.fromDegrees(-74.006, 40.7128, 15000000),
      orientation: { heading: 0, pitch: -Math.PI / 2, roll: 0 },
    });

    viewer.scene.globe.enableLighting = true;
    viewer.clock.shouldAnimate = true;
    viewer.clock.multiplier = 1;

    const handler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas);
    handler.setInputAction((click: Cesium.ScreenSpaceEventHandler.PositionedEvent) => {
      const picked = viewer.scene.pick(click.position);
      const entity = picked?.id as Cesium.Entity | undefined;
      const noradId = entity?.properties?.norad_id?.getValue() as number | undefined;
      if (noradId) {
        onSatelliteClick(noradId);
      }
    }, Cesium.ScreenSpaceEventType.LEFT_CLICK);

    viewerRef.current = viewer;
    const entities = satelliteEntitiesRef.current;

    return () => {
      if (!handler.isDestroyed()) handler.destroy();
      if (!viewer.isDestroyed()) viewer.destroy();
      viewerRef.current = null;
      entities.clear();
      orbitEntityRef.current = null;
    };
    // The viewer is created once; the click handler reads the latest callback through the closure below.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Update satellite positions
  useEffect(() => {
    const viewer = viewerRef.current;
    if (!viewer || positions.length === 0) return;

    const currentNoradIds = new Set(positions.map((p) => p.norad_id));
    for (const [noradId, entity] of satelliteEntitiesRef.current.entries()) {
      if (!currentNoradIds.has(noradId)) {
        viewer.entities.remove(entity);
        satelliteEntitiesRef.current.delete(noradId);
      }
    }

    positions.forEach((sat) => {
      const cartesian = Cesium.Cartesian3.fromDegrees(sat.lon, sat.lat, sat.alt_km * 1000);
      const color = getColorByAltitude(sat.alt_km);
      const isSelected = sat.norad_id === selectedSatellite;
      const pixelSize = isSelected ? 10 : 6;
      let entity = satelliteEntitiesRef.current.get(sat.norad_id);

      if (entity) {
        entity.position = new Cesium.ConstantPositionProperty(cartesian);
        if (entity.point) {
          entity.point.pixelSize = new Cesium.ConstantProperty(pixelSize);
          entity.point.color = new Cesium.ConstantProperty(color);
        }
      } else {
        entity = viewer.entities.add({
          id: `sat-${sat.norad_id}`,
          position: cartesian,
          point: {
            pixelSize,
            color,
            outlineColor: Cesium.Color.WHITE,
            outlineWidth: 1,
            scaleByDistance: new Cesium.NearFarScalar(1.5e6, 2.0, 8.0e6, 0.5),
            heightReference: Cesium.HeightReference.NONE,
          },
          label: {
            text: sat.name,
            font: '12px Inter',
            fillColor: Cesium.Color.WHITE,
            outlineColor: Cesium.Color.BLACK,
            outlineWidth: 2,
            style: Cesium.LabelStyle.FILL_AND_OUTLINE,
            verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
            pixelOffset: new Cesium.Cartesian2(0, -12),
            show: isSelected,
            distanceDisplayCondition: new Cesium.DistanceDisplayCondition(0, 5000000),
          },
          properties: {
            norad_id: sat.norad_id,
            name: sat.name,
            altitude: sat.alt_km,
            velocity: sat.velocity_km_s,
          },
        });
        satelliteEntitiesRef.current.set(sat.norad_id, entity);
      }

      if (entity.label) {
        entity.label.show = new Cesium.ConstantProperty(isSelected);
      }
    });
  }, [positions, selectedSatellite]);

  // Handle orbit visualization
  useEffect(() => {
    const viewer = viewerRef.current;
    if (!viewer) return;

    if (orbitEntityRef.current) {
      viewer.entities.remove(orbitEntityRef.current);
      orbitEntityRef.current = null;
    }

    if (showOrbit && selectedSatellite) {
      satelliteApi
        .getOrbit(selectedSatellite, 90)
        .then((orbitData: OrbitPath) => {
          if (!viewerRef.current) return;
          const orbitPositions = orbitData.orbit_points.map((point) =>
            Cesium.Cartesian3.fromDegrees(point.lon, point.lat, point.alt_km * 1000)
          );
          orbitEntityRef.current = viewer.entities.add({
            id: `orbit-${selectedSatellite}`,
            polyline: {
              positions: orbitPositions,
              width: 2,
              material: Cesium.Color.CYAN.withAlpha(0.6),
            },
          });
        })
        .catch((error: unknown) => {
          if (import.meta.env.DEV) {
            console.error('Failed to load orbit:', error);
          }
        });
    }
  }, [selectedSatellite, showOrbit]);

  return <div ref={cesiumContainer} className="w-full h-full" />;
}

/**
 * Get color based on altitude band
 */
function getColorByAltitude(altKm: number) {
  if (altKm < 400) return Cesium.Color.RED;
  if (altKm < 600) return Cesium.Color.CYAN;
  if (altKm < 1400) return Cesium.Color.YELLOW;
  return Cesium.Color.GRAY;
}

export default Globe;
