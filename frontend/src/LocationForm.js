import React, { useState } from 'react';
import axios from 'axios';

const LocationForm = ({ handleAddLocationSubmit, setShowAddLocationForm }) => {
  const [showOwnerForm, setShowOwnerForm] = useState(false);
  const [ownerData, setOwnerData] = useState({
    website: '',
    owner_info: ''
  });
  const [errors, setErrors] = useState(null); // Для хранения ошибок

  // Обработчик изменения формы владельца
  const handleOwnerChange = (e) => {
    setOwnerData({
      ...ownerData,
      [e.target.name]: e.target.value
    });
  };

  // Обработчик отправки формы владельца
  const handleOwnerSubmit = async () => {
    try {
      const response = await axios.post('http://127.0.0.1:8000/owner-info', ownerData, {
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('authToken')}` // Добавляем токен для аутентификации
        }
      });

      alert('Информация о владельце успешно отправлена!');
      setShowOwnerForm(false);
    } catch (error) {
      if (error.response && error.response.data.detail) {
        setErrors(error.response.data.detail); // Устанавливаем ошибки
      } else {
        console.error('Ошибка при отправке информации о владельце:', error);
        setErrors(['Произошла ошибка при отправке информации.']);
      }
    }
  };

  return (
    <div className="modal">
      <div className="modal-content">
        <h3>Добавить новую локацию</h3>
        <form onSubmit={handleAddLocationSubmit}>
          <div className="form-group">
            <label htmlFor="name">Название локации</label>
            <input type="text" name="name" id="name" placeholder="Введите название" required />
          </div>
          <div className="form-group">
            <label htmlFor="address">Адрес</label>
            <input type="text" name="address" id="address" placeholder="Введите адрес" required />
          </div>
          <div className="form-group">
            <label htmlFor="working_hours_start">Начало работы</label>
            <input type="text" name="working_hours_start" id="working_hours_start" placeholder="09:00" required />
          </div>
          <div className="form-group">
            <label htmlFor="working_hours_end">Конец работы</label>
            <input type="text" name="working_hours_end" id="working_hours_end" placeholder="18:00" required />
          </div>
          <div className="form-group">
            <label htmlFor="average_check">Средний чек (2000-5000)</label>
            <input type="number" name="average_check" id="average_check" placeholder="Введите средний чек" required min="2000" max="5000" />
          </div>

          {/* Кнопка для показа формы владельца */}
          <button type="button" className="btn-secondary" onClick={() => setShowOwnerForm(!showOwnerForm)}>
            {showOwnerForm ? 'Скрыть форму владельца' : 'Я владелец'}
          </button>

          {showOwnerForm && (
            <div className="owner-form">
              <h4>Информация о владельце</h4>
              <div className="form-group">
                <label htmlFor="website">Вебсайт</label>
                <input
                  type="text"
                  name="website"
                  id="website"
                  placeholder="Введите вебсайт"
                  value={ownerData.website}
                  onChange={handleOwnerChange}
                />
              </div>
              <div className="form-group">
                <label htmlFor="owner_info">Информация о владельце</label>
                <textarea
                  name="owner_info"
                  id="owner_info"
                  placeholder="Введите информацию о себе"
                  required
                  value={ownerData.owner_info}
                  onChange={handleOwnerChange}
                />
              </div>

              {/* Кнопка для отправки данных о владельце */}
              <button type="button" className="btn-primary" onClick={handleOwnerSubmit}>
                Отправить информацию о владельце
              </button>
            </div>
          )}

          {/* Кнопки для завершения добавления */}
          <button type="submit" className="btn-primary">Добавить локацию</button>
          <button type="button" className="btn-secondary" onClick={() => setShowAddLocationForm(false)}>Отмена</button>

          {/* Вывод ошибок валидации */}
          {errors && (
            <div className="error-messages">
              {errors.map((error, index) => (
                <p key={index} style={{ color: 'red' }}>{error}</p>
              ))}
            </div>
          )}
        </form>
      </div>
    </div>
  );
};

export default LocationForm;