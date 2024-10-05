import React, { useEffect, useState } from 'react';
import { GoogleMap, useLoadScript } from '@react-google-maps/api';
import axios from 'axios';
import LocationForm from './LocationForm';
import MapControls from './MapControls';
import MapMarkers from './MapMarkers';

const Map = ({ isAuthenticated, setShowRegistrationModal }) => {
  const [locations, setLocations] = useState([]);
  const [map, setMap] = useState(null);
  const [showAddLocationForm, setShowAddLocationForm] = useState(false);
  const [clickedPosition, setClickedPosition] = useState(null);

  const { isLoaded } = useLoadScript({
    googleMapsApiKey: process.env.REACT_APP_GOOGLE_MAPS_API_KEY,
  });

  const token = localStorage.getItem('authToken'); // Извлекаем токен

  // Функция для определения местоположения
  const locateMe = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const pos = {
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          };
          map.panTo(pos);
          map.setZoom(12);
        },
        () => {
          alert('Не удалось определить местоположение.');
        }
      );
    } else {
      alert('Ваш браузер не поддерживает геолокацию.');
    }
  };

  // Функции для зума
  const zoomIn = () => {
    if (map) {
      map.setZoom(map.getZoom() + 1);
    }
  };

  const zoomOut = () => {
    if (map) {
      map.setZoom(map.getZoom() - 1);
    }
  };

  // Загружаем локации с бэкенда
  useEffect(() => {
    const fetchLocations = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:8000/locations', {
          headers: {
            Authorization: `Bearer ${token}`, // Добавляем токен в заголовок
          },
        });
        setLocations(response.data);
      } catch (error) {
        console.error('Ошибка при загрузке локаций:', error);
      }
    };

    fetchLocations();
  }, [token]);

  // Обработчик клика на карте
  const handleMapClick = (event) => {
    if (isAuthenticated) {
      setClickedPosition({
        lat: event.latLng.lat(),
        lng: event.latLng.lng(),
      });
      setShowAddLocationForm(true);
    } else {
      alert('Только авторизованные пользователи могут добавлять локации.');
    }
  };

  // Функция для отправки формы добавления локации
  const handleAddLocationSubmit = async (event) => {
    event.preventDefault();
    const formData = new FormData(event.target);
    const name = formData.get('name');
    const address = formData.get('address');
    const working_hours_start = formData.get('working_hours_start');
    const working_hours_end = formData.get('working_hours_end');
    const average_check = formData.get('average_check');

    try {
      await axios.post(
        'http://127.0.0.1:8000/locations',
        {
          name,
          address,
          working_hours_start,
          working_hours_end,
          average_check,
          latitude: clickedPosition.lat,
          longitude: clickedPosition.lng,
          created_at: new Date().toISOString(),
        },
        {
          headers: {
            Authorization: `Bearer ${token}`, // Добавляем токен в заголовок
            'Content-Type': 'application/json',
          },
        }
      );

      setShowAddLocationForm(false);
      alert('Локация успешно добавлена!');
    } catch (error) {
      console.error('Ошибка при добавлении локации:', error);
    }
  };

  if (!isLoaded) return <div>Загрузка карты...</div>;

  const mapOptions = {
    zoom: 12,
    center: { lat: 51.1657, lng: 10.4515 },
    disableDefaultUI: true,
    zoomControl: false,
    mapTypeControl: false,
    fullscreenControl: false,
    streetViewControl: false,
  };

  return (
    <div style={{ position: 'relative' }}>
      <GoogleMap
        options={mapOptions}
        mapContainerStyle={{ width: '100%', height: '100vh' }}
        onLoad={(mapInstance) => setMap(mapInstance)}
        onClick={handleMapClick}
      >
        {/* Маркеры локаций */}
        <MapMarkers locations={locations} />
      </GoogleMap>

      {/* Управление картой */}
      <MapControls locateMe={locateMe} zoomIn={zoomIn} zoomOut={zoomOut} />

      {/* Форма добавления локации */}
      {showAddLocationForm && (
        <LocationForm
          handleAddLocationSubmit={handleAddLocationSubmit}
          setShowAddLocationForm={setShowAddLocationForm}
        />
      )}
    </div>
  );
};

export default Map;