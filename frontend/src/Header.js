import React, { useState } from 'react';


const Header = ({ isAuthenticated, handleLogout, handleDeleteAccount, setShowLoginModal }) => {
  const [showDropdown, setShowDropdown] = useState(false);

  const toggleDropdown = () => {
    setShowDropdown(!showDropdown);
  };

  return (
    <header>
      <img src="logo.png" alt="Логотип" onClick={() => window.location.reload()} />

      {isAuthenticated ? (
        <div className="dropdown">
          <button className="dropdown-toggle" onClick={toggleDropdown}>
            Профиль
          </button>
          {showDropdown && (
            <div className="dropdown-menu">
              <button className="dropdown-item">Настройки</button>
              <button className="dropdown-item" onClick={handleDeleteAccount}>
                Удалить аккаунт
              </button>
              <button className="dropdown-item" onClick={handleLogout}>
                Выйти
              </button>
            </div>
          )}
        </div>
      ) : (
        <button onClick={() => setShowLoginModal(true)}>Войти</button>
      )}
    </header>
  );
};

export default Header;