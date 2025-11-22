/**
 * Cesium Globe Component
 * Main 3D visualization of satellites and Earth
 */
import { useEffect, useRef, useState } from 'react';
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

function Globe({ positions, selectedSatellite, showOrbit, onSatelliteClick }: GlobeProps) {
  const cesiumContainer = useRef<HTMLDivElement>(null);
  const viewerRef = useRef<Cesium.Viewer | null>(null);
  const satelliteEntitiesRef = useRef<Map<number, any>>(new Map());
  const orbitEntityRef = useRef<any>(null);
  const [enableRotation, setEnableRotation] = useState(false);

  // Initialize Cesium Viewer
  useEffect(() => {
    if (!cesiumContainer.current || viewerRef.current) return;

    const viewer = new Cesium.Viewer(cesiumContainer.current, {
      terrainProvider: Cesium.createWorldTerrain ? Cesium.createWorldTerrain() : undefined,
      baseLayerPicker: false,
      geocoder: false,
      homeButton: true,
      sceneModePicker: false,
      timeline: false,
      navigationHelpButton: false,
      animation: false,
      scene3DOnly: true,
    });

    // Set initial camera position (above Earth)
    viewer.camera.setView({
      destination: Cesium.Cartesian3.fromDegrees(-74.0060, 40.7128, 15000000),
      orientation: {
        heading: 0,
        pitch: -Math.PI / 2,
        roll: 0,
      },
    });

    // Enable lighting
    viewer.scene.globe.enableLighting = true;

    // Enable real-time clock animation for smooth satellite movement
    viewer.clock.shouldAnimate = true;
    viewer.clock.multiplier = 1; // Real-time speed


    // Handle click events
    const handler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas);
    handler.setInputAction((click: any) => {
      const pickedObject = viewer.scene.pick(click.position);
      if (pickedObject && pickedObject.id && pickedObject.id.properties) {
        const noradId = pickedObject.id.properties.norad_id?.getValue();
        if (noradId) {
          onSatelliteClick(noradId);
        }
      }
    }, Cesium.ScreenSpaceEventType.LEFT_CLICK);

    viewerRef.current = viewer;

    return () => {
      if (handler && !handler.isDestroyed()) {
        handler.destroy();
      }
      if (viewer && !viewer.isDestroyed()) {
        viewer.destroy();
      }
      viewerRef.current = null;
    };
  }, []);

  // Update satellite positions
  useEffect(() => {
    const viewer = viewerRef.current;
    
    if (!viewer || positions.length === 0) {
      return;
    }

    // Remove satellites that no longer exist
    const currentNoradIds = new Set(positions.map(p => p.norad_id));
    for (const [noradId, entity] of satelliteEntitiesRef.current.entries()) {
      if (!currentNoradIds.has(noradId)) {
        viewer.entities.remove(entity);
        satelliteEntitiesRef.current.delete(noradId);
      }
    }

    // Add or update satellites
    positions.forEach(sat => {
      let entity = satelliteEntitiesRef.current.get(sat.norad_id);
      
      const color = getColorByAltitude(sat.alt_km);
      const isSelected = sat.norad_id === selectedSatellite;
      const pixelSize = isSelected ? 10 : 6;

      if (entity) {
        // Direct position update - simple and reliable
        entity.position = Cesium.Cartesian3.fromDegrees(sat.lon, sat.lat, sat.alt_km * 1000);
        entity.show = true;
        
        if (entity.point) {
          entity.point.pixelSize = pixelSize;
          entity.point.color = color;
          entity.point.show = true;
        }
      } else {
        // Create new entity
        const cartesian = Cesium.Cartesian3.fromDegrees(sat.lon, sat.lat, sat.alt_km * 1000);
        
        entity = viewer.entities.add({
          id: `sat-${sat.norad_id}`,
          position: cartesian,
          show: true,
          point: {
            pixelSize: pixelSize,
            color: color,
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

      // Show/hide label based on selection
      if (entity.label) {
        entity.label.show = isSelected;
      }
    });
  }, [positions, selectedSatellite]);

  // Handle orbit visualization
  useEffect(() => {
    const viewer = viewerRef.current;
    if (!viewer) return;

    // Remove previous orbit
    if (orbitEntityRef.current) {
      viewer.entities.remove(orbitEntityRef.current);
      orbitEntityRef.current = null;
    }

    // Show new orbit if requested
    if (showOrbit && selectedSatellite) {
      satelliteApi.getOrbit(selectedSatellite, 90)
        .then((orbitData: OrbitPath) => {
          if (!viewer || !viewerRef.current) return;

          const positions = orbitData.orbit_points.map(point =>
            Cesium.Cartesian3.fromDegrees(point.lon, point.lat, point.alt_km * 1000)
          );

          const entity = viewer.entities.add({
            id: `orbit-${selectedSatellite}`,
            polyline: {
              positions: positions,
              width: 2,
              material: Cesium.Color.CYAN.withAlpha(0.6),
            },
          });

          orbitEntityRef.current = entity;
        })
        .catch(error => {
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


