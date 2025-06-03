import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './Cart.css';

interface OrderItem {
  id: number;
  license_id: string;
  license_name: string;
  quantity: number;
  price_at_order_time: number;
  created_by: string;
  created_date: string;
}

interface Cart {
  order_id: number;
  customer_id: string;
  customer_name: string;
  status: boolean;
  total_amount: number;
  comment: string;
  items: OrderItem[];
}

interface NewItem {
  license_id: string;
  license_name: string;
  quantity: number;
  price_at_order_time: number;
  created_by: string;
}

interface User {
  customer_id: string;
  customer_name: string;
}

const API_BACKEND_URL = import.meta.env.VITE_API_BACKEND_URL;

const apiClient = axios.create({
  baseURL: API_BACKEND_URL,
  withCredentials: true,
});

const CartComponent: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [cart, setCart] = useState<Cart | null>(null);
  const [newItem, setNewItem] = useState<NewItem>({
    license_id: '',
    license_name: '',
    quantity: 1,
    price_at_order_time: 0,
    created_by: '',
  });

  // 取得使用者資訊
  useEffect(() => {
    setLoading(true);
    apiClient
      .get<User>('/api/users/me', {
        headers: { 'X-CSRF-Token': localStorage.getItem('csrf_token') || '' },
      })
      .then((res) => {
        setUser(res.data);
        setNewItem((prev) => ({ ...prev, created_by: res.data.customer_name }));
        localStorage.setItem('user', JSON.stringify(res.data));
        setError(null);
      })
      .catch(() => {
        setUser(null);
        localStorage.removeItem('user');
        setError('請先登入以使用購物車');
      })
      .finally(() => setLoading(false));
  }, [window.location.pathname]);

  // 模擬取得購物車資料 (實務中可改成 API 請求)
  useEffect(() => {
    if (!user) {
      setCart(null);
      return;
    }
    setLoading(true);
    // 假設 apiClient.get(`/api/cart/${user.customer_id}`) 取得購物車
    // 這裡先模擬
    setTimeout(() => {
      setCart({
        order_id: 1,
        customer_id: user.customer_id,
        customer_name: user.customer_name,
        status: true,
        total_amount: 500,
        comment: '需要折扣優惠',
        items: [
          {
            id: 1,
            license_id: 'LIC123',
            license_name: '產品A',
            quantity: 2,
            price_at_order_time: 100,
            created_by: user.customer_name,
            created_date: '2025-05-26',
          },
          {
            id: 2,
            license_id: 'LIC456',
            license_name: '產品B',
            quantity: 3,
            price_at_order_time: 100,
            created_by: user.customer_name,
            created_date: '2025-05-26',
          },
        ],
      });
      setLoading(false);
    }, 1000);
  }, [user]);

  const addToCart = (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return;

    setLoading(true);
    // 模擬加入購物車
    const newOrderItem: OrderItem = {
      id: Date.now(),
      license_id: newItem.license_id,
      license_name: newItem.license_name,
      quantity: newItem.quantity,
      price_at_order_time: newItem.price_at_order_time,
      created_by: newItem.created_by,
      created_date: new Date().toISOString().split('T')[0],
    };
    setCart((prev) => {
      if (!prev) {
        return {
          order_id: Date.now(),
          customer_id: user.customer_id,
          customer_name: user.customer_name,
          status: true,
          total_amount: newItem.price_at_order_time * newItem.quantity,
          comment: '',
          items: [newOrderItem],
        };
      }
      const updatedItems = [...prev.items, newOrderItem];
      const updatedTotal = updatedItems.reduce(
        (sum, i) => sum + i.price_at_order_time * i.quantity,
        0
      );
      return {
        ...prev,
        items: updatedItems,
        total_amount: updatedTotal,
      };
    });
    setNewItem({
      license_id: '',
      license_name: '',
      quantity: 1,
      price_at_order_time: 0,
      created_by: user.customer_name,
    });
    setLoading(false);
  };

  const removeItem = (id: number) => {
    if (!cart) return;
    setLoading(true);
    const filteredItems = cart.items.filter((item) => item.id !== id);
    const updatedTotal = filteredItems.reduce(
      (sum, i) => sum + i.price_at_order_time * i.quantity,
      0
    );
    setCart({
      ...cart,
      items: filteredItems,
      total_amount: updatedTotal,
    });
    setLoading(false);
  };

  const checkout = () => {
    if (!cart) return;
    setLoading(true);
    // 模擬結帳動作
    setTimeout(() => {
      setCart({ ...cart, status: false });
      setLoading(false);
      alert('結帳完成，感謝您的購買！');
    }, 1000);
  };

  if (!user && !loading) {
    return (
      <div className="container">
        <h1>購物車</h1>
        <div className="error">請先登入以使用購物車</div>
      </div>
    );
  }

  return (
    <div className="container">
      <h1>購物車</h1>

      {error && <div className="error">{error}</div>}
      {loading && <div className="loading">載入中...</div>}

      {user && (
        <div className="add-item">
          <h2>新增商品</h2>
          <form onSubmit={addToCart}>
            <div className="form-group">
              <label>許可證 ID</label>
              <input
                type="text"
                value={newItem.license_id}
                onChange={(e) => setNewItem({ ...newItem, license_id: e.target.value })}
                required
              />
            </div>
            <div className="form-group">
              <label>許可證名稱</label>
              <input
                type="text"
                value={newItem.license_name}
                onChange={(e) => setNewItem({ ...newItem, license_name: e.target.value })}
                required
              />
            </div>
            <div className="form-group">
              <label>數量</label>
              <input
                type="number"
                min={1}
                value={newItem.quantity}
                onChange={(e) =>
                  setNewItem({ ...newItem, quantity: parseInt(e.target.value) || 1 })
                }
                required
              />
            </div>
            <div className="form-group">
              <label>價格</label>
              <input
                type="number"
                min={0}
                value={newItem.price_at_order_time}
                onChange={(e) =>
                  setNewItem({ ...newItem, price_at_order_time: parseInt(e.target.value) || 0 })
                }
                required
              />
            </div>
            <button type="submit" disabled={loading}>
              新增到購物車
            </button>
          </form>
        </div>
      )}

      {cart ? (
        <div className="cart">
          <h2>購物車內容</h2>
          <p>
            客戶：{cart.customer_name} (ID: {cart.customer_id})
          </p>
          <p>總金額：${cart.total_amount}</p>
          <p>狀態：{cart.status ? '未結帳' : '已結帳'}</p>
          <p>備註：{cart.comment}</p>

          <table>
            <thead>
              <tr>
                <th>許可證名稱</th>
                <th>數量</th>
                <th>價格</th>
                <th>小計</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              {cart.items.map((item) => (
                <tr key={item.id}>
                  <td>{item.license_name}</td>
                  <td>{item.quantity}</td>
                  <td>${item.price_at_order_time}</td>
                  <td>${item.quantity * item.price_at_order_time}</td>
                  <td>
                    <button
                      onClick={() => removeItem(item.id)}
                      disabled={loading || !cart.status}
                      className="remove-btn"
                    >
                      移除
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {cart.status && (
            <button onClick={checkout} disabled={loading} className="checkout-btn">
              結帳
            </button>
          )}
        </div>
      ) : (
        !loading && <p>購物車為空</p>
      )}
    </div>
  );
};

export default CartComponent;
