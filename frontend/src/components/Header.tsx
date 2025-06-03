import { Link, useNavigate } from "react-router-dom";
import { useEffect, useState, useRef } from "react";
import { useLocation } from 'react-router-dom';
import axios from "axios";
import "./Header.css";

const Header = () => {
  const [user, setUser] = useState(null);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownTimeout = useRef(null);
  const navigate = useNavigate();
  const location = useLocation();
  const API_BACKEND_URL = import.meta.env.VITE_API_BACKEND_URL;

const apiClient = axios.create({
  baseURL: API_BACKEND_URL,
  withCredentials: true,
  });

useEffect(() => {
  const localUserStr = localStorage.getItem("user");
  if (localUserStr) {
    try {
      const localUser = JSON.parse(localUserStr);
      if (localUser.activate === true) {
        setUser(localUser);
        return; // 不呼叫 API，直接返回
      }
    } catch (e) {
      console.error("解析 localStorage user 失敗", e);
      // 若解析失敗，繼續呼叫 API
    }
  }

  // 沒有 user 或 activate !== true，呼叫 API
  apiClient
    .get('/api/users/me', {
      headers: { 'X-CSRF-Token': localStorage.getItem('csrf_token') },
    })
    .then((res) => {
      setUser(res.data);
      localStorage.setItem("user", JSON.stringify(res.data)); // 存入 localStorage
    })
    .catch(() => {
      setUser(null);
      localStorage.removeItem("user"); // 錯誤時清除
    });
}, [location.pathname]);


  const handleLogout = async () => {
  try {
    await apiClient.post(`/api/logout/`, { withCredentials: true });
    
    // 清除前端非 HttpOnly 的 csrf_token cookie
    document.cookie = "csrf_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/";
    localStorage.removeItem("user");
    localStorage.removeItem("csrf_token");
    setUser(null);
    navigate("/home");
  } catch (err) {
    console.error("登出失敗", err);
  }
  };

  const handleMouseEnter = () => {
    clearTimeout(dropdownTimeout.current);
    setDropdownOpen(true);
  };

  const handleMouseLeave = () => {
    dropdownTimeout.current = setTimeout(() => {
      setDropdownOpen(false);
    }, 200); // 延遲 200ms 關閉選單
  };

  return (
    <header className="bg-white shadow">
      <div className="max-w-7xl mx-auto px-4 py-4 flex flex-col sm:flex-row sm:items-center">
        {/* 左側 Logo + 導覽列 */}
        <div className="flex items-center space-x-12">
          <Link to="/home">
            <img src="/omniwaresoft-logo.jpg" alt="Logo" className="w-40 h-auto" />
          </Link>
          <nav className="flex flex-col sm:flex-row items-start sm:items-center space-y-2 sm:space-y-0 sm:space-x-4">
            <Link to="/home" className="text-gray-700 hover:text-yellow-600">首頁</Link>
            <Link to="/production" className="text-gray-700 hover:text-yellow-600">證照資訊</Link>
            <Link to="/contact" className="text-gray-700 hover:text-yellow-600">聯絡我們</Link>
          </nav>
        </div>

        {/* 右側：登入、登出、購物車等 */}
        <div className="flex justify-center sm:justify-end items-center space-x-4 mt-4 sm:mt-0 sm:ml-auto">
          {user ? (
            <>
              <Link to="/cart" className="relative text-2xl text-gray-700 hover:text-blue-600">
                🛒<span className="absolute -top-1 -right-2 bg-red-500 text-white text-xs px-1 rounded-full">3</span>
              </Link>
              <Link to="/user" className="user-center">
                <img src="/user_logo.svg" alt="User" className="user-logo" />
                <span className="user-tooltip">使用者中心</span>
              </Link>
              <button onClick={handleLogout} className="logout-button">
                登出
              </button>
            </>
          ) : (
            <div
              className="relative"
              onMouseEnter={handleMouseEnter}
              onMouseLeave={handleMouseLeave}
            >
              <div className="login-dropdown">
                <div className="login-button">
                  登入 ▾
                </div>
                <div className="dropdown-menu">
                  <Link to="/login" className="dropdown-item">登入</Link>
                  <Link to="/register" className="dropdown-item">註冊</Link>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;
