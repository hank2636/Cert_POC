import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import "./Register.css";
import taiwanAddress from "../components/taiwan-address.json";
import CitySelector from "../components/CitySelector";

interface TaiwanCity {
  city: string;
  districts: string[];
}

export default function Register() {
  const navigate = useNavigate();

  const [customerName, setCustomerName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [phoneNumber, setPhoneNumber] = useState("");
  const [city, setCity] = useState("");
  const [district, setDistrict] = useState("");
  const [detailAddress, setDetailAddress] = useState("");
  const [error, setError] = useState("");
  const API_BACKEND_URL = import.meta.env.VITE_API_BACKEND_URL;

  const data: TaiwanCity[] = taiwanAddress;

  // 當縣市改變時，區也重置
  const handleCityChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setCity(e.target.value);
    setDistrict(""); // 區域重置
  };

  const districts =
    data.find((item) => item.city === city)?.districts || [];

  const fullAddress = `${city}${district}${detailAddress}`;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    // 欄位必填檢查，address 改成檢查 city, district, detailAddress
    if (
      !customerName.trim() ||
      !email.trim() ||
      !password.trim() ||
      !phoneNumber.trim() ||
      !city.trim() ||
      !district.trim() ||
      !detailAddress.trim()
    ) {
      setError("所有欄位皆為必填");
      return;
    }

    if (!/^\d+$/.test(phoneNumber)) {
      setError("電話號碼只能為數字");
      return;
    }

    try {
      const response = await axios.post(
        `${API_BACKEND_URL}/api/users/`,
        {
          customer_name: customerName,
          email: email,
          password: password,
          phone_number: `8869${phoneNumber}`,
          address: fullAddress, // 用組合完整地址送出
        },
        { withCredentials: true }
      );

      if (response.status === 200) {
        navigate("/emailVerify");
      }
    } catch (err) {
      if (axios.isAxiosError(err)) {
        if (err.response?.status === 400) {
          setError("帳號已存在");
        } else {
          setError(`註冊失敗，錯誤代碼: ${err.response?.status ?? ""}`);
        }
      } else {
        setError("註冊失敗，請稍後再試");
      }
    }
  };

  return (
    <div className="register-container">
      <div className="register-box">
        <h2 className="register-title">客戶註冊</h2>
        <form className="space-y-4" onSubmit={handleSubmit}>
          <div className="input-group">
            <label className="input-label" htmlFor="customerName">姓名</label>
            <input
              id="customerName"
              type="text"
              value={customerName}
              maxLength={50}
              onChange={(e) => setCustomerName(e.target.value)}
              className="input-field"
              required
            />
          </div>

          <div className="input-group">
            <label className="input-label" htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              value={email}
              maxLength={255}
              onChange={(e) => setEmail(e.target.value)}
              className="input-field"
              required
            />
          </div>

          <div className="input-group">
            <label className="input-label" htmlFor="password">密碼</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="input-field"
              required
            />
          </div>

          <div className="input-group">
            <label className="input-label" htmlFor="phoneNumber">電話</label>
            <span style={{ color: 'black', marginRight: '0.25rem' }}>+886(09)</span>
            <input
              id="phoneNumber"
              type="text"
              value={phoneNumber}
              onChange={(e) => {
                const value = e.target.value.replace(/\D/g, ''); // 僅保留數字
                setPhoneNumber(value);
              }}
              className="input-field"
              maxLength={8}
              required
            />
          </div>

          <div className="input-group">
            <label className="input-label">縣市</label>
            <CitySelector
              options={data.map((item) => item.city)}
              value={city}
              onChange={(selectedCity) => {
                setCity(selectedCity);
                setDistrict("");
              }}
              placeholder="請選擇縣市"
            />
          </div>

          <div className="input-group">
            <label className="input-label">區鄉鎮</label>
            <CitySelector
              options={districts}
              value={district}
              onChange={setDistrict}
              disabled={!city}
              placeholder="請選擇區鄉鎮"
            />
          </div>

          <div className="input-group">
            <label className="input-label" htmlFor="detailAddress">詳細地址</label>
            <input
              id="detailAddress"
              type="text"
              value={detailAddress}
              onChange={(e) => setDetailAddress(e.target.value)}
              className="input-field"
              required
            />
          </div>

          {error && <div className="register-error">{error}</div>}
          <button type="submit" className="btn-primary">註冊</button>
          <button
            type="button"
            className="btn-secondary"
            onClick={() => navigate("/login")}
          >
            返回登入
          </button>
        </form>
      </div>
    </div>
  );
}
