import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Header from "./components/Header";
import Home from "./pages/Home";
import Login from "./pages/Login"; 
import Register from "./pages/Register";
import EmailVerify from "./pages/Email_verify"; 
import Cart from "./pages/Cart";
import ProductDetail from "./pages/ProductDetail";
// import ProductList from "./pages/Production";

const App = () => {
  return (
    <Router>
      <div className="min-h-screen bg-gray-100">
        <Header />
        <main className="max-w-7xl mx-auto px-4 sm:px-6 py-8">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/home" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/emailVerify" element={<EmailVerify />} />
            <Route path="/cart" element={<Cart />} />
            <Route path="/productDetail" element={<ProductDetail />} />
            {/* <Route path="/cart" element={<Cart />} /> */}
            {/* <Route path="/production" element={<ProductList />} /> */}
          </Routes>
        </main>
      </div>
    </Router>
  );
};

export default App;