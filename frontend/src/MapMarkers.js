import React from 'react';
import { Marker } from '@react-google-maps/api';

const MapMarkers = ({ locations }) => {
  return (
    <>
      {locations.map((location) => (
        <Marker
          key={location.id}
          position={{ lat: location.latitude, lng: location.longitude }}
          title={location.name}
        />
      ))}
    </>
  );
};

export default MapMarkers;