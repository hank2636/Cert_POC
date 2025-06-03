import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import "./login.css";

export default function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(false);
  const [error, setError] = useState("");
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
  const API_BACKEND_URL = import.meta.env.VITE_API_BACKEND_URL;
  useEffect(() => {
    const savedEmail = localStorage.getItem("savedEmail");
    const savedPassword = localStorage.getItem("savedPassword");
    if (savedEmail && savedPassword) {
      setEmail(savedEmail);
      setPassword(savedPassword);
      setRememberMe(true);
    }
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(""); // 清除之前的錯誤訊息

    if (rememberMe) {
      localStorage.setItem("savedEmail", email);
      localStorage.setItem("savedPassword", password);
    } else {
      localStorage.removeItem("savedEmail");
      localStorage.removeItem("savedPassword");
    }

    try {
      const response = await axios.post(
        `${API_BACKEND_URL}/api/login/access-token`,
        new URLSearchParams({
          username: email,
          password: password,
        }),
        {
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
          },
          withCredentials: true,
        }
      );
      if (response.status === 200) {
        const csrfToken = response.data.csrf_token; // 從 response 中取得 token
        localStorage.setItem('csrf_token', csrfToken);
        window.location.href = `${API_BASE_URL}/home`;
      }
    }
    catch (err) {
      if (axios.isAxiosError(err)) {
        // 如果是 Axios 的錯誤，從 err.response 拿狀態碼
        if (err.response?.status === 400) {
          setError("登入失敗 : Email 或 密碼 錯誤!");
        } else {
          setError(`登入失敗，錯誤代碼: ${err.response?.status ?? ''}`);
        }
      } else {
        setError("登入失敗，E001"); //發生非 Axios 錯誤
        }
    };
  }
  

  return (
    <div className="login-container">
      <div className="login-box">
        <h2 className="login-title">客戶登入</h2>
        <form className="space-y-4" onSubmit={handleSubmit}>
          <div className="input-group">
            <label htmlFor="email" className="input-label">Email</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="input-field"
              required
            />
          </div>

          <div className="input-group">
            <label htmlFor="password" className="input-label">密碼</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="input-field"
              required
            />
          </div>

          <div className="flex items-center justify-between">
            <label className="remember-label">
              <input
                type="checkbox"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
                className="remember-checkbox"
              />
              記住密碼
            </label>
            <button type="button" className="forgot-password-btn">
              忘記密碼？
            </button>
          </div>
          {error && (
            <div className="login-error">
              {error}
            </div>
          )}

          <button type="submit" className="btn-primary">登入</button>
          <button type="button" className="btn-secondary" onClick={() => navigate("/register")}>
            註冊
          </button>
        </form>
      </div>
    </div>
  );
}

